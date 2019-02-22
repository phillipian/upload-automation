from __future__ import print_function
import pickle
import os.path
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])

    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))


    # added this, hope it works??

    # file_id = '1meoBMYrymou6K80UJV4VGFWLdZ8WK7fwkjZ_l0z56bs'
    file_id = '1pR5rRTTOHmgW6oFM34p72PkFSCBuzseDTnG-f5tQdfc'
    mimeType = 'text/plain'

    # request = service.files().get(fileId=file_id) # to get just the metadata
    request = service.files().export(fileId=file_id, mimeType=mimeType) # to get the file content
    fh = io.BytesIO()
    # fh = io.FileIO('A/E Basketball', 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d" % int(status.progress() * 100))
    # print(fh.getvalue())
    html = fh.getvalue()
    with open('file3.txt', 'wb') as f: 
        f.write(html)

if __name__ == '__main__':
    main()
