from email_help.mbox_to_csv import check_files_in_folder, delete_file, split_mbox, mbox_to_csv
from drive.google_auth import get_drive_service
from drive.drive_upload import get_folder, upload_csv
from assistant.script import send_link_to_chatgpt

import os

def main(mbox_file):
    """Main function to run the script."""
    drive_service = get_drive_service()

    if drive_service is None:
        print("Failed to create Google Drive service.")
        return

    drive_folder = get_folder(drive_service, 'Email CSVs')
    if drive_folder is None:
        print("Failed to get or create Google Drive folder.")
        return

    try:
        #First check if there are MBOX  files to be processed
        mbox_folder = check_files_in_folder('mbox_output')
        if not mbox_folder:
            print('No files found in mbox_output, splitting MBOX file...')
            split_mbox(mbox_file, 'mbox_output', emails_per_file=1000)
            mbox_folder = check_files_in_folder('mbox_output')

        if mbox_folder:
            #Convert MBOX files to CSV
            #Process only the first file for testing
            file = mbox_folder[0]
            csv_folder = 'csv_output'
            os.makedirs(csv_folder, exist_ok=True)
            print(f"Processing MBOX file: {file}")
            mbox_file_path = os.path.join('mbox_output', file)
            csv_file_path = os.path.join(csv_folder, 'csv_1.csv')

            # Upload CSV to Google Drive and get the link
            csv_file = mbox_to_csv(mbox_file_path, csv_file_path)
            print(f"Uploading CSV file: {csv_file_path}")
            drive_link = upload_csv(drive_service, csv_file_path, drive_folder)

            # Send the link to ChatGPT for processing
            instructions_path = 'assistant/instructions.txt'
            response = send_link_to_chatgpt(drive_link, instructions_path)
            print(response)
            #FULL PRODUCTION CODE
#                 # for file in mbox_folder:
#                 #     csv_file = mbox_to_csv(file, f'csv_{file_count}.csv')
#                 #     csv_file_path = os.path.join(csv_folder, csv_file)
#                 #     upload_csv(drive_service, csv_file_path, drive_folder)
#                 #     file_count +=1
#                       print(f"Deleting processed files: mbox_output/{file}, {csv_file_path}")
#                 #     delete_file(f'mbox_output\{file}')
#                 #     delete_file(csv_file_path)
#             except Exception as e:
#                 print(f"An error occurred: {e}")

            
            # Optionally delete the processed files if needed

        else:
            print('No files found in mbox_output after splitting.')
    except Exception as e:
        print(f"An error occurred: {e}")
if __name__ == "__main__":
    main("email_help/Mail_2024_July.mbox")