import os
from subprocess import call
from subprocess import check_output
import sys
import pandas as pd
import fetch_sheet
import fetch_document
import argparse

# PATH
# TODO: get the real path from newsroom computer, THIS IS A PLACEHOLDER
PATHPREFIX = os.getcwd()+'/../Digital/'

# sections to upload
sections = ['News']
# sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page']


parser = argparse.ArgumentParser(description='Upload articles from the budget spreadsheet.')
parser.add_argument('--url', metavar='URL', type=str, nargs='?',
                    help='url of the budget spreadsheet as it appears in the browser')
args = parser.parse_args()
sheet_url = args.url
# TODO: catch if no value is provided


# fetch sheet dataframe
for s in sections:
    section_df = fetch_sheet.get_google_sheet(sheet_url, s)

# fetch article text
    if ('Link' in section_df.columns):
        test_url = section_df.head()['Link'].values[0]
        final_txt = fetch_document.get_google_doc(test_url)
# create post (TEMPORARY, for TESTING)
        # cd to wordpress (test code for computer only)
        workingdir = os.getcwd()
        os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
        call("pwd")
        # make a post with the given parameters
        # print(workingdir,'wdend')
        
        # TODO: uncomment one

        cmd = "wp post create --porcelain --post_status=publish --post_title='INSERT HEADLINE' " + workingdir+'/'+final_txt
        post_id = check_output(cmd, shell=True)
        print("POSTID " + str(post_id))

        # cmd = "wp post create --post_status=publish --post_title='Article 1' " + workingdir+'/'+final_txt
        # call(cmd, shell=True)

# fetch image folder path
        if ('Images' in section_df.columns):
            test_path = PATHPREFIX + s + '/' + section_df.head()['Images'].values[0]
            # print(test_path)

            images = os.listdir(test_path)
            print(images)

            for image in images:
                cmd = "wp media import " + test_path + '/' + image + " --post_id=" + post_id
                call(cmd, shell=True)


# add photos
