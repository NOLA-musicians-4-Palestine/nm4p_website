from google.oauth2 import service_account
from googleapiclient.discovery import build

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
