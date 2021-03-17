# If pulled from github, delete the token file. credentials.json is connected to lenss@glaseducation.org

from __future__ import print_function #imports for Google Drive API functionality
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from datetime import datetime, timedelta #time based variables for search query function

import smtplib #email code imports
import os, sys
import configparser
from getpass import getpass

def getSearchQuery(): #finds what to search for in Google Drive API
    yesterday = datetime.now() - timedelta(1) #uses today's date and the equivalent to one day to find yesterday's date
    time = yesterday.strftime('%Y-%m-%d_LENSSTSL') #assembles time into a string for search
    return time #end result

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly'] #limits what email can do on google drive

def getFileNames(): #API search for yesterday's files
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
        q="name contains '{0}'".format(getSearchQuery()), spaces='drive', fields="nextPageToken, files(id, name)").execute() # searches API: search query input into q
    items = results.get('files', [])

    if not items:
        outcome = "No files found."
    else:
        outcome = ""
        for item in items:
            outcome = outcome + str(item['name']) + "," # returns a list of all files found

    return outcome

def sendStatus(): # sends email
    message = """\
    Subject: Daily Status Report

    The following data files were added to the LENSS Drive today:
    {0}""".format(getFileNames()) # what will be sent out

    #Email_FilePathName = sys.argv[1] #reads 2nd argument to find file containing email and mailing list information
    #readEmail = configparser.ConfigParser()
    #readEmail.read(Email_FilePathName)

    password = getpass() #obscured input for password
    sender = 'lenss@glaseducation.org'
    receivers = ['joe@glaseducation.org', 'adam@glaseducation.org']

    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.ehlo
    smtp_server.login(sender, password)
    for i in range(len(receivers)):
        print(receivers[i])
        smtp_server.sendmail(sender, receivers[i], message)
    smtp_server.close()
 
if __name__ == '__main__':
    sendStatus()
