import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import argparse
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def search_emails(service, query):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        print(f"Subject: {get_subject(msg)} {get_date(msg)}")
        print(f"From: {get_sender(msg)}")
        print(f"Snippet: {msg['snippet']}\n")

def get_date(msg):
    return datetime.fromtimestamp(int(msg["internalDate"]) / 1000).strftime("%A, %d. %B %Y %I:%M%p")

def get_subject(msg):
    return next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject')

def get_sender(msg):
    return next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'From')

def main():
    parser = argparse.ArgumentParser(description='Search Gmail and display results.')
    parser.add_argument('query', type=str, help='Search query for Gmail')
    args = parser.parse_args()

    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    search_emails(service, args.query)

if __name__ == '__main__':
    main()
