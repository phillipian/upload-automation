"""
fetch articles and article info
compress images and fetch image info
write all info to top of article text
scp article text files and image files to server
"""
# TODO: support multiple author functionality
# TODO: support multiple photos
import os
from subprocess import call
import fetch_sheet
import fetch_document
import assign_subcategory
import helper
import imgprepare_python_2 # TODO: change everything to imgprepare
import argparse
import datetime as dt

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
local_article_path = ''
server_article_path = '/home/plipdigital/temp_articles/' # path to articles on the server
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage'}
sections = ['News', 'Sports', 'Commentary', 'Arts', 'The Eighth Page'] # sections to upload

# IMG CONSTANTS
local_img_path = '' # TODO: fill this in; path to photos in the docker image / local computer
server_img_path = '/home/plipdigital/wp-photos/'+paper_week+'/' # path to photos on the server
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage'}

# GLOBAL VARS
photo_caption = {'':''} # map photo_dir to caption
photo_credit = {'':''} # map photo_dir to credit
illus_credit = {'':''} # map illus_dir to credit

# FUNCTIONS
def assign_categories(cur_cat_str, article_txt, headline):
    """produce the category string"""
    cat_string = cur_cat_str

    src=open(article_txt,"r")
    content=src.readlines()
    src.close()
    if (cur_cat_str == 'sports'):
        cat_string += ','+assign_subcategory.find_sports_subcategories(headline, content)
    elif (cur_cat_str == 'arts'):
        if len(assign_subcategory.find_arts_subcategories(headline)) > 0:
            cat_string += ','+ assign_subcategory.find_arts_subcategories(headline)
    return cat_string

def copy_photos_to_server():
    cmd = 'scp -r '+local_img_path+' plipdigital@phillipian.net:'+server_img_path
    call(cmd, shell=True)
def copy_article_to_server(article_txt):
    cmd = 'scp "'+article_txt+'" plipdigital@phillipian.net:'+server_article_path
    call(cmd, shell=True)
    return server_article_path+article_txt.split('/')[-1]
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
            photo_caption[paths[i]] = captions[i]
        
            credit = ''
            for special_case in special_photo_credits:
                if (special_case.lower() in credits[i].lower()): # if it's a special case, use raw credits[i]
                    credit = credits[i]
                    break
            if (credit == ''):
                credit = credits[i][0]+'.'+credits[i].split(' ')[1]+'/The Phillipian'

            photo_credit[paths[i]] = credit

            # compress image
            if (compress_job): 
                full_path = local_img_path+sections[i].lower()+'/'+paths[i]
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
            if compress_job: 
                full_path = local_img_path+sections[i].lower()+'/'+paths[i]
                imgs = os.listdir(full_path) 
                ind = 0
                while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                    ind += 1
                img = full_path+'/'+imgs[ind] 
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare
    else:
        print('error: missing col')

# fetch_photos(sheet_url, False)
# fetch_illustrations(sheet_url, False)
# COPY PHOTOS OVER TO SERVER
# copy_photos_to_server()

# FETCH ARTICLES
for s in sections:
    print('starting section: ' + s)
    # fetch and verify sheet dataframe content
    section_df = fetch_sheet.get_google_sheet(sheet_url, s) 
    helper.check_columns(section_df, ['Link','ImageDir','Headline','Writer','Featured?','Upload?']) 

    article_urls = section_df['Link'].values
    headlines = section_df['Headline'].values
    img_names = section_df['ImageDir'].values
    writers = section_df['Writer'].values
    statuses = section_df['Upload?'].values
    featured_posts = section_df['Featured?'].values

    category_slug = category_slugs[s] # main category

    # upload articles
    for i in range(len(article_urls)):
        if (statuses[i].lower() != 'yes'): # only upload finished articles -- skip all that are not marked
            print('  skipping article: '+headlines[i])
            continue 

        # PROCESS ARTICLE TEXT
        article_doc_url = article_urls[i]
        headline = headlines[i]
        writer = writers[i]
        featured = featured_posts[i]
        helper.check_content([article_doc_url, headline, writer])

        print('Uploading: ' + headline + ' from ' + s) # progress string
        if (not 'docs.google.com/document/d/' in article_doc_url): # verify url
            print('  Error: not a url, now skipping '+article_doc_url)
            continue

        article_txt = fetch_document.get_google_doc(article_doc_url) # fetch article text file
        category_string = assign_categories(category_slug, article_txt, headline) # assign categories and subcategories
        
        # fix headlines for each section
        if (category_slug == 'eighthpage'):
            headline = 'Phillipian Satire: ' + headline
        if (category_slug == 'commentary'):
            headline = 'Phillipian Commentary: ' + headline

        # if featured article, make timestamp yesterday and add to the featured category
        more_options = ''
        if featured.lower() == 'yes':
            post_timestamp = (dt.datetime.now()-dt.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            more_options += "--post_date='"+post_timestamp+"'"
            category_string += ',featured'

        # PROCESS ARTICLE IMAGES
        img_name = img_names[i] # directory name from budget
        if (NOPHOTO not in img_name and img_name != ''):
            # fetch image (only 1 supported)
            name = str(img_name)
            imgs = os.listdir(local_img_path + s.lower() + '/' + name) # find imgs in the directory
            ind = 0
            while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                ind += 1
            img = server_img_path+s.lower()+'/'+name+'/'+imgs[ind] # path to img on server

            # generate short code for image, prepend to article content
            inphoto = False
            if name in photo_caption.keys() and name in photo_credit.keys(): # check for valid photo
                inphoto = True
                caption = photo_caption[name]
                credit = photo_credit[name]
                if caption == '' or caption == None:
                    print('warning: missing caption on image for imagedir '+name)
                if credit == '' or credit == None:
                    print('warning: missing credit on image for imagedir '+name)
            if not inphoto and name not in illus_credit.keys(): 
                print('error: imageDir not found in photo or illustration budget for imagedir '+name)
                credit = photo_credit[name]
                if credit == '' or credit == None:
                    print('warning: missing credit on image for imagedir '+name)
                exit(0)
                helper.prepend(article_txt, 'caption: ' + caption)
                helper.prepend(article_txt, 'credit: ' + credit)
            # TODO: whatever else is needed
            # TODO: prepend all photo info to article text file
            helper.prepend(article_txt, 'path to img:\t'+img)
        else:
            helper.prepend(article_txt, 'path to img:\t'+NOPHOTO)

        # prepend info to article text file
        helper.prepend(article_txt, 'headline:\t'+headline)
        helper.prepend(article_txt, 'writer:\t'+writer)
        helper.prepend(article_txt, 'categories:\t'+category_string)
        helper.prepend(article_txt, 'more options:\t'+more_options)
        print(article_txt)
        # copy article to server
        article_txt_on_server = copy_article_to_server(article_txt)
        print('article file: '+article_txt)
        break
    break
            
        
    
