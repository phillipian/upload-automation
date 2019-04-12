"""
Automatically upload Phillipian articles
Run weekly from a newsroom computer within the docker image
On newsroom computer, -v with drobo folder (ex: '/Volumes/Phillipian/Phillipian/Spring 2019/4:12/digital')

"""
# TODO: support multiple author functionality
# TODO: support multiple photos
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
import custom_author

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

# CONSTANTS
local_path = '/pleasework2' # path to photos in the docker image
server_path = '/wp-photos/'+paper_week+'/'
ARTICLECAP = 2
workingdir = os.getcwd()

# PATHPREFIX = server_path # PATH to folders # TODO: add this back
PATHPREFIX = '/Users/sarahchen/Documents/plip-upload/Digital/' # PATH to folders 
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage'}
# sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page'] # sections to upload
sections = ['News']
server_name = 'plipdigital@phillipian.net/home/plipdigital/phillipian.net' # TODO: I'm not sure if this works

# VARS
all_post_ids = []
fetch_caption = {'':''} # map photo_dir to caption
fetch_credit = {'':''} # map photo_dir to credit
illus_credit = {'':''} # map illus_dir to credit
# existing_writers = [] # import from running list # TODO: get this from wp
# writer_file = open('existing_users.txt','r')
# for line in writer_file:
#     existing_writers.append(line[:-1]) # cut off the new line

def copy_photos_to_server():
    cmd = 'scp -r "'+local_path+' plipdigital@phillipian.net:'+server_path
    call(cmd, shell=True)

def fetch_photos(sheet_url):
    photo_df = fetch_sheet.get_google_sheet(sheet_url, 'Photo') # fetch image sheet
    if ('ImageDir' in photo_df.columns and 'Caption' in photo_df.columns and 'Photographer' in photo_df.columns):
        paths = photo_df['ImageDir'].values
        captions = photo_df['Caption'].values
        credits = photo_df['Photographer'].values
        if (not (len(paths) == len(captions) and len(captions) == len(credits))):
            print('error: photo budget columns not the same length')
            exit(0)

        # fill in the dictionaries
        for i in range(len(paths)):
            if (captions[i] == '' or credits[i] == ''):
                print('missing caption or credit')
                continue

            fetch_caption[paths[i]] = captions[i]
        
            credit = ''
            for special_case in special_photo_credits:
                if (special_case.lower() in credits[i].lower()): # if it's a special case, use raw credits[i]
                    credit = credits[i]
                    break
            if (credit == ''):
                print("c: " + credits[i])
                credit = credits[i][0]+'.'+credits[i].split(' ')[1]+'/The Phillipian'

            fetch_credit[paths[i]] = credit
        print(fetch_caption)
        print(fetch_credit)
    else:
        print('error: missing col')

def fetch_illustrations(sheet_url):
    illus_df = fetch_sheet.get_google_sheet(sheet_url, 'Illustrations') #fetch illustration sheet
    if('ImageDir' in illus_df.columns and 'Illustrator' in illus.df.columns):
        paths = illus_df['ImageDir'].values
        credits = illus_df['Illustrator'].values
        if(not(len(paths) == len(captions) and len(captions) == len(credits))):
            print('error: illustration budget columns not the same length')
            exit(0)

        # fill dictionaries
        for i in range(len(paths)):
            if(credits[i] == ''):
                print('missing credit')
                continue
       
            credit = ''
            if (credit == ''):
                print("c: credits[i])
                credit = credits[i][0] + '.' + credits[i].split(' ')[1]+'/The Phillipian'
            illus_credit[paths[i]] = credit
        print(illus_credit)
    else:
        print('error: missing col')

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
    
    try:
        cmd = 'wp user get --ssh='+server_name+' --field=ID ' + writer_login
        writer_id = check_output(cmd, shell=True)
    except:
        cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@phillipian.net --ssh="+server_name+" --display_name='"+writer+"' --porcelain"
        writer_id = check_output(cmd, shell=True)
    
    """
    if (writer_str in existing_writers): # TODO: can you acces it?
        cmd = 'wp user get --field=ID ' + writer_login
        # cmd = 'wp user get --ssh=automatic_upload@craig.dreamhost.com --field=ID ' + writer_login
    else:
        # cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@craig.dreamhost.com --ssh=automaticupload@craig.dreamhost.com --display_name='"+writer+"' --porcelain" 
        cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@craig.dreamhost.com --display_name='"+writer+"' --porcelain" 
        existing_writers.append(writer)
    """
    # writer_id = check_output(cmd, shell=True)
    os.chdir(workingdir)
    return writer_id


# COPY PHOTOS OVER TO SERVER
copy_photos_to_server()

# FETCH PHOTOS
fetch_photos(sheet_url)
print(fetch_caption)
# FETCH ILLUSTRATIONS
fetch_illustrations(sheet_url)
print(illus_credit)

# FETCH ARTICLES
for s in sections:
    print(s)
    # fetch and verify sheet dataframe content
    section_df = fetch_sheet.get_google_sheet(sheet_url, s) 
    helper.check_columns(section_df, ['Link','ImageDir','Headline','Writer','Featured?','Upload?']) 

    article_urls = section_df['Link'].values
    headlines = section_df['Headline'].values
    img_names = section_df['ImageDir'].values
    writers = section_df['Writer'].values
    statuses = section_df['Upload?'].values
    featured_posts = section_df['Featured?'].values

    if (not (len(article_urls) == len(img_names) and len(headlines) == len(img_names) and len(writers) == len(img_names) and len(statuses) == len(img_names))):
        print('error: '+s+' budget columns not the same length') # I don't think this ever happens but
        exit(0)
    
    category_slug = category_slugs[s] # main category

    # loop through articles and upload them
    for i in range(min(ARTICLECAP,len(article_urls))):

        if (statuses[i].lower() != 'yes'):
            print('  do not upload')
            continue # only upload finished articles -- skip all that are not marked
        
        # load and check fields
        article_url = article_urls[i]
        headline = headlines[i]
        img_name = img_names[i] # directory name
        writer = writers[i]
        featured = featured_posts[i]
        helper.check_content([article_url, headline, img_name, writer])

        print('Uploading: ' + headline + ' from ' + s) # progress string

        article_txt = fetch_document.get_google_doc(article_url) # fetch article text
        category_string = assign_categories(category_slug, article_txt, headline) # assign categories and subcategories
        writer_id = fetch_writer_id(writer) # fetch writer id number, or create user if writer does not exist
        
        # fetch image(s)
        # There can be multiple img_names in this field
        if (NOPHOTO not in img_name and img_name != ''):
            for name in img_name:
                img_dir = PATHPREFIX + s + '/' + name # TODO: change this to work on the server
                imgs = os.listdir(img_dir) 
                ind = 0
            
                while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                    ind += 1

                # fetch and compress image
                img = img_dir+'/'+imgs[ind] 
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare

                # upload the image to the media library
                os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
                cmd = 'wp media import '+img+' --ssh='+server_name+' --porcelain | xargs -I {} wp post list --post__in={} --field=url --ssh='+server_name+' --post_type=attachment'
                # cmd = 'wp media import '+img+' --ssh=automatic_upload@craig.dreamhost.com --porcelain | xargs -I {} wp post list --post__in={} --field=url --ssh=automatic_upload@craig.dreamhost.com --post_type=attachment'
                img_url = check_output(cmd, shell=True)
                img_url = helper.media_url_to_img_url(img_url,imgs[ind])
                os.chdir(workingdir)

                # generate short code for image, prepend to article content
                # TODO: catch error if name is not in keys
                if name not in fetch_caption.keys() or name not in fetch_credit.keys():
                    print('error: imageDir not found in photo budget')
                else if name not in illus_credit.keys():
                    print('error: imageDir not found in illustration budget')
                image_txt = imgprepare_python_2.img_for_post_content(img_url, fetch_caption[name], fetch_credit[name]) 
                helper.prepend(article_txt, image_txt)
               
        # fix headlines for each section
        if (category_slug == 'eighthpage'):
            headline = 'Phillipian Satire: ' + headline
        if (category_slug == 'commentary'):
            headline = 'Phillipian Commentary: ' + headline

        # if featured article, make timestamp yesterday and add to the featured category
        more_options = ''
        if featured == 'yes':
            dt = datetime
            post_timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            more_options += "--post_date='"+post_timestamp+"'"
            category_string += ',featured'

        # POST WITH GIVEN PARAMETERS
        # os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes") # cd to wordpress (test code only)
        # cmd = "wp post create "+ workingdir +"/"+ article_txt + " --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        cmd = "wp post create "+ workingdir +"/"+ article_txt + " --ssh="+server_name+" --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        post_id = check_output(cmd, shell=True)
        all_post_ids.append(post_id)

        os.chdir(workingdir)

custom_author.write_authors_from_list(all_post_ids)

# writer_file = open('existing_users.txt','w')
# for writer in existing_writers:
#     writer_file.write(writer+'\n') # cut off the new line
