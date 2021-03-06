from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request, AuthorizedSession
import gspread
import pandas as pd
import numpy as np

'''
def get_hyperlinks(raw_links):
    link_list = []
    for raw in raw_links:
        if (raw == '' or 'Slug'):
            continue
        elif('=HYPERLINK' in raw):
            link = raw[10:-2].split(',')[0].strip('"')[2:]
            link_list.append(link)
    return link_list
'''
def get_google_sheet(spreadsheet_url, section):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    SCOPES = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    SERVICE_ACCT_FILE = '../client_secret.json'

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCT_FILE, scopes=SCOPES)
    client = gspread.Client(auth=credentials)
    client.session = AuthorizedSession(credentials)

    sheet = client.open_by_url(spreadsheet_url) # for spreadsheet by URL
    # sheet1 = client.open(spreadsheet_id).sheet1 # for spreadsheet by NAME

    # convert sheet to dataframe
    section_sheet = sheet.worksheet(section)
    values = section_sheet.get_all_values()
    #print(section_sheet.col_values(1, 'FORMULA'))
    #links = pd.DataFrame(section_sheet.col_values(1, 'FORMULA')[2:])
    section_sheet_df = pd.DataFrame(values[2:])

    # rename columns
    col_names = section_sheet_df[0:1].values[0]
    section_sheet_df = section_sheet_df[1:]
    section_sheet_df.columns = col_names
    #print(section_sheet_df)
    return section_sheet_df

def main():
    # SPREADSHEET_NAME = input("Spreadsheet Name")
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1XrCCN4SI0ZReGy9G44b9_afTIqCzT2sMNUXx1DgCyUo/edit#gid=1756024164'
    gsheet = get_google_sheet(SPREADSHEET_URL, 'Commentary')
    photo_sheet = get_google_sheet(SPREADSHEET_URL, 'Photo')
    print(gsheet.head())
    print(photo_sheet.head())
    gsheet.to_csv(r'../test1.csv',encoding='utf-8')
    photo_sheet.to_csv(r'../test2.csv',encoding='utf-8')
if __name__ == '__main__':
    main()
