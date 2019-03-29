# TODO: fix multiple authors
import os
from subprocess import call
from subprocess import check_output
import sys
import pandas as pd
import fetch_sheet
import fetch_document
import assign_subcategory
# import imgprepare # TODO: uncomment
import imgprepare_python_2
import argparse
import datetime

def remove_spaces_commas(s_in):
    """Remove spaces and commas from a string"""
    s_out = ''
    for i in range(len(s_in)):
        if (s_in[i] != ',' and s_in[i] != ' '):
            s_out += s_in[i]
    return s_out
def media_url_to_img_url(murl, filename):

    murl_elements = murl.split('/')

    if ('' == murl_elements[-1] or '\n' == murl_elements[-1]):
        del murl_elements[-1]
    
    print(murl_elements)
    
    cur_month = str(datetime.datetime.now().month)
    if (len(cur_month) < 2):
        cur_month = '0'+cur_month
    iurl = '/'.join(murl_elements[:-1])+'/wp-content/uploads/'+str(datetime.datetime.now().year)+'/'+str(cur_month)+'/'+filename
    return iurl

# TODO: get the real path from newsroom computer, THIS IS A PLACEHOLDER

PATHPREFIX = os.getcwd()+'/../Digital/' # PATH to folders
NOPHOTO = 'xxnophotoxx'
ARTICLECAP = 3 # TODO: remove after finished (for testing purposes)

special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage'}
sections = ['News'] # sections to upload
# sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page']

existing_writers = [] # import from running list
writer_file = open('existing_users.txt','r')
for line in writer_file:
    existing_writers.append(line[:-1]) # cut off the new line

parser = argparse.ArgumentParser(description='Upload articles from the budget spreadsheet.')
parser.add_argument('--url', metavar='URL', type=str, nargs='?',
                    help='url of the budget spreadsheet as it appears in the browser')
args = parser.parse_args()
sheet_url = args.url
if (sheet_url == None):
    print('Error: no sheet_url provided')
    exit(0)

# fetch image sheet to get caption and credit for photo ids
photo_df = fetch_sheet.get_google_sheet(sheet_url, 'Photo')
# dictionary for photo_dir to caption, to credit
fetch_caption = {'':''}
fetch_credit = {'':''}
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


# fetch sheet dataframe
for s in sections:
    section_df = fetch_sheet.get_google_sheet(sheet_url, s)

    if (not ('Link' in section_df.columns and \
        'ImageDir' in section_df.columns and \
        'Headline' in section_df.columns and \
        'Writer' in section_df.columns and \
        'Featured?' in section_df.columns and \
        'Upload?' in section_df.columns)):
        print('error: missing budget columns')
        exit(0)

    article_urls = section_df['Link'].values
    headlines = section_df['Headline'].values
    img_names = section_df['ImageDir'].values
    writers = section_df['Writer'].values
    statuses = section_df['Upload?'].values
    featured_posts = section_df['Featured?'].values

    if (not (len(article_urls) == len(img_names) and len(headlines) == len(img_names) and len(writers) == len(img_names) and len(statuses) == len(img_names))):
        print('error: '+s+' budget columns not the same length')
        exit(0)

    # the highest category for each
    category_slug = category_slugs[s]

    # loop through articles and upload them
    for i in range(min(ARTICLECAP,len(article_urls))):
        article_url = article_urls[i]
        headline = headlines[i]
        img_name = img_names[i] # directory name
        writer = writers[i]
        status = statuses[i]
        featured = featured_posts[i]

        if (article_url == ''):
            print('error: no article url')
        if (headline == ''):
            print('error: no headline')
        if (img_name == ''):
            print('error: no image name')
        if (writer == ''):
            print('error: no writer')
        if (status == ''):
            print('error: no status')

        

        # only upload done articles, skip unless marked
        if (status != 'yes'):
            continue

        # fetch article text
        article_txt = fetch_document.get_google_doc(article_url) 

        # get writer id number, or create user if it does not exist
        writer_login = remove_spaces_commas(writer).lower()
        workingdir = os.getcwd()
        os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
        if (writer in existing_writers):
            cmd = 'wp user get --field=ID ' + writer_login
        else:
            cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@phillipian.net --display_name='"+writer+"' --porcelain" 
            existing_writers.append(writer)
        writer_id = check_output(cmd, shell=True)
        os.chdir(workingdir)
        
        # fetch image 
        if (img_name != NOPHOTO and img_name != ''):
            img_dir = PATHPREFIX + s + '/' + img_name
            imgs = os.listdir(img_dir) 
            print(img_dir)
            print('img')
            ind = 0
            while (imgs[ind][0] == '.'):
                ind += 1
            img = img_dir+'/'+imgs[ind] # the image to upload -- ONLY THE 1ST IMAGE IN THE DIRECTORY IS POSTED (there should only be 1)
            # imgprepare.compress_img(img) # compress the image # TODO: uncomment
            print(img)
            img = imgprepare_python_2.compress_img(img, 30) 

            os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
            cmd = 'wp media import '+img+' --porcelain | xargs -I {} wp post list --post__in={} --field=url --post_type=attachment'
            img_url = check_output(cmd, shell=True)
            img_url = media_url_to_img_url(img_url,imgs[ind])
            print(img_url)
            os.chdir(workingdir)

            # generate short code for image to prependto article content
            img_caption = fetch_caption[img_name]
            img_credit = fetch_credit[img_name]
            # image_txt = imgprepare.img_for_post_content(img_url, img_caption, img_credit) # TODO: uncomment
            image_txt = imgprepare_python_2.img_for_post_content(img_url, img_caption, img_credit) 

            src=open(article_txt,"r")
            content=src.readlines()
            content.insert(0,image_txt+'\n') # prepend the string we want to on first line
            src.close()
                
            src=open(article_txt,"w")
            src.writelines(content)
            src.close()
        
        # assign categories
        category_string = category_slug
        src=open(article_txt,"r")
        content=src.readlines()
        src.close()
        if (category_string == 'sports'):
            category_string += ','+assign_subcategory.find_sports_subcategories(headline, content)
        elif (category_string == 'arts'):
            category_string += ','+find_arts_subcategories(headline)

        print(category_string)

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

        
        # cd to wordpress (test code only)
        os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")

        # make a post with the given parameters
        # TODO: make status draft for the real site
        # TODO: check if category needs quotes around it
        cmd = "wp post create "+ workingdir +"/"+ article_txt + " --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        post_id = check_output(cmd, shell=True)

        os.chdir(workingdir)


writer_file = open('existing_users.txt','w')
for writer in existing_writers:
    writer_file.write(writer+'\n') # cut off the new line