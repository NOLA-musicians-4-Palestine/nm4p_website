import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly",
]


def main():
    # Load the OAuth credentials file
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=42669)

    # Save the credentials for future use
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    print("Access token and refresh token generated.")


if __name__ == "__main__":
    main()
