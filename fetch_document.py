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
BOFSTR = 'BOFCXLII'
EOFSTR = 'EOFCXLII'

def get_file_id_from_url(doc_url):
    partial_prefix = 'docs.google.com/document/d/'
    postfix = '/edit'

    start = doc_url.index(partial_prefix)+len(partial_prefix)
    end = doc_url.index(postfix)
    return doc_url[start:end]

def article_from_txt(raw_txt, filter_txt):
    # each line is a paragraph
    rf = open(raw_txt, 'r')
    wf = open(filter_txt, 'w')
    copy = False
    for x in rf:
        if ('EOFCXLII' in x):
            break
        if (copy):
            wf.write(x) 
        if ('BOFCXLII' in x):
            copy = True
         
    rf.close()
    wf.close()

def get_google_doc(doc_url):
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
            flow = InstalledAppFlow.from_client_secrets_file('/imgs/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    file_id = get_file_id_from_url(doc_url)
    print(file_id)
    mimeType = 'text/plain'

    # TODO: make this fit whatever we decide
    raw_article = file_id+'_raw.txt'
    filter_article = file_id+'_filter.txt'

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
    content = fh.getvalue()
    with open(raw_article, 'wb') as f: 
        f.write(content)
    
    article_from_txt(raw_article, filter_article)

    return filter_article

if __name__ == '__main__':
    get_google_doc('https://docs.google.com/document/d/15GuvkChMq_a-3Dbx7c8zCX1zzBpXQ2DD2Tnk6V3jDL0/edit')
