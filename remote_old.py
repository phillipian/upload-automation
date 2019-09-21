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
import re

os.chdir('/home/plipdigital/phillipian.net') # must run script in wordpress installation, so cd

server_article_path = '/home/plipdigital/temp_articles/articles/' # path to articles on the server (same as from local script + articles/)
sections = [ 'News', 'Sports','Commentary', 'Arts', 'The Eighth Page'] # sections to upload
server_name = 'plipdigital@phillipian.net/home/plipdigital/phillipian.net' # TODO: I'm not sure if this works
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']

def fetch_writer_id(writer_str):
    writer_login = helper.remove_spaces_commas(writer_str).lower()
    try:
        cmd = 'wp user create ' + writer_login + ' ' + writer_login +"@phillipian.net --role='author' --display_name='"+writer+"' --first_name='"+writer.split(' ')[0]+"' --last_name='"+writer.split(' ')[-1]+"' --porcelain"
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
    if 'raw' in article_txt: # only upload filtered articles
        continue
    print('uploading '+article_txt)
    more_options = helper.deprepend(article_txt).split('\t')
    if len(more_options) > 1: # catch possibility of no options
        more_options = more_options[1].strip()
    else:
        more_options = ''

    categories = helper.deprepend(article_txt).split('\t')[1].strip()
    writer = helper.deprepend(article_txt).split('\t')[1].strip()
    headline = helper.deprepend(article_txt).split('\t')[1].strip()
    writer_id = fetch_writer_id(writer) # fetch writer id number, or create user if writer does not exist
    img = helper.deprepend(article_txt).split('\t')[1].strip()

    headline = re.sub('"','\\"',headline) # escape double quotes
    
    print('  headline '+headline)
    
    if (img != NOPHOTO):
        credit = helper.deprepend(article_txt).split('\t')[1].strip()
        caption = helper.deprepend(article_txt).split('\t')
        if len(caption) > 1: # catch possibility of no options
            caption = caption[1].strip()
        else:
            caption = ''

        # upload the image to the media library
        cmd = 'wp media import "'+img+'" --porcelain | xargs -I {} wp post list --post__in={} --field=url --post_type=attachment'
        img_url = check_output(cmd, shell=True)
        img_url = helper.media_url_to_img_url(img_url, img.split('/')[-1])

        image_shortcode = imgprepare_python_2.img_for_post_content(img_url, caption, credit)
        helper.prepend(article_txt, image_shortcode)
        
    # POST WITH GIVEN PARAMETERS
    cmd = "wp post create " + article_txt + " --post_category="+ categories +' --post_status=publish --post_title="'+ headline +'" --porcelain --post_author='+ writer_id + ' ' + more_options.strip()
    post_id = check_output(cmd, shell=True)
    print('posted article as draft')
    # CUSTOM AUTHOR UPDATE
    # cmd = 'wp post get ' + post_id[:-1] + ' --field=post_author'
    # user_num = check_output(cmd, shell=True)[:-1]
    # cmd = 'wp user get ' + user_num + ' --field=display_name'
    # author_name = check_output(cmd, shell=True)[:-1]
    # cmd = 'wp post meta update ' + post_id[:-1] + ' cpa_author "' + author_name+'"'
    # call(cmd, shell=True)
