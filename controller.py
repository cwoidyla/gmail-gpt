import os
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import openai
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64decode
from email import policy
from email.parser import BytesParser
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup

# 1. Login to Gmail API
def gmail_login():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# 2. Fetch and Preprocess Gmail Data
def fetch_and_preprocess(gmail):
    try:
        after = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        timestamp = int(time.mktime(datetime.strptime(after, "%Y/%m/%d").timetuple()))
        query = f'after:{timestamp}'

        # Get emails from the last 30 days
        results = gmail.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        gmail_data = []
        for message in messages:
            msg = gmail.users().messages().get(userId='me', id=message['id'], format='raw').execute()
            msg_str = urlsafe_b64decode(msg['raw']).decode()
            mime_msg = BytesParser(policy=policy.default).parsebytes(msg_str.encode())

            # Looking for 'text/plain' or 'text/html' part in the email.
            if mime_msg.is_multipart():
                for part in mime_msg.walk():
                    if part.get_content_type() in ['text/plain', 'text/html']:
                        body = part.get_content()
                        soup = BeautifulSoup(body, 'html.parser')
                        body = soup.get_text().strip()
                        break
            else:
                body = mime_msg.get_content()
                soup = BeautifulSoup(body, 'html.parser')
                body = soup.get_text().strip()
            
            # If the content type is 'text/html', convert to 'text/plain'
            if part.get_content_type() == 'text/html':
                soup = BeautifulSoup(body, 'html.parser')
                body = soup.get_text().strip()

            data = {
                'subject': mime_msg['subject'],
                'from': mime_msg['from'],
                'to': mime_msg['to'],
                'date': mime_msg['date'],
                'body': body
            }

            gmail_data.append(data)

        return gmail_data

    except HttpError as error:
        print(f'An error occurred: {error}')

# 3. Use GPT-4 to process data
def process_with_gpt4(gmail_data):
    # Logic to process the Gmail data with GPT-4 goes here.
    print("in process_with_gpt4()")
    pass

# 4. Rank Emails
def rank_emails(processed_data):
    # Logic to rank emails based on the processed data goes here.
    print("in rank_emails()")
    pass

def main():
    gmail = gmail_login()
    gmail_data = fetch_and_preprocess(gmail)
    print(gmail_data)
    processed_data = process_with_gpt4(gmail_data)
    ranked_emails = rank_emails(processed_data)

if __name__ == "__main__":
    main()

