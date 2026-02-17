import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for reading, sending, and modifying emails
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def main():
    creds = None
    # The file gmail_credentials.json stores the user's access and refresh tokens
    if os.path.exists('gmail_credentials.json'):
        creds = Credentials.from_authorized_user_file('gmail_credentials.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found.")
                print("1. Go to Google Cloud Console > APIs & Services > Credentials")
                print("2. Create Credentials > OAuth Client ID > Desktop App")
                print("3. Download JSON and save as 'credentials.json' in this directory")
                print("4. IMPORTANT: Ensure your email is added to 'Test Users' in OAuth Consent Screen")
                return

            print("Launching browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        print("Saving gmail_credentials.json...")
        with open('gmail_credentials.json', 'w') as token:
            token.write(creds.to_json())
            
    print("Authentication successful!")
    
    # Post-processing: Ensure client_id and client_secret are in gmail_credentials.json
    # This is required for the Node.js MCP server compatibility
    with open('gmail_credentials.json', 'r') as f:
        token_data = json.load(f)
    
    needs_update = False
    if 'client_secret' not in token_data or 'client_id' not in token_data:
        print("Adding client metadata to gmail_credentials.json for MCP compatibility...")
        try:
            with open('credentials.json', 'r') as f:
                client_data = json.load(f)
                # Client data is usually nested under 'installed' or 'web'
                key = 'installed' if 'installed' in client_data else 'web'
                if key in client_data:
                    token_data['client_id'] = client_data[key].get('client_id')
                    token_data['client_secret'] = client_data[key].get('client_secret')
                    needs_update = True
        except Exception as e:
            print(f"Warning: Could not merge client secrets: {e}")

    if needs_update:
        with open('gmail_credentials.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        print("Updated gmail_credentials.json with client secrets.")

    print(f"Setup complete! Path to credentials: {os.path.abspath('gmail_credentials.json')}")
    print("ELYX is now authorized to use this email.")

if __name__ == '__main__':
    main()
