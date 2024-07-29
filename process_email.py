import sqlite3
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

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

def load_rules():
    """Load rules from the JSON file."""
    with open('rules.json') as f:
        return json.load(f)

def matches_rule(email, rule):
    """Check if an email matches the given rule."""
    conditions = rule['conditions']
    predicate = rule['predicate']
    for condition in conditions:
        field = condition['field']
        pred = condition['predicate']
        value = condition['value']
        email_field_value = email.get(field.lower(), '')
        if field == 'Received Date/Time':
            email_date = datetime.strptime(email_field_value, '%a, %d %b %Y %H:%M:%S %z')
            value_date = datetime.strptime(value, '%Y-%m-%d')
            if pred == 'Less than' and not (email_date < value_date):
                return False
            if pred == 'Greater than' and not (email_date > value_date):
                return False
        else:
            if pred == 'Contains' and value not in email_field_value:
                return False
            if pred == 'Does not contain' and value in email_field_value:
                return False
            if pred == 'Equals' and email_field_value != value:
                return False
            if pred == 'Does not equal' and email_field_value == value:
                return False
    if predicate == 'All':
        return True
    elif predicate == 'Any':
        return any([
            condition['predicate'] in email.get(condition['field'], '')
            for condition in conditions
        ])
    return False

def mark_as_read(service, email_id):
    """Mark an email as read."""
    service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()

def move_to_label(service, email_id, label_id):
    """Move an email to a specific label."""
    service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label_id]}).execute()

def process_emails(service):
    """Process and perform actions on emails based on rules."""
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    rules = load_rules()
    c.execute('SELECT * FROM emails')
    emails = c.fetchall()
    for email in emails:
        email_data = {
            'id': email[0],
            'from': email[1],
            'to': email[2],
            'subject': email[3],
            'snippet': email[4],
            'date_received': email[5],
            'payload': json.loads(email[6])
        }
        for rule in rules:
            if matches_rule(email_data, rule):
                print(f'Processing email {email_data["id"]} based on rule: {rule}')
                for action in rule['actions']:
                    if action['action'] == 'Mark as read':
                        mark_as_read(service, email_data['id'])
                    elif action['action'] == 'Move Message':
                        move_to_label(service, email_data['id'], action['label_id'])
    conn.close()

def main():
    service = authenticate_gmail()
    process_emails(service)

if __name__ == '__main__':
    main()
