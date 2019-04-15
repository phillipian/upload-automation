"""
read article and img info from top of article text file
post

(run from server)
"""
import os
from subprocess import call
from subprocess import check_output
import sys
import pandas as pd
import fetch_sheet
import fetch_document
import assign_subcategory
import helper
import imgprepare_python_2 # TODO: uncomment, change everything to imgprepare
import argparse
import datetime
import custom_author
import re 

server_article_path = '/home/plipdigital/temp_articles/' # path to articles on the server
sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page'] # sections to upload
server_name = 'plipdigital@phillipian.net/home/plipdigital/phillipian.net' # TODO: I'm not sure if this works
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']

def fetch_writer_id(writer_str):
    writer_login = helper.remove_spaces_commas(writer_str).lower()
    
    try:
        cmd = 'wp user create ' + writer_login + ' ' + writer_login + "@phillipian.net --ssh="+server_name+" --role='author' --display_name='"+writer+"' --porcelain"
        writer_id = check_output(cmd, shell=True)
    except:
        cmd = 'wp user get --ssh='+server_name+' --field=ID ' + writer_login
        writer_id = check_output(cmd, shell=True)

    return writer_id

# FETCH ARTICLES
for s in sections:
    print('starting section: ' + s)
    article_txts = os.listdir(server_article_path+s.lower()) # array of article text files 
    
    for article_txt in article_txts: # loop through articles and upload them
        # article properties
        headline = deprepend(article_txt).split('\t')[1].strip()
        writer = deprepend(article_txt).split('\t')[1].strip()
        categories = deprepend(article_txt).split('\t')[1].strip()
        more_options = deprepend(article_txt).split('\t')[1].strip()

        writer_id = fetch_writer_id(writer) # fetch writer id number, or create user if writer does not exist

        img = deprepend(article_txt).split('\t')[1].strip()
        if (img != NOPHOTO):
            # TODO: fill this in
            caption = ''
            credit = ''

            # upload the image to the media library
            cmd = 'wp media import '+img+' --porcelain | xargs -I {} wp post list --post__in={} --field=url --ssh='+server_name+' --post_type=attachment'
            img_url = check_output(cmd, shell=True)
            img_url = helper.media_url_to_img_url(img_url,imgs[ind])

            image_txt = imgprepare_python_2.img_for_post_content(img_url, caption, credit) 
            helper.prepend(article_txt, temp_shortcode)
        
        # POST WITH GIVEN PARAMETERS
        cmd = "wp post create " + article_txt + " --post_category="+ category_string +" --post_status=publish --post_title='"+ headline +"' --porcelain --post_author="+ writer_id + ' ' + more_options 
        post_id = check_output(cmd, shell=True)

        # CUSTOM AUTHOR UPDATE
        cmd = 'wp post get ' + post_id[:-1] + ' --field=post_author --ssh='+server_name
        user_num = check_output(cmd, shell=True)[:-1]
        cmd = 'wp user get ' + user_num + ' --field=display_name --ssh='+server_name
        author_name = check_output(cmd, shell=True)[:-1]
        cmd = 'wp post meta update --ssh='+server_name +' ' + post_id[:-1] + ' cpa_author "' + author_name+'"'
        call(cmd, shell=True)
