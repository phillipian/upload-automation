"""
read article and img info from top of article text file
post

(run this script from the server)
"""
import os
from subprocess import call
from subprocess import check_output
import json
import re
import argparse
from student_directory import StudentDirectory

import sys
sys.path.append('../')
import helper
from config import * # TODO: test the config file import


def process_args():
    """process command line args"""
    parser = argparse.ArgumentParser(description='Upload articles to phillipian.net.')
    
    parser.add_argument(
        '--sections', 
        metavar='SECT', 
        type=str, 
        default='arts, commentary, editorial, news, sports, multilingual', 
        help='Comma separated list of sections to upload'
    )
    args = parser.parse_args()
    return args

def fetch_writer_id(writer_str):
    writer_login = helper.remove_spaces_commas(writer_str).lower()
    try:
        writer_email = directory.student_dict[directory.search_by_name(writer_str.split(' ')[0], writer_str.split(' ')[-1])[0]]['email']
    except:
        writer_email = writer_login + '@phillipian.net'
    try:
        cmd = 'wp user create ' + writer_login + ' ' + writer_email + " --role='author' --display_name='"+writer_str+"' --first_name='"+writer_str.split(' ')[0]+"' --last_name='"+writer_str.split(' ')[-1]+"' --porcelain"
        writer_id = check_output(cmd, shell=True).decode('utf8').strip()
    except:
        writer_login = re.sub(r'\W+', '', writer_login)
        print('failed cmd '+cmd)
        cmd = 'wp user get --field=ID ' + writer_login
        writer_id = check_output(cmd, shell=True).decode('utf8').strip()

    return writer_id

def upload_img(img):
    # upload the image to the media library and store its id
    cmd = 'wp media import "{}" --porcelain'.format(img)
    # img_id comes back as a byte string, so convert to unicode
    img_id = check_output(cmd, shell=True).decode('utf-8').strip()
    
    cmd = 'wp post list --post__in={} --field=url --post_type=attachment'.format(img_id)
    img_url = check_output(cmd, shell=True).decode('utf-8').strip()
    img_url = helper.media_url_to_img_url(img_url, img.split('/')[-1])

    return img_id, img_url

def upload_article(article_txt, section):
    # article properties
    article_txt = os.path.join(server_article_path, section, article_txt)

    if article_txt[:-5] in uploaded_list: # skip already uploaded articles
        return
    if not 'filter' in article_txt: # only upload filtered articles
        return
    if not '.json' in article_txt: # must be json file
        return

    print('uploading '+article_txt)

    # LOAD JSON
    article_info = {}
    with open(article_txt, "r", encoding='utf8') as f:
            article_info = json.load(f)
    headline = article_info['headline'].strip()
    headline = re.sub('"','\\"',headline) # escape double quotes
    print('  uploading headline: '+headline)
    writer_list = article_info['writer']
    writer_ids = [fetch_writer_id(writer) for writer in writer_list] # fetch writer id number, or create user if writer does not exist
    img_path_list = article_info['img_paths']
    # WRITE ARTICLE TO TEMP TXT FILE
    with open(article_txt[:-5]+'.txt', 'wb') as f: 
        f.write(article_info['article_content'].encode('utf8'))
    helper.add_line_breaks(article_txt[:-5]+'.txt')
    
    # PROCESS IMAGE(S) if article has image(s)
    img_id_list = [] # list of wp image ids
    credit_list = [] # list of credit ids 

    if NOPHOTO not in img_path_list:
        for i, (img, credit, caption) in enumerate(zip(img_path_list, article_info['credit'], article_info['caption'])):
            # upload image to the media library
            img_id, img_url = upload_img(img.strip())

            credit_id = fetch_writer_id(credit.split('/')[0]) #remove the /phillipian from the credit name

            # if multiple images, add closing image gallery tag 
            if i == 0 and len(img_path_list) > 1:
                helper.prepend(article_txt[:-5]+'.txt', '[/imggallery]')

            image_shortcode = helper.img_for_post_content(img_url, caption, credit_id, img_id)
            helper.prepend(article_txt[:-5]+'.txt', image_shortcode)

            img_id_list.append(img_id)
            credit_list.append(credit_id)

        # after processing all images, add starting image gallery tag if multiple images
        if len(img_path_list) > 1:
            helper.prepend(article_txt[:-5]+'.txt', '[imggallery]')

    # POST WITH GIVEN PARAMETERS
    cmd = 'wp post create {} --post_category={} --post_status=draft --post_title="{}" --porcelain --post_author={}'.format(
                article_txt[:-5]+'.txt', 
                article_info['categories'].strip(), 
                headline, 
                writer_ids[0] + ' ' + article_info['more_options'].strip()
    )
    # authorship
    post_id = check_output(cmd, shell=True).decode('utf8').rstrip()
    for writer_id in writer_ids:
        cmd = "wp user get {} --field=user_login".format(writer_id)
        username = check_output(cmd, shell=True).decode('utf8').rstrip()
        cmd = "wp co-authors-plus add-coauthors --coauthor={} --post_id={}".format(username, post_id)
        call(cmd, shell=True)
    
    # link media with creator page
    if NOPHOTO not in img_path_list:
        for i in range(len(img_path_list)):
            credit_id = credit_list[i]
            img_id = img_id_list[i]
      
            cmd = "wp user get {} --field=display_name".format(credit_id)
            full_name = check_output(cmd, shell=True).decode('utf8').rstrip()
            
            #TODO fix assign media credit function

            link_cmd = "php -f /home/plipdigital/upload-automation/src/remote/assign_media_credit.php {} {} {}".format(
                img_id, 
                post_id, 
                full_name 
            )
        call(link_cmd, shell=True)

    # Add tags to post
    cmd = "wp post term add {} post_tag {}".format(post_id, article_info['tags'])
            
    # MARK AS DONE
    print('posted')
    uploaded_list.append(article_txt[:-5])


# Set up student directory to search author names and emails
os.chdir(wp_install_dir) # must run script in wordpress installation
with open('../students.json', 'r') as f:
    students = json.load(f)
directory = StudentDirectory(students)

# obtain lowercase and whitespace-stripped section strings for sections to upload
# ex: [ 'news', 'sports','commentary', 'arts', 'multilingual', 'editorial']
args = process_args()
sections = [x.strip().lower().capitalize() for x in args.sections.split(',')] 

# GLOBAL VARS
uploaded_list = [] # list of uploaded articles

# FETCH ARTICLES BY SECTION
for s in sections:
    print('UPLOADING '+s.upper())
    article_txts = os.listdir(server_article_path+s) # return array of article text files

    for article_txt in article_txts: # loop through articles and upload them
        upload_article(article_txt, s)

