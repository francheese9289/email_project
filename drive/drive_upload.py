import os

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

project_id = 'clean-up-project-430018'


def get_folder(drive_service, folder_name):
  try:
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    if not items:
      file_metadata = {
          "name": folder_name,
          "mimeType": "application/vnd.google-apps.folder",
      }
      file = drive_service.files().create(body=file_metadata, fields="id").execute()
      return file.get("id")
    else:
      return items[0].get("id")


  except HttpError as error:
    print(f"An error occurred: {error}")
    return None



def upload_csv(drive_service, file_path, folder_id=None):
    """Upload a CSV file to Google Drive."""
    try:
      file_metadata = {'name': os.path.basename(file_path)}
      if folder_id:
          file_metadata['parents'] = [folder_id]

      media = MediaFileUpload(file_path, mimetype='text/csv')

      file = drive_service.files().create(
          body=file_metadata,
          media_body=media,
          fields='id'
      ).execute()

      file_id=file.get("id")

      drive_service.permissions().create(fileId=file_id, body={'role': 'reader', 'type': 'anyone'}).execute()
                              
      print(f'UPLOAD SUCCESS\nFile ID: {file_id}' )
      
      link = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
      return link

    except Exception as error:
      print(f'An error occured: {error}')

