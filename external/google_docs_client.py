"""
This file contains the functions necessary to access Google Docs. Specifically
it allows you get a Google Docs' client, verify that a file exists,
and access that file.
"""

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

FOLDER_ID_LENSS_TSL_002 = "1jr5G9i0_Qa9kgXbaaWolglRNEgz6OMl3"


class GoogleDocs:
    """
    This class is the abstraction that will be used to access Google Doc
    storage.
    """

    def __init__(self):
        g_auth = GoogleAuth()
        g_auth.LoadCredentialsFile("../client_secrets.json")
        if g_auth.credentials is None:
            # Authenticate if they're not there
            g_auth.LocalWebserverAuth()
        elif g_auth.access_token_expired:
            # Refresh them if expired
            g_auth.Refresh()
        else:
            # Initialize the saved creds
            g_auth.Authorize()
        # Save the current credentials to a file
        g_auth.SaveCredentialsFile("../google_credentials.txt")

        self.drive = GoogleDrive(g_auth)

    def does_file_exist(self, file_name: str):
        """
        This function takes in a file's folder and its name and returns a
        boolean indicating if a file exists.

        Inputs:
            file_name (str): the name of the desired file

        Returns (bool):
            a boolean indicating whether the requested file exists
        """

        return (
            len(
                self.drive.ListFile(
                    {"q": f"title = '{file_name}' and mimeType='text/plain'"}
                ).GetList()
            )
            > 0
        )

    def get_file(self, file_name: str):
        """
        This function takes in a file's folder and its name and returns a file
        object.

        Inputs:
            folder (str): the desired folder
            file_name (str): the name of the desired file

        Returns (file object):
            the file object requested
        """

        return self.drive.ListFile(
            {"q": f"title = '{file_name}' and mimeType='text/plain'"}
        ).GetList()[0]
