import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_drive_service():
    """Initialize and return the Google Drive service object."""
    creds = None

    # token.json created on first run
    if os.path.exists("config/token.json"):
        creds = Credentials.from_authorized_user_file("config/token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("Credentials refreshed.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("config/client_secrets.json", SCOPES)
                creds = flow.run_local_server(port=63208)
                print("New credentials obtained.")
            
            # Save the credentials for the next run
            with open("config/token.json", "w") as token:
                token.write(creds.to_json())
                print("Credentials saved to token.json.")
        except Exception as e:
            print(f"An error occurred during authentication: {e}")
            return None

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        print("Google Drive service created successfully.")
        return drive_service
    except HttpError as error:
        print(f"An error occurred while building the Drive service: {error}")
        return None
