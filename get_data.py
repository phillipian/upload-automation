from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request, AuthorizedSession
import gspread
import pandas as pd


# SPREADSHEET_NAME = input("Spreadsheet Name")
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1XrCCN4SI0ZReGy9G44b9_afTIqCzT2sMNUXx1DgCyUo/edit#gid=1756024164'

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

    section_sheet = sheet.worksheet(section)

    values = section_sheet.get_all_values()
    section_sheet_data = pd.DataFrame(values[2:])
    return section_sheet_data

gsheet = get_google_sheet(SPREADSHEET_URL, 'Commentary')
print(gsheet.head())
gsheet.to_csv(r'../test1.csv',encoding='utf-8')
