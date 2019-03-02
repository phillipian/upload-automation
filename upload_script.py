import os
from subprocess import call
import sys
import pandas as pd
import fetch_sheet
import fetch_document
import argparse

# PATH
# TODO: get the real path from newsroom computer
PATHPREFIX = 'PLACEHOLDER/Digital/'

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
# fetch image folder path
    if ('Images' in section_df.columns):
        test_path = PATHPREFIX + s + '/' + section_df.head()['Images'].values[0]
# create posts
"""
# cd to wordpress (test code for computer only)
call("pwd")
os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
call("pwd")

# make a post with the given parameters
call("wp post create --from-post=1 --post_title='Testing wp cli FROM PYTHON'", shell=True)
"""

# add photos
