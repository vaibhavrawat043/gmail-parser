# Gmail Email Processing Script

## Description

This project is a standalone Python script that integrates with the Gmail API to fetch emails from your Inbox, store them in a SQLite3 database, and process them based on rules defined in a JSON file. The script can mark emails as read or move them to the "Social" or "Promotions" tabs.

## Requirements

- Python 3.x
- pip

## Installation

1. **Clone the repository** (if applicable):
    ```bash
    git clone https://github.com/vaibhavrawat043/gmail-parser.git
    cd email-parser
    ```

2. **Create a virtual environment (optional but recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Gmail API credentials**:
   - Go to the [Google API Console](https://console.developers.google.com/).
   - Create a new project and enable the Gmail API.
   - Create OAuth 2.0 credentials for a desktop application.
   - Download the credentials file and save it as `credentials.json` in the project directory.

## Usage

### Fetch Emails

To fetch emails and save them to the database:

```bash
python fetch_emails.py
```

### Process Emails

To process emails based on rules:

```bash
python fetch_emails.py
```
