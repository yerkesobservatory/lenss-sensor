""" WATCHDOG
    ========
    
    This is the watchdog program for the LENSS SENSOR project.
    
    The program does the following:
    Generates a search query based on yesterday's date
    Navigates the Google Drive API and finds data files created yesterday
    Emails the names of all matching files to Adam and Joe
    
    Authors: Joe Murphy
"""


#### Setup

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

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly'] #limits what email can do on google drive
tokenfile = 'token.json'
credentialsfile = sys.argv[1]
#emailpassword = os.getenv('LENSS_EMAIL_PASSWORD')

#### Function Definitions

def getSearchQuery(): 
    """ This functions generates the filename to search for in the Google Drive
        The filename is based on the date.
    """
    yesterday = datetime.now() - timedelta(1) #uses today's date and the equivalent to one day to find yesterday's date
    time = yesterday.strftime('%Y-%m-%d_LENSSTSL') #assembles time into a string for search
    return time #end result

def getFileNames():
    """ Looks for files uploaded in the last day on google drive.
        The function returns a list of filenames.
    """
    #### Get Google Drive API Credentials
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(tokenfile):
        creds = Credentials.from_authorized_user_file(tokenfile, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentialsfile, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenfile, 'w') as token:
            token.write(creds.to_json())

    #### Get information from the API
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    # searches API: search query input into q
    results = service.files().list(q="name contains '{0}'".format(getSearchQuery()), 
                                   spaces='drive', 
                                   fields="nextPageToken, files(id, name)").execute()
    # Get the list of files
    items = results.get('files', [])

    # Make response string
    if not items:
        outcome = "No files found."
    else:
        outcome = ""
        for item in items:
            outcome = outcome + str(item['name']) + "," # returns a list of all files found

    return outcome

def sendStatus():
    """ This function sends the mail with the daily status report
    """
    # Define mail message
    message = """\
    Subject: Daily Status Report

    The following data files were added to the LENSS Drive today:
    {0}""".format(getFileNames()) # what will be sent out

    Email_FilePathName = sys.argv[2] #reads 3rd argument to find file containing email and mailing list information
    readEmail = configparser.ConfigParser()
    readEmail.read(Email_FilePathName)

    emailpassword = readEmail['login']['pw']

    # Define email credentials
    if emailpassword:
        password = emailpassword
    else:
        password = getpass() #obscured input for password
    sender = 'lenss@glaseducation.org'
    receivers = ['joe@glaseducation.org', 'adam@glaseducation.org']

    # Use the SMTP library to send the email
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.ehlo
    smtp_server.login(sender, password)
    for i in range(len(receivers)):
        # Send email to each receiver
        print(receivers[i])
        smtp_server.sendmail(sender, receivers[i], message)
    smtp_server.close()
 
if __name__ == '__main__':
    sendStatus()
