import mailbox
import csv
import os
from bs4 import BeautifulSoup
from email.header import decode_header

def split_mbox(input_mbox, output_dir, emails_per_file=1000):
    '''Split large mbox file into smaller files, with 1000 emails each.'''
    # Open the original MBOX file
    mbox = mailbox.mbox(input_mbox)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    file_count = 0
    email_count = 0
    
    current_mbox = None
    
    for i, message in enumerate(mbox):
        if email_count % emails_per_file == 0:
            if current_mbox:
                current_mbox.close()
            file_count += 1
            current_mbox = mailbox.mbox(os.path.join(output_dir, f'part_{file_count}.mbox'))

        current_mbox.add(message)
        email_count += 1

    if current_mbox:
        current_mbox.close()  
    
    print(f'Split {email_count} emails into {file_count} files.')

def clean_html(html_content):
    '''Extract text from parts of email (subject, body, etc.)'''
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def get_charset(message, default="ascii"):
    '''Function to ID charset being used in emails.'''
    return message.get_content_charset() or default

def decode_header_field(field):
    '''Specifically for decoding the subject of an email'''
    try:
        decoded_header = decode_header(field)
        field = ''.join([str(t[0], t[1] or 'utf-8') if isinstance(t[0], bytes) else t[0] for t in decoded_header])
    except Exception as e:
        field = ''
    return field

def extract_body_from_message(message):
    '''Extracting the body from the email message.'''
    body = ''
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type in ['text/plain', 'text/html']:
                charset = get_charset(part)
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors='ignore')
                    if content_type == 'text/html':
                        body = clean_html(body)
                    break
    else:
        content_type = message.get_content_type()
        if content_type in ['text/plain', 'text/html']:
            charset = get_charset(message)
            payload = message.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors='ignore')
                if content_type == 'text/html':
                    body = clean_html(body)
    return body

def mbox_to_csv(mbox_file, csv_file):
    '''Convert individual mbox files to csv files.'''
    # Open the MBOX file
    mbox = mailbox.mbox(mbox_file)
    
    # Create a CSV file
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'From', 'To', 'Subject', 'Body', 'X-Gmail-Labels', 'List-Unsubscribe', 'Message-ID']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Extract email content and write to CSV
        message_count = 0
        for message in mbox:
            message_count += 1
            print(f"Processing message {message_count}")

            # Initialize fields
            body = extract_body_from_message(message)

            x_gmail_labels = message['X-Gmail-Labels']
            list_unsubscribe = message['List-Unsubscribe']
            message_id = message['Message-ID']

            # Decode and clean subject, from and to
            subject = message['Subject']
            recipient = message['To']
            sender = message['From']
            clean_subject = decode_header_field(subject)
            clean_recipient = decode_header_field(recipient)
            clean_sender = decode_header_field(sender)

            print(f"Writing message {message_count} to CSV")
            writer.writerow({
                'Date': message['date'],
                'From': clean_sender.strip(),
                'To': clean_recipient.strip(),
                'Subject': clean_subject.strip(),
                'Body': body,
                'X-Gmail-Labels': x_gmail_labels,
                'List-Unsubscribe': list_unsubscribe,
                'Message-ID': message_id
            })
    print(f"Processed {message_count} messages.")
    return csv_file

def check_files_in_folder(folder_path):
    """Check if there are any files in the specified local folder."""
    try:
        # List all items in the folder
        items = os.listdir(folder_path)
        # Filter out directories, leaving only files
        files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
        if not files:
            return []
        else:
            return files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def delete_file(file_path):
    """Delete the specified file."""
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' does not exist.")
    except PermissionError:
        print(f"Permission denied: unable to delete '{file_path}'.")
    except Exception as e:
        print(f"An error occurred while trying to delete '{file_path}': {e}")

# This block will only run if the script is executed directly
if __name__ == '__main__':
    folder_path = 'path/to/your/folder'  # Replace with your folder path
    check_files_in_folder(folder_path)
