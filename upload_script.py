
# TODO: support multiple author functionality
import os
from subprocess import call
from subprocess import check_output
import sys
import pandas as pd
import fetch_sheet
import fetch_document
import assign_subcategory
import helper
# import imgprepare # TODO: uncomment, change everything to imgprepare
import imgprepare_python_2
import argparse
import datetime

# CONSTANTS
PATHPREFIX = server_path # PATH to folders
NOPHOTO = 'xxnophotoxx'
special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage'}
sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page'] # sections to upload

existing_writers = [] # import from running list
writer_file = open('existing_users.txt','r')
for line in writer_file:
    existing_writers.append(line[:-1]) # cut off the new line

local_path = '/Volumes/Phillipian/Phillipian/Spring 2019/'+helper.replace_dash_w_colon(paper_week)+'/digital'
server_path = '/wp-photos/'+paper_week+'/'

def copy_photos_to_server():
    cmd = 'scp -r "'+local_path+'" auto_upload@craig.dreamhost.com:'+server_path+''
    call(cmd, shell=True)

def fetch_photos(sheet_url):
    photo_df = fetch_sheet.get_google_sheet(sheet_url, 'Photo') # fetch image sheet
    fetch_caption = {'':''} # map photo_dir to caption
    fetch_credit = {'':''} # map photo_dir to credit
    if ('Path' in photo_df.columns and 'Caption' in photo_df.columns and 'Photographer' in photo_df.columns):
        paths = photo_df['Path'].values
        captions = photo_df['Caption'].values
        credits = photo_df['Photographer'].values
        if (not (len(paths) == len(captions) and len(captions) == len(credits))):
            print('error: photo budget columns not the same length')
            exit(0)

        # fill in the dictionaries
        for i in range(min(len(paths), ARTICLECAP)):
            fetch_caption[paths[i]] = captions[i]
        
            credit = ''
            for special_case in special_photo_credits:
                if (special_case.lower() in credits[i].lower()): # if it's a special case, use raw credits[i]
                    credit = credits[i]
                    break
            if (credit == ''):
                credit = credits[i][0]+'.'+credits[i].split(' ')[1]+'/The Phillipian'

            fetch_credit[paths[i]] = credit

def assign_categories(cur_cat_str, article_txt, headline):
    """produce the category string"""
    cat_string = cur_cat_str

    src=open(article_txt,"r")
    content=src.readlines()
    src.close()
    if (cur_cat_str == 'sports'):
        cat_string += ','+assign_subcategory.find_sports_subcategories(headline, content)
    elif (cur_cat_str == 'arts'):
        if len(find_arts_subcategories(headline)) > 0:
            cat_string += ','+find_arts_subcategories(headline)
    return cat_string

def fetch_writer_id(writer_str):
    writer_login = helper.remove_spaces_commas(writer_str).lower()
    workingdir = os.getcwd()
    os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes") # TODO: fix
    if (writer_str in existing_writers): # TODO: can you acces it?
        cmd = 'wp user get --ssh=automatic_upload@craig.dreamhost.com --field=ID ' + writer_login
    else:
        cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@craig.dreamhost.com --ssh=automaticupload@craig.dreamhost.com --display_name='"+writer+"' --porcelain" 
        existing_writers.append(writer)
    writer_id = check_output(cmd, shell=True)
    os.chdir(workingdir)
    return writer_id


# PARSE COMMAND
parser = argparse.ArgumentParser(description='Upload articles from the budget spreadsheet.')
parser.add_argument('--url', metavar='URL', type=str, nargs='?',
                    help='url of the budget spreadsheet as it appears in the browser')
parser.add_argument('--date', metavar='DATE', type=str, nargs='?',
                    help='date for the paper as it appears in Drobo file directory, ex: 3-29')
args = parser.parse_args()
sheet_url = args.url
paper_week = args.date
if (sheet_url == None):
    print('Error: no sheet_url provided')
    exit(0)
if (paper_week == None):
    print('Error: no sheet_url provided')
    exit(0)

# COPY PHOTOS OVER TO SERVER
copy_photos_to_server()

# FETCH PHOTOS
fetch_photos(sheet_url)

# FETCH ARTICLES
for s in sections:
    section_df = fetch_sheet.get_google_sheet(sheet_url, s) # fetch sheet dataframe

    helper.check_columns(section_df, ['Link','ImageDir','Headline','Writer','Featured?','Upload?']) # confirm that required columns are present

    article_urls = section_df['Link'].values
    headlines = section_df['Headline'].values
    img_names = section_df['ImageDir'].values
    writers = section_df['Writer'].values
    statuses = section_df['Upload?'].values
    featured_posts = section_df['Featured?'].values

    if (not (len(article_urls) == len(img_names) and len(headlines) == len(img_names) and len(writers) == len(img_names) and len(statuses) == len(img_names))):
        print('error: '+s+' budget columns not the same length') # I don't think this ever happens but
        exit(0)

    # main category
    category_slug = category_slugs[s]

    # loop through articles and upload them
    for i in range(min(ARTICLECAP,len(article_urls))):
        # load and check fields
        status = statuses[i]

        if (status != 'yes'):
            continue # only upload finished articles -- skip all that are not marked

        article_url = article_urls[i]
        headline = headlines[i]
        img_name = img_names[i] # directory name
        writer = writers[i]
        featured = featured_posts[i]

        helper.check_content([article_url, headline, img_name, writer])

        # progress string
        print('Uploading: ' + headline + ' from ' + s) 

        # fetch article text
        article_txt = fetch_document.get_google_doc(article_url) 

        # assign categories and subcategories
        category_string = assign_categories(category_slug, article_txt, headline)

        # fetch writer id number, or create user if writer does not exist
        writer_id = fetch_writer_id(writer)
        
        # fetch image 
        num_imgs = 1
        if (len(img_name.split(' ')) > 1):
            print('multiple images! # = '+img_name.split(' ')[1])
            num_imgs = img_name.split(' ')[1]

        if (NOPHOTO not in img_name and img_name != ''):
            img_dir = PATHPREFIX + s + '/' + img_name
            imgs = os.listdir(img_dir) 
            ind = 0
            while (imgs[ind][0] == '.'): # skip hidden directories
                ind += 1

            for j in range(num_imgs):
                # the image to upload
                img = img_dir+'/'+imgs[ind+j] 
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare

                # upload the image to the media library
                os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
                cmd = 'wp media import '+img+' --ssh=automatic_upload@craig.dreamhost.com --porcelain | xargs -I {} wp post list --post__in={} --field=url --ssh=automatic_upload@craig.dreamhost.com --post_type=attachment'
                img_url = check_output(cmd, shell=True)
                img_url = helper.media_url_to_img_url(img_url,imgs[ind])
                os.chdir(workingdir)

                # generate short code for image, prepend to article content
                
                image_txt = imgprepare_python_2.img_for_post_content(img_url, fetch_caption[img_name], fetch_credit[img_name]) 

                helper.prepend(article_txt, image_txt)
        
        # fix headlines for each section
        if (category_slug == 'eighthpage'):
            headline = 'Phillipian Satire: ' + headline
        if (category_slug == 'commentary'):
            headline = 'Phillipian Commentary: ' + headline

        # if featured article, make timestamp yesterday and add to the featured category
        more_options = ''
        if featured == 'yes':
            post_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            more_options += "--post_date='"+post_timestamp+"'"
            category_string += ',featured'

        # make a post with the given parameters
        # cd to wordpress (test code only)
        os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
        # TODO: make status draft for the real site
        # TODO: check if category needs quotes around it
        cmd = "wp post create "+ workingdir +"/"+ article_txt + " --ssh=automaticupload@craig.dreamhost.com --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        post_id = check_output(cmd, shell=True)

        os.chdir(workingdir)

writer_file = open('existing_users.txt','w')
for writer in existing_writers:
    writer_file.write(writer+'\n') # cut off the new line