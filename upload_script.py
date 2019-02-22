import os
from subprocess import call
import sys
import pandas as pd
import fetch_sheet
import fetch_document

"""
# cd to wordpress
call("pwd")
os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
call("pwd")

# make a post with the given parameters
call("wp post create --from-post=1 --post_title='Testing wp cli FROM PYTHON'", shell=True)
"""

import argparse

parser = argparse.ArgumentParser(description='Upload articles from the budget spreadsheet.')
parser.add_argument('--url', metavar='URL', type=str, nargs='?',
                    help='url of the budget spreadsheet as it appears in the browser')
args = parser.parse_args()
sheet_url = args.url
# TODO: catch if no value is provided

# fetch articles and photos from sheet
sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page']
for s in sections:
    section_df = fetch_sheet.get_google_sheet(sheet_url, s)
    print(section_df.head()['Slug'].values)




# fetch content
# create posts
# add photos

