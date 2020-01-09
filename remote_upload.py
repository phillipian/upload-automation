"""
read article and img info from top of article text file
post

(run from server)
"""
import os
from subprocess import call
from subprocess import check_output
import helper
import imgprepare_python_2 # TODO: uncomment, change everything to imgprepare
from student_directory import StudentDirectory
import json
import re

#Set up student directory to search author names and emails

os.chdir('/home/plipdigital/phillipian.net') # must run script in wordpress installation, so cd
with open('../students.json', 'r') as f:
    students = json.load(f)
directory = StudentDirectory(students)

server_article_path = '/home/plipdigital/temp_articles/articles/' # path to articles on the server (same as from local script + articles/)
sections = [ 'News', 'Sports','Commentary', 'Arts', 'The Eighth Page', 'Multilingual', 'Editorial'] # sections to upload
server_name = 'plipdigital@phillipian.net/home/plipdigital/phillipian.net' # TODO: I'm not sure if this works
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']

def fetch_writer_id(writer_str):
    writer_login = helper.remove_spaces_commas(writer_str).lower()
    try:
        writer_email = directory.student_dict[directory.search_by_name(writer.split(' ')[0], writer.split(' ')[-1])[0]]['email']
        print(writer_email)
    except:
        writer_email = writer_login + '@phillipian.net'
    try:
        cmd = 'wp user create ' + writer_login + ' ' + writer_email + " --role='author' --display_name='"+writer+"' --first_name='"+writer.split(' ')[0]+"' --last_name='"+writer.split(' ')[-1]+"' --porcelain"
        writer_id = check_output(cmd, shell=True).strip()
    except:
        print('failed cmd '+cmd)
        cmd = 'wp user get --field=ID ' + writer_login
        writer_id = check_output(cmd, shell=True).strip()

    return writer_id

# FETCH ARTICLES; TODO: do it by section
article_txts = os.listdir(server_article_path) # array of article text files

for article_txt in article_txts: # loop through articles and upload them
    # article properties
    article_txt = server_article_path+article_txt
    if 'filter' in article_txt: # only upload filtered articles
        print('uploading '+article_txt)
        '''
        more_options = helper.deprepend(article_txt).split('\t')
        '''
        article_info = {}
        with open(article_txt, "r") as f:
            article_info = json.load(f)
        more_options = article_info['more_options']
        if len(more_options) > 1: # catch possibility of no options
            more_options = more_options.strip()
        else:
            more_options = ''

        categories = article_info['categories'].strip()
        writer_list = article_info['writer']
        headline = article_info['headline'].strip()
        writer_ids = [fetch_writer_id(writer) for writer in writer_list] # fetch writer id number, or create user if writer does not exist
        img = article_info['img_path'].strip()

        article_string = article_info['article_content']

        with open(article_txt[:-5]+'.txt', 'wb') as f: 
            f.write(article_info['article_content'].encode('utf8'))

        helper.add_line_breaks(article_txt[:-5]+'.txt')

        headline = re.sub('"','\\"',headline) # escape double quotes

        print('  headline '+headline)

        if (img != NOPHOTO):
            credit = article_info['credit'].strip()
            caption = article_info['caption']
            '''
            if len(caption) > 1: # catch possibility of no options
                caption = caption[1].strip()
            else:
                caption = ''
            '''
            # upload the image to the media library
            cmd = 'wp media import "'+img+'" --porcelain | xargs -I {} wp post list --post__in={} --field=url --post_type=attachment'
            img_url = check_output(cmd, shell=True)
            img_url = helper.media_url_to_img_url(img_url, img.split('/')[-1])

            image_shortcode = imgprepare_python_2.img_for_post_content(img_url, caption, credit)
            helper.prepend(article_txt[:-5]+'.txt', image_shortcode)

        # POST WITH GIVEN PARAMETERS
        cmd = "wp post create " + article_txt[:-5]+'.txt' + " --post_category="+ categories +' --post_status=publish --post_title="'+ headline +'" --porcelain --post_author='+ writer_id + ' ' + more_options.strip()
        post_id = check_output(cmd, shell=True)
        print('posted article')
        call("mv " + article_txt[:-5]+'.txt ' + server_article_path + "uploaded/", shell=True)
        call("mv " + article_txt + " " + server_article_path + "uploaded/", shell=True) 
        # CUSTOM AUTHOR UPDATE
        # cmd = 'wp post get ' + post_id[:-1] + ' --field=post_author'
        # user_num = check_output(cmd, shell=True)[:-1]
        # cmd = 'wp user get ' + user_num + ' --field=display_name'
        # author_name = check_output(cmd, shell=True)[:-1]
        # cmd = 'wp post meta update ' + post_id[:-1] + ' cpa_author "' + author_name+'"'
        # call(cmd, shell=True)
