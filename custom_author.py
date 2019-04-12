# TODO: support multiple author functionality
import os
from subprocess import call
from subprocess import check_output
import sys
import pandas as pd
import fetch_sheet
import fetch_document
import assign_subcategory
import helper
import argparse
import datetime

# sections = ['Sports', 'News', 'Commentary', 'Arts', 'The Eighth Page'] # sections to upload
sections = ['News']

def write_authors():
   cmd = 'wp post list --post_type=post --format=ids'
   post_list = check_output(cmd, shell=True)
   for post_id in post_list:
       cmd = 'wp post get ' + post_id + ' --field=post_author'
       author_name = check_output(cmd, shell=True)
       cmd = 'wp post meta update ' + post_id + ' Custom Post Author ' + author_name
def write_authors_from_list(posts):
   for post_id in posts:
       cmd = 'wp post get ' + post_id + ' --field=post_author'
       author_name = check_output(cmd, shell=True)
       cmd = 'wp post meta update ' + post_id + ' Custom Post Author ' + author_name
 
write_authors()
