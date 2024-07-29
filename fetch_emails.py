import os
import json
import sqlite3
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Authenticate and create a Gmail API service instance."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_emails(service):
    """Fetch emails from Gmail."""
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='').execute()
    messages = results.get('messages', [])
    email_data = []
    for message in messages[:10]:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        headers = {header['name']: header['value'] for header in msg['payload']['headers']}
        email_data.append({
            'id': msg['id'],
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', ''),
            'snippet': msg.get('snippet', ''),
            'date_received': headers.get('Date', ''),
            'payload': json.dumps(msg.get('payload', {}))
        })
    return email_data

def save_emails_to_db(email_data):
    """Save emails to the SQLite database."""
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY, 
                  from_address TEXT, 
                  to_address TEXT, 
                  subject TEXT, 
                  snippet TEXT, 
                  date_received TEXT, 
                  payload TEXT)''')
    for email in email_data:
        c.execute('''INSERT OR REPLACE INTO emails 
                     (id, from_address, to_address, subject, snippet, date_received, payload) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                  (email['id'], email['from'], email['to'], email['subject'], email['snippet'], email['date_received'], email['payload']))
    conn.commit()
    conn.close()

def main():
    service = authenticate_gmail()
    emails = fetch_emails(service)
    save_emails_to_db(emails)

if __name__ == '__main__':
    main()
