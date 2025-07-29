import frontmatter
import os
import pytz
import yaml
import datetime
from googleapiclient.http import MediaIoBaseDownload
from slugify import slugify
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


def google_creds():
    return service_account.Credentials.from_service_account_file(
        "service-account-file.json",
        scopes=[
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
    )


def fetch_events(service):
    try:

        # this is the id of the calendar called "Solidarity Network"
        # could be a github environment variable
        target_calendar_id = "0b3ffa27ffe7ad1f5e25331bfddc2f1b3352f7fad89712b24761041cdfa8fb3f@group.calendar.google.com"

        # date bounds
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))
        one_month_from_now = now + datetime.timedelta(weeks=4)

        request = service.events().list(
            calendarId = target_calendar_id,
            singleEvents = True,
            timeMin = now.isoformat(),
            timeMax = one_month_from_now.isoformat()
        )

        events = []
        
        while request is not None:
            # make the request
            response = request.execute()

            # collect the items
            events = events + response.get("items", [])

            # prepare a new request (it'll be null if there are no more)
            request = service.events().list_next(request, response)

        # Check if any events are found
        if not events:
            print("No upcoming events found.")
            return []

        # Print the events
        for event in events:
            start = event["start"].get(
                "dateTime",
                event["start"].get("date")
            )
            print(f"{event['summary']}")
            print("event[start]:")
            print(vars(event["start"]))

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")


def fetch_drive_attachment(attachment, service):
    def destination_filename(attachment):
        extension = f".{attachment['mimeType'].split('/')[-1]}"
        return slugify(attachment["title"].split(extension)[0]) + extension

    file_name = destination_filename(attachment)
    file_path = f"assets/images/event_flyers/{file_name}"

    with open(file_path, "wb") as file:
        request = service.files().get_media(fileId=attachment["fileId"])
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress()) * 100}%")

        print(f"Downloaded {file_name} to {file_path}")
    return file_name


def get_first_image_attachment(event, service):
    attachments = event.get("attachments", [])

    if not attachments:
        print(f"No attachments found for event {event['summary']}.")
        return None

    # Loop through attachments and find the first image
    for attachment in attachments:
        mime_type = attachment.get("mimeType", "")

        # Check if it's an image attachment (based on MIME type)
        if mime_type.startswith("image/"):
            print(f"Found image attachment: {attachment['title']}")
            return fetch_drive_attachment(attachment, service)


def read_event_template(path):
    with open(path) as fh:
        post = frontmatter.load(fh)
    return post


def get_day_from_event(event): #returns datetime.date.isoformat() always
    start = event["start"]
    return start.get( # get the day as a date
        "date",
        start.get(
            "datetime",
            datetime.datetime(1970, 1, 1)
        ).date()
    ).isoformat()

def get_start_time_from_event(event): #returns a datetime.time.strftime(...) or None
    if not "datetime" in event["start"]:
        return None

    return event["start"]["datetime"].time().strftime("%I:%M%p")

def get_end_time_from_event(event): #returns a datetime.time.strftime(...) or None
    if not "datetime" in event["start"]:
        return None

    return event["end"]["datetime"].time().strftime("%I:%M%p")
    

def event_as_post(event, drive_service):
    is_all_day_event = "date" in event["start"]

    day = get_day_from_event(event)
    start_time = get_start_time_from_event(event)
    end_time = get_end_time_from_event(event)

    post = read_event_template("_events/no-more.md")

    post.metadata["title"] = event["summary"]
    post.metadata["date"] = day
    post.metadata["flyer"] = get_first_image_attachment(event, drive_service)

    if not is_all_day_event:
        post.metadata["time"] = f"{start_time} - {end_time}"

    if "location" in event:
        post.metadata["location"] = event["location"]

    post.content = event.get("description", event["summary"])

    return post


def run():
    creds = google_creds()
    calendar_service = build("calendar", "v3", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    events = fetch_events(calendar_service)

    posts = [event_as_post(event, drive_service) for event in events]
    for post in posts:
        if post.metadata["flyer"]:
            post_path = f"./_events/{post.metadata['date']}-{slugify(post.metadata['title'])}.html"
            with open(post_path, "w") as f:
                f.write(frontmatter.dumps(post))
                f.write(f"post path: {post_path}")


# Example usage
if __name__ == "__main__":
    print("yee, and I cannot stress this enough, haw")
    run()
