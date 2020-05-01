"""
!
fetch articles and article info
compress images and fetch image info
write all info to top of article text
scp article text files and image files to server
"""
# TODO: support multiple photos!
import os
from subprocess import call
import json
import argparse
import datetime as dt
import re
import unidecode
import sys

import fetch_sheet
import fetch_document
import assign_subcategory

sys.path.insert(1, '../')
import helper
from config import * # TODO: test the config file import

# GLOBAL VARS
photo_caption = {'':''} # map photo_dir to caption
photo_credit = {'':''} # map photo_dir to credit
illus_credit = {'':''} # map illus_dir to credit
ALL_SECTIONS = ['News', 'Sports', 'Commentary', 'Arts', 'Editorial', 'Multilingual'] # sections supported by automation # TODO: add 8th pg

# FUNCTIONS
def process_args():
    """process command line args"""
    parser = argparse.ArgumentParser(description='Upload articles from the budget spreadsheet.')
    parser.add_argument(
        '--url', 
        metavar='URL', 
        type=str, 
        nargs='?',
        help='url of the budget spreadsheet, as it appears in the browser'
    )
    parser.add_argument(
        '--date', 
        metavar='DATE', 
        type=str, 
        nargs='?',
        help='date for the paper as it appears in Drobo file directory, ex: 3-29'
    )
    parser.add_argument(
        '--sections', 
        metavar='SECT', 
        type=str, 
        default='arts, commentary, editorial, news, sports, multilingual', 
        help='Comma separated list of sections to upload'
    )
    args = parser.parse_args()
    return args

def setup_directories():
    for section in ALL_SECTIONS:
        if not os.path.isdir(os.path.join(local_article_path, section)):
            os.mkdir(os.path.join(local_article_path, section))

def assign_categories(section_str, category, headline):
    """produce the category string for an article, given its section and headline"""
    cat_string = section_str

    if (section_str == 'sports'):
        cat_string += ','+assign_subcategory.find_sports_subcategories(headline, category)
    elif (section_str == 'arts'):
        if len(assign_subcategory.find_arts_subcategories(headline)) > 0:
            cat_string += ','+ assign_subcategory.find_arts_subcategories(headline)
    elif (section_str == 'news'):
        if len(assign_subcategory.find_news_subcategories(headline)) > 0:
            cat_string += ','+ assign_subcategory.find_news_subcategories(headline)
    return cat_string

def copy_photos_to_server():
    cmd = 'scp -r '+local_img_path+' plipdigital@phillipian.net:'+server_img_path
    call(cmd, shell=True)
def copy_article_to_server(article_dir):
    cmd = 'scp -r "'+article_dir+'" plipdigital@phillipian.net:'+server_article_homedir
    call(cmd, shell=True)
    return server_article_homedir+article_dir.split('/')[-1]

def fetch_photos(sheet_url):
    """from photo budget, fill global dictionaries (photo_caption, photo_credit) and compress images in imagedirs"""
    
    # fetch photo sheet from the budget
    photo_df = fetch_sheet.get_google_sheet(sheet_url, 'Photo') 
    # check if all columns are present
    assert ('ImageDir' in photo_df.columns), 'error: missing ImageDir column in photo budget'
    assert ('Online Caption' in photo_df.columns), 'error: missing Context/Caption column in photo budget'
    assert ('Photographer' in photo_df.columns), 'error: missing Photographer column in photo budget'
    assert ('Section' in photo_df.columns), 'error: missing Section column in photo budget'

    def process_photo_budget_row(row):
        path = row['ImageDir'].strip().lower()
        caption = row['Online Caption']
        credit = row['Photographer']
        section = row['Section'].lower()
    
        # skip empty dirs and invalid sections
        if (path == NOPHOTO or path == '' or section == '' or section not in [s.lower() for s in sections]): 
            return

        # map imgdir to caption 
        photo_caption[path] = caption

        # map imgdir to credit
        # if a special case, use credit w/o any processing
        for special_case in special_photo_credits:
            if (special_case.lower() in credit.lower()): 
                photo_credit[path] = credit
                break
        # if not a special case, append '/The Phillipian'
        if not path in photo_credit.keys():
            photo_credit[path] = credit+'/The Phillipian'

        # compress image
        full_path = os.path.join(local_img_path+section, path)
        try:
            imgs = os.listdir(full_path)
        except FileNotFoundError:
            print('Warning: Directory {} does not exist'.format(full_path))
            return
        for img in imgs:
            if img[0] == '.': # skip hidden directories ('.anything')
                continue 
            if (img.split('_')[0] != 'Compressed'): # compress if not already compressed
                print('compressing '+full_path)
                img = os.path.join(full_path, img)
                img = helper.compress_img(img, 70)

        # remove all non compressed images
        # TODO: test this out
        imgs = os.listdir(full_path)
        for img in imgs:
            if img[0] == '.': # skip hidden directories ('.anything')
                continue 
            if (img.split('_')[0] != 'Compressed'): # delete if not compressed
                os.remove(os.path.join(full_path, img))
    
    # fetch column info
    photo_df.apply(process_photo_budget_row, axis=1)


# MAIN
# parse commands
args = process_args()
sheet_url = args.url
paper_week = args.date
sections = [x.strip().lower().capitalize() for x in args.sections.split(',')] # obtain lowercase and whitespace-stripped section strings 

# validate passed args
for section in sections: # verify that all section strings are legit
    assert section in ALL_SECTIONS, 'Error: section string {} is not supported - might want to check your spelling'.format(section)
assert sheet_url != None, 'Error: no sheet_url provided'
assert paper_week != None, 'Error: no sheet_url provided'

# set server img path to the week's paper
server_img_path = os.path.join(server_img_path, paper_week)

#ensure that articles directory is correctly set up
setup_directories()

# fetch photos
fetch_photos(sheet_url)
# copy photos to server
copy_photos_to_server() 

# upload articles for each section
# copy articles to server

def process_section(s):
    """process articles for section s"""
    # fetch and verify dataframe content for each section
    section_df = fetch_sheet.get_google_sheet(sheet_url, s)

    if s == 'multilingual':
        helper.check_columns(section_df, ['Link','Translator','Translated Headline','Writer','Language','Upload'])
    elif s == 'sports':
        helper.check_columns(section_df, ['Subcategory'])
    else:
        helper.check_columns(section_df, ['Link','ImageDir','Headline','Writer','Featured','ready for autoupload', 'uploaded online', 'TAGS'])
        
    return section_df

def process_article_imgs(article_image_dir):
    """obtain image info for json output"""

    def process_single_img(img):
        # path to img on server
        image_path = os.path.join(server_img_path, 'digital', s.lower(), name, img) 

        # generate short code for images, prepend to article content
        if name in photo_caption.keys() and name in photo_credit.keys(): # check for valid photo
            caption = (photo_caption[name])
            credit = (photo_credit[name])
            if photo_caption[name] == '' or photo_caption[name] == None:
                print('  error: missing caption on image for imagedir '+name)
                exit(0)
            if photo_credit[name] == '' or photo_credit[name] == None:
                print('  error: missing credit on image for imagedir '+name)
                exit(0)
        return image_path, caption, credit   


    # if article has no photo specified
    if NOPHOTO in article_image_dir or article_image_dir == '':
        return [None, None, NOPHOTO]
    
    name = str(article_image_dir)
    imgs = os.listdir(os.path.join(local_img_path, s.lower(), name)) # find imgs in the 'article_image_dir' directory
    imgs = [x for x in imgs if x[0] != '.'] # skip files beginning w '.'
    image_path_list = []
    caption_list = []
    credit_list = []

    for img in imgs:
        if img.split('_')[0] != 'Compressed': # skip non-compressed images (photos should already have been processed)
            continue
        image_path, caption, credit = process_single_img(img)
        image_path_list.append(image_path)
        caption_list.append(caption)
        credit_list.append(credit)
        
    return caption_list, credit_list, image_path_list

def process_section_df_row(row, s):
    """apply this function to all rows of a section df"""
    
    def writer_to_writer_list(writer):
        # convert writer string to list of writers (multiple author support)
        if '&' in writer:
            writer_list = writer.split('&')
            writer_list = [x.strip() for x in writer_list]
        elif ' and ' in writer:
            writer_list = writer.split(' and ')
            writer_list = [x.strip() for x in writer_list]
        else:
            writer_list = [writer]

        return writer_list
    
    def correct_headlines(headline, category_slug):
        """modify headlines for commentary and eigth page articles to contain section names"""
        if (category_slug == 'eighthpage'):
            headline = 'Phillipian Satire: ' + headline
        if (category_slug == 'commentary'):
            headline = 'Phillipian Commentary: ' + headline
        return headline

    def add_options(category_string, featured_post):
        # for featured articles, move timestamp forward and add to the featured category
        more_options = ''
        if featured_post in ['yes', 'x']:
            post_timestamp = (dt.datetime.now()+dt.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
            more_options += "--post_date='"+post_timestamp+"'"
            category_string += ',featured'
        return category_string, more_options

    category_slug = category_slugs[s] # main category slug

    # LOAD ROW INFO 
    status = row['ready for autoupload'].rstrip().lower()
    is_uploaded = row['uploaded online'].rstrip().lower()
    if (status not in ['yes', 'x'] or is_uploaded in ['yes', 'x']): 
        # only upload finished articles that aren't already uploaded-- skip all rows that are not marked
        if s == 'multilingual':
            print('skipping:\t'+row['Translated Headline'].rstrip())
        else:
            print('skipping:\t'+row['Headline'].rstrip())
        return
    article_doc_url = row['Link'].rstrip()
    tag = row['TAGS'].rstrip()
    writer = row['Writer'].rstrip()
    writer_list = writer_to_writer_list(writer) # process writer list
    if s == 'multilingual': # multilingual specific processing:
        headline = row['Translated Headline'].rstrip()
        translator = row['Translator'].rstrip()
        writer_list.append(translator) # add translator to writer list
        language = row['Language'].rstrip()
        category_slug = category_slug + ',' + "'" + language + "'" # add language to category slug
        featured_post = '' # do not feature multilingual articles
    else:
        headline = row['Headline'].rstrip()
        featured_post = row['Featured'].rstrip().lower()
        imgdir = row['ImageDir'].rstrip()
    if s == 'sports': # sports specific processing:
        category = row['Subcategory'].rstrip()
        category_slug = assign_categories(category_slug, category, headline) # assign categories and subcategories
    headline = correct_headlines(headline, category_slug)
    assert len(writer_list) > 0, 'error: no writers detected'

    # PROCESS ARTICLE TEXT
    # make sure that the following strings exist
    helper.check_content([article_doc_url, headline])
    print('Processing:\t' + headline + ' from ' + s) # progress string
    if (not 'docs.google.com/document/d/' in article_doc_url): # verify url
        print('  Error: not a url, now skipping '+article_doc_url)
        return
    
    
    # fetch article from google docs and place in json at the path article_txt
    article_txt = fetch_document.get_google_doc(article_doc_url, local_article_path+s) 
    
    article_info = {}
    with open(article_txt, 'r') as f:
        article_info = json.load(f)

    # get json info
    category_string, more_options = add_options(category_slug, featured_post)
    caption_list, credit_list, image_path_list = process_article_imgs(imgdir)

    # prepend info to article text file
    article_info['tags'] = tag.strip()
    article_info['headline'] = headline.strip() 
    article_info['writer'] = writer_list
    
    article_info['categories'] = category_string.strip() 
    article_info['more_options'] = more_options.strip() 

    article_info['caption'] = caption_list
    article_info['credit'] = credit_list
    article_info['img_paths'] = image_path_list
    #article_info['article_txt'] = article

    with open(article_txt, 'w') as f:
        json.dump(article_info, f)


for s in sections:
    print('starting section:\t' + s)
    section_df = process_section(s)
    section_df.apply(process_section_df_row, axis=1, args=(s,))


copy_article_to_server(local_article_path)

'''
Experimental + untested: uncomment if you dare

for s in sections:
    print('removing files for section:\t' + s)
    helper.remove_local_articles(local_article_path, s)

'''
