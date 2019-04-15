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
import re 

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
local_path = '/Users/sarahchen/Downloads/digitaaal/' # path to photos in the docker image / local computer
server_path = '/home/plipdigital/wp-photos/'+paper_week+'/' # path to photos on the server
server_articles = '/home/plipdigital/temp_articles/' # path to articles on the server
ARTICLECAP = 100

# PATHPREFIX = server_path # PATH to folders # TODO: add this back
PATHPREFIX = '/Users/sarahchen/Documents/plip-upload/Digital/' # PATH to folders 
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage'}
# sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page'] # sections to upload
sections = ['Sports']
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
    cmd = 'scp -r '+local_path+' plipdigital@phillipian.net:'+server_path
    call(cmd, shell=True)
def copy_article_to_server(article_txt):
    cmd = 'scp "'+article_txt+'" plipdigital@phillipian.net:'+server_articles
    call(cmd, shell=True)
    return server_articles+article_txt.split('/')[-1]

def fetch_photos(sheet_url, compress_job):
    """fill dictionaries and compress images"""
    photo_df = fetch_sheet.get_google_sheet(sheet_url, 'Photo') # fetch image sheet
    if ('ImageDir' in photo_df.columns and 'Caption' in photo_df.columns and 'Photographer' in photo_df.columns and 'Section' in photo_df.columns):
        paths = photo_df['ImageDir'].values
        captions = photo_df['Caption'].values
        credits = photo_df['Photographer'].values
        sections = photo_df['Section'].values

        if (not (len(paths) == len(captions) and len(captions) == len(credits))):
            print('error: photo budget columns not the same length')
            exit(0)

       
        for i in range(len(paths)):
            if (captions[i] == '' or credits[i] == '' or sections[i] == ''):
                continue
            paths[i] = paths[i].strip()
             # fill in the dictionaries
            fetch_caption[paths[i]] = captions[i]
        
            credit = ''
            for special_case in special_photo_credits:
                if (special_case.lower() in credits[i].lower()): # if it's a special case, use raw credits[i]
                    credit = credits[i]
                    break
            if (credit == ''):
                credit = credits[i][0]+'.'+credits[i].split(' ')[1]+'/The Phillipian'

            fetch_credit[paths[i]] = credit

            # compress image
            if (compress_job and sections[i] == 'Sports'): # TODO: remove the sports thing
                full_path = local_path+sections[i].lower()+'/'+paths[i]
                imgs = os.listdir(full_path) 
                ind = 0
                while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                    ind += 1
                img = full_path+'/'+imgs[ind] 
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare

    else:
        print('error: missing col')

def fetch_illustrations(sheet_url, compress_job):
    illus_df = fetch_sheet.get_google_sheet(sheet_url, 'Illustrations') #fetch illustration sheet
    if ('ImageDir' in illus_df.columns and 'Illustrator' in illus_df.columns and 'Section' in illus_df.columns):
        paths = illus_df['ImageDir'].values
        credits = illus_df['Illustrator'].values
        sections = illus_df['Section'].values

        if(not(len(paths) == len(credits)) or not(len(paths) == len(sections))):
            print('error: illustration budget columns not the same length')
            exit(0)

        # fill dictionaries
        for i in range(len(paths)):
            if (paths[i] == ''):
                print('missing imagedir')
                continue
            if(credits[i] == ''):
                print('missing credit')
                continue
       
            credit = ''
            if (credit == ''):
                credit = credits[i][0] + '.' + credits[i].split(' ')[1]+'/The Phillipian'
            illus_credit[paths[i]] = credit

            # compress image
            if compress_job and sections[i] == 'Sports': # TODO: remove sports req
                full_path = local_path+sections[i].lower()+'/'+paths[i]
                imgs = os.listdir(full_path) 
                ind = 0
                while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                    ind += 1
                img = full_path+'/'+imgs[ind] 
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare
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
    
    
    try:
        cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@phillipian.net --ssh="+server_name+" --role='author' --display_name='"+writer+"' --porcelain"
        writer_id = check_output(cmd, shell=True)
    except:
        cmd = 'wp user get --ssh='+server_name+' --field=ID ' + writer_login
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

    return writer_id

# FETCH PHOTOS (and compress)
fetch_photos(sheet_url, False)
# FETCH ILLUSTRATIONS (and compress)
fetch_illustrations(sheet_url, False)
# COPY PHOTOS OVER TO SERVER
# copy_photos_to_server() # TODO: uncomment this

# FETCH ARTICLES
for s in sections:
    print('starting section: ' + s)
    # fetch and verify sheet dataframe content
    section_df = fetch_sheet.get_google_sheet(sheet_url, s) 
    helper.check_columns(section_df, ['Link','ImageDir','Headline','Writer','Featured?','Upload']) 

    article_urls = section_df['Link'].values
    headlines = section_df['Headline'].values
    img_names = section_df['ImageDir'].values
    writers = section_df['Writer'].values
    statuses = section_df['Upload'].values
    featured_posts = section_df['Featured?'].values

    if (not (len(article_urls) == len(img_names) and len(headlines) == len(img_names) and len(writers) == len(img_names) and len(statuses) == len(img_names))):
        print('error: '+s+' budget columns not the same length') # I don't think this ever happens but
    
    category_slug = category_slugs[s] # main category

    # loop through articles and upload them
    for i in range(min(ARTICLECAP,len(article_urls))):
        if (statuses[i].lower() != 'yes'):
            print('  skipped article: '+headlines[i])
            continue # only upload finished articles -- skip all that are not marked
        print(os.getcwd())
        # load and check fields
        article_url = article_urls[i]
        headline = headlines[i]
        img_name = img_names[i] # directory name
        writer = writers[i]
        featured = featured_posts[i]
        helper.check_content([article_url, headline, img_name, writer])

        print('Uploading: ' + headline + ' from ' + s) # progress string

        if (not 'docs.google.com/document/d/' in article_url):
            print('not a url, not uploading '+article_url)
            continue
        article_txt = fetch_document.get_google_doc(article_url) # fetch article text
        category_string = assign_categories(category_slug, article_txt, headline) # assign categories and subcategories
        writer_id = fetch_writer_id(writer) # fetch writer id number, or create user if writer does not exist
        
        # fetch image (only 1 supported)
        if (NOPHOTO not in img_name and img_name != ''):
            name = str(img_name)
            print('loading image '+name)
            local_img_dir = local_path + s.lower() + '/' + name # TODO: change this to work on the server
            imgs = os.listdir(local_img_dir) 
            ind = 0
            
            while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                ind += 1
            img = server_path+s.lower()+'/'+name+'/'+imgs[ind] 
            # img = imgprepare_python_2.compress_img(img, 30) # TODO: this should be deleted, compressing earlier now

            # upload the image to the media library
            cmd = 'wp media import '+img+' --ssh='+server_name+' --porcelain | xargs -I {} wp post list --post__in={} --field=url --ssh='+server_name+' --post_type=attachment'
            
            # cmd = 'wp media import '+img+' --ssh=automatic_upload@craig.dreamhost.com --porcelain | xargs -I {} wp post list --post__in={} --field=url --ssh=automatic_upload@craig.dreamhost.com --post_type=attachment'
            img_url = check_output(cmd, shell=True)
            img_url = helper.media_url_to_img_url(img_url,imgs[ind])

            # generate short code for image, prepend to article content
            inphoto = False
            if name in fetch_caption.keys() and name in fetch_credit.keys(): # check for valid photo
                inphoto = True
                caption = fetch_caption[name]
                credit = fetch_credit[name]
                if caption == '' or caption == None:
                    print('warning: missing caption on image for imagedir '+name)
                if credit == '' or credit == None:
                    print('warning: missing credit on image for imagedir '+name)
            if not inphoto and name not in illus_credit.keys(): 
                print('error: imageDir not found in photo or illustration budget for imagedir '+name)
                credit = fetch_credit[name]
                if credit == '' or credit == None:
                    print('warning: missing credit on image for imagedir '+name)
                exit(0)
            
            
            temp_shortcode = "<img src="+img_url.strip()+" />"
            # image_txt = imgprepare_python_2.img_for_post_content(img_url, caption, credit) 
            helper.prepend(article_txt, temp_shortcode) # TODO: put back!!!! (real in shortcodes image_txt only work on redesign)
            
        # fix headlines for each section
        if (category_slug == 'eighthpage'):
            headline = 'Phillipian Satire: ' + headline
        if (category_slug == 'commentary'):
            headline = 'Phillipian Commentary: ' + headline

        # if featured article, make timestamp yesterday and add to the featured category
        more_options = ''
        print(featured)
        if featured.lower() == 'yes':
            dt = datetime
            post_timestamp = (dt.datetime.now()-dt.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            more_options += "--post_date='"+post_timestamp+"'"
            category_string += ',featured'
        print(category_string)
        # POST WITH GIVEN PARAMETERS
        # cmd = "wp post create "+ workingdir +"/"+ article_txt + " --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        article_on_server = copy_article_to_server(article_txt)
        # cmd = "wp post create "+ article_on_server + " --ssh="+server_name+" --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        # cmd = "wp post create "+ article_on_server + " --ssh="+server_name+" --post_category="+ category_string +" --post_status=draft --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options  
        cmd = "wp post create "+ article_on_server + " --ssh="+server_name+" --post_category="+ category_string +" --post_status=draft --post_title='"+ re.sub("'","\'",headline) +"' --porcelain --post_author="+ writer_id
        print('calling '+ cmd)
        post_id = check_output(cmd, shell=True)

        print(post_id[:-1])

        cmd = 'wp post get ' + post_id[:-1] + ' --field=post_author --ssh='+server_name
        user_num = check_output(cmd, shell=True)[:-1]
        print(user_num)
        cmd = 'wp user get ' + user_num + ' --field=display_name --ssh='+server_name
        author_name = check_output(cmd, shell=True)[:-1]
        print(author_name)
        cmd = 'wp post meta update --ssh='+server_name +' ' + post_id[:-1] + ' cpa_author "' + author_name+'"'
        call(cmd, shell=True)

    

# writer_file = open('existing_users.txt','w')
# for writer in existing_writers:
#     writer_file.write(writer+'\n') # cut off the new line
