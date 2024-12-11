import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive']


def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')


def upload(service, filename):
    try:
        file_metadata = {'name': filename}
        media = MediaFileUpload(filename, mimetype='audio/mp3')
        results = service.files().list(pageSize=1, fields="files(id)", q=f"trashed=false and name='{filename}'").execute()
        files = results.get('files')
        if files:
            file = (
                service.files()
                .update(fileId=files[0]['id'], media_body=media)
                .execute()
            )
        else:
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields='id')
                .execute()
            )
        # print(f'File ID: {file.get("id")}')
        return file.get('id')
    except HttpError as error:
        print(f'An error occurred: {error}')
