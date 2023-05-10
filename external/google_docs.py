"""
This file contains the functions necessary to access Google Docs. Specifically
it allows you get a Google Docs' client, verify that a file exists,
and access that file.
"""

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials


class GoogleDocs:
    """
    This class is the abstraction that will be used to access Google Doc
    storage.
    """

    def __init__(self):
        scope = ["https://www.googleapis.com/auth/drive"]
        g_auth = GoogleAuth()
        g_auth.auth_method = "service"
        g_auth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "client_secrets.json", scope
        )
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

        Returns (list):
            returns a list containing all lines of the file
        """

        if not self.does_file_exist(file_name):
            return []

        gcp_file = self.drive.ListFile(
            {"q": f"title = '{file_name}' and mimeType='text/plain'"}
        ).GetList()[0]

        file = self.drive.CreateFile({"id": gcp_file["id"]})

        return file.GetContentString().split("\r\n")
