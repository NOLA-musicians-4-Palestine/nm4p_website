import frontmatter
import os
import pytz
import yaml
from googleapiclient.http import MediaIoBaseDownload
from slugify import slugify
from datetime import datetime
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
# from googleapiclient.discovery import build
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_file(
    #"service-account-file.json",
    "token.json",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)

calendar_service = build("calendar", "v3", credentials=creds)

target_calendar_id = "0b3ffa27ffe7ad1f5e25331bfddc2f1b3352f7fad89712b24761041cdfa8fb3f@group.calendar.google.com"
events_result = calendar_service.events().list(calendarId=target_calendar_id).execute()
events = events_result.get("items", [])

for event in events:
    print(event["summary"])
