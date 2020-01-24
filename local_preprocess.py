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
import json
import imgprepare_python_2 # TODO: change everything to imgprepare
import argparse
import datetime as dt
import re
import unidecode
import pdb

# PARSE COMMAND
parser = argparse.ArgumentParser(description='Upload articles from the budget spreadsheet.')
parser.add_argument('--url', metavar='URL', type=str, nargs='?',
                    help='url of the budget spreadsheet as it appears in the browser')
parser.add_argument('--date', metavar='DATE', type=str, nargs='?',
                    help='date for the paper as it appears in Drobo file directory, ex: 3-29')
parser.add_argument('--sections', metavar='SECT', type=str, default='arts, commentary, editorial, news, sports, multilingual', help='Comma seperated list of sections to upload')
args = parser.parse_args()
sheet_url = args.url
paper_week = args.date

ALL_SECTIONS = ['News', 'Sports', 'Commentary', 'Arts', 'Editorial', 'Multilingual'] # list of valid sections # TODO: 8th pg
sections = args.sections.split(',')
sections = [i.strip().lower().capitalize() for i in sections] #ensure section strings are all lowercase and wwhitespace-stripped

for section in sections: #verify that all section strings are legit
    assert section in ALL_SECTIONS, "Error: section string {} doesn't seem to be supported — might want to check your spelling".format(section)

assert sheet_url != None, 'Error: no sheet_url provided'
assert paper_week != None, 'Error: no sheet_url provided'

# CONSTANTS
local_article_path = 'articles/'
server_article_path = '/home/plipdigital/temp_articles/' # path to articles on the server
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage', 'Multilingual':'multilingual', 'Editorial':'editorial'}

# IMG CONSTANTS
local_img_path = '/Users/jzpan/digital/' # TODO: fill this in; path to photos in the docker image / local computer
server_img_path = '/home/plipdigital/wp-photos/'+paper_week+'/' # path to photos on the server
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']

# GLOBAL VARS
photo_caption = {'':''} # map photo_dir to caption
photo_credit = {'':''} # map photo_dir to credit
illus_credit = {'':''} # map illus_dir to credit

# FUNCTIONS
def assign_categories(cur_cat_str, category, headline):
    """produce the category string"""
    cat_string = cur_cat_str
    '''
    src=open(article_txt,"r")
    content=src.readlines()
    src.close()
    '''
    if (cur_cat_str == 'sports'):
        cat_string += ','+assign_subcategory.find_sports_subcategories(headline, category)
    elif (cur_cat_str == 'arts'):
        if len(assign_subcategory.find_arts_subcategories(headline)) > 0:
            cat_string += ','+ assign_subcategory.find_arts_subcategories(headline)
    return cat_string

def copy_photos_to_server():
    cmd = 'scp -r '+local_img_path+' plipdigital@phillipian.net:'+server_img_path
    call(cmd, shell=True)
def copy_article_to_server(article_txt):
    cmd = 'scp -r "'+article_txt+'" plipdigital@phillipian.net:'+server_article_path
    call(cmd, shell=True)
    return server_article_path+article_txt.split('/')[-1]
def fetch_photos(sheet_url):
    """fill dictionaries and compress images"""
    photo_df = fetch_sheet.get_google_sheet(sheet_url, 'Photo') # fetch image sheet
    if ('ImageDir' in photo_df.columns and 'Photographer' in photo_df.columns and 'Section' in photo_df.columns):
        paths = photo_df['ImageDir'].values
        captions = photo_df['Context/Caption'].values
        credits = photo_df['Photographer'].values
        sections_col = photo_df['Section'].values

        assert len(paths) == len(captions), 'error: photo budget columns not the same length'
        assert len(captions) == len(credits), 'error: photo budget columns not the same length'

        for i in range(len(paths)):
            if (paths[i].lower() == 'nophoto' or paths[i] == '' or sections_col[i] == '' or sections_col[i] not in [s.lower() for s in sections]): # skip empty fields
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
                credit = credits[i]+'/The Phillipian'

            photo_credit[paths[i]] = credit

            # compress image
            full_path = os.path.join(local_img_path+sections_col[i].lower(), paths[i].lower())
            imgs = os.listdir(full_path)

            for img in imgs:
                if img[0] == '.': # skip hidden directories ('.anything')
                    continue 
                if (img.split('_')[0] != 'Compressed'): # compress if not already compressed
                    print('compressing '+full_path)
                    img = os.path.join(full_path, img)
                    img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare
    else:
        print('error: missing col')

def fetch_graphics(sheet_url):
    graphics_df = fetch_sheet.get_google_sheet(sheet_url, 'Graphic') #fetch illustration sheet
    if ('ImageDir' in graphics_df.columns and 'Designer' in graphics_df.columns and 'Section' in graphics_df.columns):
        paths = graphics_df['ImageDir'].values
        credits = graphics_df['Designer'].values
        sections = graphics_df['Section'].values
        do_upload = graphics_df['Upload?'].values

        assert len(paths) == len(credits), 'error: graphic budget columns not the same length'
        assert len(paths) == len(sections), 'error: graphic budget columns not the same length'

        # fill dictionaries
        for i in range(len(paths)):
            if (paths[i] == ''):
                print('missing imagedir')
                continue
            if(credits[i] == ''):
                print('missing credit')
                continue
            if paths[i] == NOPHOTO:
                print('no photo')
                continue
            

            credit = ''
            if (credit == ''):
                credit = credits[i]+'/The Phillipian'
            graphics_credit[paths[i]] = credit
            # compress image
            full_path = local_img_path+sections[i].lower()+'/'+paths[i]
            imgs = os.listdir(full_path)
            ind = 0
            while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                ind += 1
            if imgs[ind][0] != '0':
                print('compressing '+full_path)
                img = full_path+'/'+imgs[ind]
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare
    else:
        print('error: missing col')
        print(graphics_df.columns)
    
def fetch_illustrations(sheet_url):
    illus_df = fetch_sheet.get_google_sheet(sheet_url, 'Illustrations!') #fetch illustration sheet
    if ('ImageDir' in illus_df.columns and 'Illustrator' in illus_df.columns and 'Section' in illus_df.columns):
        paths = illus_df['ImageDir'].values
        credits = illus_df['Illustrator'].values
        sections = illus_df['Section'].values

        assert len(paths) == len(credits), 'error: illustration budget columns not the same length'
        assert len(paths) == len(sections), 'error: illustration budget columns not the same length'

        # fill dictionaries
        for i in range(len(paths)):
            if (paths[i] == ''):
                print('missing imagedir')
                continue
            if(credits[i] == ''):
                print('missing credit')
                continue
            if paths[i] == NOPHOTO:
                print('no photo')
                continue

            credit = ''
            if (credit == ''):
                credit = credits[i]+'/The Phillipian'
            illus_credit[paths[i]] = credit
            # compress image
            full_path = local_img_path+sections[i].lower()+'/'+paths[i]
            imgs = os.listdir(full_path)
            ind = 0
            while (imgs[ind][0] == '.'): # skip hidden directories ('.anything')
                ind += 1
            if imgs[ind][0] != '0':
                print('compressing '+full_path)
                img = full_path+'/'+imgs[ind]
                img = imgprepare_python_2.compress_img(img, 30) # TODO: use imgprepare
    else:
        print('error: missing col')
        print(illus_df.columns)


fetch_photos(sheet_url)
#fetch_illustrations(sheet_url)
#fetch_graphics(sheet_url)
# COPY PHOTOS OVER TO SERVER
#copy_photos_to_server() # TODO: uncomment after done testing

# FETCH ARTICLES
for s in sections:
    print('starting section:\t' + s)
    # fetch and verify sheet dataframe content
    section_df = fetch_sheet.get_google_sheet(sheet_url, s)
    languages = None
    img_names = None
    translators = None
    featured_posts = None
    if s == 'multilingual':
        helper.check_columns(section_df, ['Link','Translator','Translated Headline','Writer','Language','Upload'])
        headlines = section_df['Translated Headline'].values
        translators = section_df['Translator'].values
        languages = section_df['Language'].values
    if s == 'sports':
        helper.check_columns(section_df, ['Subcategory'])
        categories = section_df['Subcategory'].values
        
    else:
        helper.check_columns(section_df, ['Link','ImageDir','Headline','Writer','Featured','ready for autoupload', 'uploaded online', 'TAGS'])
        headlines = section_df['Headline'].values
        img_names = section_df['ImageDir'].values
        featured_posts = section_df['Featured'].values
    
    tags = section_df['TAGS'].values
    article_urls = section_df['Link'].values
    writers = section_df['Writer'].values
    statuses = section_df['ready for autoupload'].values
    is_uploaded = section_df['uploaded online'].values

    category_slug = category_slugs[s] # main category

    # upload articles
    for i in range(len(article_urls)):
        if (statuses[i].rstrip().lower() != 'yes' or is_uploaded[i].rstrip().lower() == 'x'): # only upload finished articles that aren't already uploaded-- skip all that are not marked
            print('skipping:\t'+headlines[i])
            continue

        # PROCESS ARTICLE TEXT

        article_doc_url = article_urls[i].rstrip()
        headline = headlines[i].rstrip()
        writer = writers[i].rstrip()

        # Deal with multiple authors
        if '&' in writer:
            writer_list = writer.split('&')
            writer_list = [i.strip() for i in writer_list]
        elif ' and ' in writer:
            writer_list = writer.split(' and ')
            writer_list = [i.strip() for i in writer_list]
        else:
            writer_list = [writer]
        if s == 'multilingual':
            writer_list.append(translators[i].rstrip())
            featured = ''
        else:
            featured = featured_posts[i].rstrip()
        helper.check_content([article_doc_url, headline, writer])

        print('Processing:\t' + headline + ' from ' + s) # progress string
        if (not 'docs.google.com/document/d/' in article_doc_url): # verify url
            print('  Error: not a url, now skipping '+article_doc_url)
            continue

        article_txt = fetch_document.get_google_doc(article_doc_url, local_article_path) # fetch article text file
        if s == 'multilingual':
            category_string = category_slug + ',' + "'" + languages[i].rstrip() + "'"
        elif s == 'sports':
            category_string = assign_categories(category_slug, categories[i], headline) # assign categories and subcategories
        else:
            category_string = category_slug
        article_info = {}
        with open(article_txt, 'r') as f:
            article_info = json.load(f)
        # fix headlines for each section
        if (category_slug == 'eighthpage'):
            headline = 'Phillipian Satire: ' + headline
        if (category_slug == 'commentary'):
            headline = 'Phillipian Commentary: ' + headline

        # if featured article, make timestamp yesterday and add to the featured category
        more_options = ''
        if featured.lower() == 'yes':
            post_timestamp = (dt.datetime.now()+dt.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
            more_options += "--post_date='"+post_timestamp+"'"
            category_string += ',featured'

        article_image_dir = img_names[i].rstrip()

        if NOPHOTO in article_image_dir or article_image_dir == '':
            article_info['img_paths'] = [NOPHOTO]
        else:

            name = str(article_image_dir)
            imgs = os.listdir(os.path.join(local_img_path, s.lower(), name)) # find imgs in the directory

            image_path_list = []
            caption_list = []
            credit_list = []


            for img in imgs:
                if img[0] == '.': # skip hidden directories ('.anything')
                    continue
                if img.split('_')[0] != 'Compressed': # compress if not already compressed
                    continue
                image_path_list.append(os.path.join(server_img_path, s.lower(), name, img)) # path to img on server

                # generate a unique photo path to find the photo's metadata from the photo budget
                #short_path = os.path.join(name, img)

                # generate short code for images, prepend to article content
                inphoto = False
                if name in photo_caption.keys() and name in photo_credit.keys(): # check for valid photo
                    inphoto = True
                    caption_list.append(photo_caption[name])
                    credit_list.append(photo_credit[name])
                    if photo_caption[name] == '' or photo_caption[name] == None:
                        print('  warning: missing caption on image for imagedir '+name)
                    if photo_credit[name] == '' or photo_credit[name] == None:
                        print('  warning: missing credit on image for imagedir '+name)

                if name in illus_credit.keys():

                    caption_list.append('')
                    credit_list.append(illus_credit[name])
                    if illus_credit[name] == '' or illus_credit[name] == None:
                        print('  warning: missing credit on illustration for imagedir '+name)

                if not inphoto and name not in illus_credit.keys():
                    print('  error: imageDir not found in photo or illustration budget for imagedir '+name)
                    exit(0)

            article_info['caption'] = caption_list
            article_info['credit'] = credit_list
            article_info['img_paths'] = image_path_list

        #fix all the strings before writing to json

        # prepend info to article text file
        article_info['tags'] = tags[i].strip()
        article_info['headline'] = headline.strip() 
        article_info['writer'] = writer_list
        article_info['categories'] = category_string.strip() 
        article_info['more_options'] = more_options.strip() 
        #article_info['article_txt'] = article

        with open(article_txt, 'w') as f:
            json.dump(article_info, f)

copy_article_to_server(local_article_path)
