from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request, AuthorizedSession
import gspread
import pandas as pd


SPREADSHEET_NAME = input("Spreadsheet Name")


def get_google_sheet(spreadsheet_id):
    """ Retrieve sheet data using OAuth credentials and Google Python API. """
    SCOPES = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
    SERVICE_ACCT_FILE = '../client_secret.json'
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCT_FILE, scopes=SCOPES)
    client = gspread.Client(auth=credentials)
    client.session = AuthorizedSession(credentials)
    sheet = client.open(spreadsheet_id).sheet1
    values = sheet.get_all_values()
    sheet_data = pd.DataFrame(values[2:])
    return sheet_data

gsheet = get_google_sheet(SPREADSHEET_NAME)
print(gsheet.head())
gsheet.to_csv(r'../test1.csv')
