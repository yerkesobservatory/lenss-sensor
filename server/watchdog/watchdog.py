""" WATCHDOG
    ========
    
    This is the watchdog program for the LENSS SENSOR project.
    
    The program does the following:
    Generates a search query based on yesterday's date
    Navigates the Google Drive API and finds data files created yesterday
    Emails the names of all matching files to Adam and Joe
    
    Authors: Joe Murphy, Alex Scerba
"""


#### Setup

# If pulled from github, delete the token file. credentials.json is connected to lenss@glaseducation.org

from __future__ import print_function
from googleapiclient.discovery import build
from apiclient import errors
from email.mime.text import MIMEText
import base64
from google.oauth2 import service_account

from datetime import datetime, date, timedelta #time based variables for search query function

EMAIL_FROM = 'lenss@glaseducation.org'
EMAIL_TO = ['adam@glaseducation.org', 'chris@glaseducation.org', 'dylan@glaseducation.org', 'ascerba@glaseducation.org']
EMAIL_SUBJECT = 'LENSS Daily Status Report'

#### Function Definitions

def get_service(api_name, api_version, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = service_account.Credentials.from_service_account_file(
            key_file_location)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service

def get_search_query(): 
    """ This functions generates the filename to search for in the Google Drive
        The filename is based on the date.
    """
    yesterday = datetime.now() - timedelta(1) #uses today's date and the equivalent to one day to find yesterday's date
    time = yesterday.strftime('%Y-%m-%d_LENSSTSL') #assembles time into a string for search
    
    return time #end result

def get_file_names(service):
    """ Looks for files uploaded in the last day on google drive.
    The function returns a list of filenames. """

    files = []
    
    # Call the Drive v3 API
    # searches API: search query input into q
    sensors_data_folder = service.files().list(q="'1qTskg1BMyn4uPyRk_mSlxJpSiM08p_93' in parents and name contains '{0}'".format(date.today().strftime('%Y-%m')), 
                                   spaces='drive', 
                                   fields="nextPageToken, files(id, name)").execute()
    year_month_folder_ids = []
    for folder in sensors_data_folder.get('files', ['id']): 
      year_month_folder_ids.append(folder.get("id"))

    for folder_id in year_month_folder_ids:
      year_month_folder = service.files().list(q="'{0}' in parents".format(folder_id), 
                                   spaces='drive', 
                                   fields="nextPageToken, files(id, name)").execute()
      sensor_folder_ids = []
      for folder in year_month_folder.get('files', ['id']):
        sensor_folder_ids.append(folder.get("id"))

      for folder_id in sensor_folder_ids:
        sensor_folder = service.files().list(q="'{0}' in parents and name contains '{1}'".format(folder_id, get_search_query()), 
                                   spaces='drive', 
                                   fields="nextPageToken, files(id, name)").execute()
        for data_file in sensor_folder.get('files', ['id']):
          files.append(data_file.get("name"))
    
    # Make response string
    if not files:
        outcome = "No files found."
    else:
        outcome = ""
        for item in files:
            outcome += item + "\n" # returns a list of all files found

    print(date.today().strftime('%Y-%m'))
    print(outcome)
    return outcome

def create_message(sender, to, subject, file_names):
  """Create a message for an email.
  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText("""\
The following data files were added to the LENSS Drive today:

{0}""".format(file_names))
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw = base64.urlsafe_b64encode(message.as_bytes())
  return {'raw': raw.decode()}

def send_message(service, user_id, message):
  """Send an email message.
  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.
  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)

def service_account_login(service_account_file):
  SCOPES = ['https://www.googleapis.com/auth/gmail.send']

  credentials = service_account.Credentials.from_service_account_file(
          service_account_file, scopes=SCOPES)
  delegated_credentials = credentials.with_subject(EMAIL_FROM)
  service = build('gmail', 'v1', credentials=delegated_credentials)
  return service
 
def main():
    SERVICE_ACCOUNT_FILE = 'key.json'

    drive_service = get_service(
        api_name='drive',
        api_version='v3',
        key_file_location=SERVICE_ACCOUNT_FILE)

    mail_service = service_account_login(SERVICE_ACCOUNT_FILE)

    email_content = get_file_names(drive_service)

    # Call the Gmail API
    message = ""
    for recipient in EMAIL_TO:
        message = create_message(EMAIL_FROM, recipient, EMAIL_SUBJECT, email_content)
        sent = send_message(mail_service,'me', message)

if __name__ == '__main__':
    main()