# If pulled from github, delete the token file. credentials.json is connected to lenss@glaseducation.org

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from datetime import datetime, timedelta

import smtplib, ssl
import os, sys
import configparser

Email_FilePathName = sys.argv[1]
readEmail = configparser.ConfigParser()
readEmail.read(Email_FilePathName)

port = 465
password = readEmail['email']['password']
smtp_server = "smtp.gmail.com"
sender = readEmail['email']['username']
receivers = readEmail['watchdog']['mailingList']

context = ssl.create_default_context()

def getSearchQuery():
    yesterday = datetime.now() - timedelta(1)
    time = yesterday.strftime('%Y-%m-%d_LENSSTSL')
    return time

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def getFileNames():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        q="name contains '{0}'".format(getSearchQuery()), spaces='drive', fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        outcome = "No files found."
    else:
        outcome = ""
        for item in items:
            outcome = outcome + "{0} ({1})".format(item['name'], item['id']) + ","

    return outcome

def sendStatus():
    message = """\
    Subject: Daily Status Report

    The following data files were added to the LENSS Drive today:
    {0}""".format(getFileNames())

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        for address in receivers:
            server.sendmail(sender, address, message)
 
if __name__ == '__main__':
    sendStatus()
