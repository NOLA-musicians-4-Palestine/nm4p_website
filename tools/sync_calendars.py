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
        "tools/service-account-file.json",
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
            print(event.get("summary", "Untitled event"))

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")


def fetch_band_events(service):
    try:

        # this is the id of the band calendar
        # could be a github environment variable
        band_calendar_id = "placeholder band calendar id"

        # date bounds (same 4 week window as solidarity events)
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5)))
        one_month_from_now = now + datetime.timedelta(weeks=4)

        request = service.events().list(
            calendarId = band_calendar_id,
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
            print("No upcoming band events found.")
            return []

        # Print the events
        for event in events:
            print(f"Band event: {event.get('summary', 'Untitled event')}")

        return events

    except HttpError as error:
        print(f"An error occurred fetching band events: {error}")


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
        print(f"No attachments found for event {event.get('summary', 'Untitled event')}.")
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


def get_day_from_event(event): #returns datetime.date always
    start = event["start"]
    day_str = ""

    if "date" in start:
        day_str = start["date"]
    elif "dateTime" in start:
        day_str = start["dateTime"].split('T')[0]

    return datetime.date.fromisoformat(day_str)

def get_start_time_from_event(event): #returns a datetime.time.strftime(...) or None
    if not "dateTime" in event["start"]:
        return None

    return datetime.datetime.fromisoformat(event["start"]["dateTime"]).time().strftime("%I:%M%p")

def get_end_time_from_event(event): #returns a datetime.time.strftime(...) or None
    if not "dateTime" in event["start"]:
        return None

    return datetime.datetime.fromisoformat(event["end"]["dateTime"]).time().strftime("%I:%M%p")
    

def event_as_post(event, drive_service):
    is_all_day_event = "date" in event["start"]

    day = get_day_from_event(event)
    start_time = get_start_time_from_event(event)
    end_time = get_end_time_from_event(event)

    post = read_event_template("_events/no-more.md")

    post.metadata["title"] = event.get("summary", "Untitled event")
    post.metadata["date"] = day.isoformat()
    post.metadata["flyer"] = get_first_image_attachment(event, drive_service)

    if not is_all_day_event:
        post.metadata["time"] = f"{start_time} - {end_time}"

    if "location" in event:
        post.metadata["location"] = event["location"]

    post.content = event.get("description", event.get("summary", "Untitled event"))

    return post


def generate_band_events_include(events):
    """Generate HTML include file for band events"""
    if not events:
        html = "<p>No upcoming rehearsals or shows scheduled.</p>\n"
    else:
        html = "<ul class=\"band-events\">\n"
        for event in events:
            is_all_day_event = "date" in event["start"]
            day = get_day_from_event(event)
            start_time = get_start_time_from_event(event)
            end_time = get_end_time_from_event(event)

            html += "  <li class=\"band-event\">\n"
            html += f"    <strong>{event.get('summary', 'Untitled event')}</strong><br>\n"

            # date and time
            date_formatted = day.strftime("%A, %B %d, %Y")
            if is_all_day_event:
                html += f"    {date_formatted}<br>\n"
            else:
                html += f"    {date_formatted}, {start_time} - {end_time}<br>\n"

            # location
            if "location" in event:
                html += f"    {event['location']}<br>\n"

            # description
            description = event.get("description", "")
            if description:
                html += f"    <span class=\"event-description\">{description}</span><br>\n"

            html += "  </li>\n"
        html += "</ul>\n"

    # write to include file
    with open("_includes/band_events.html", "w") as f:
        f.write(html)

    print(f"Generated _includes/band_events.html with {len(events)} events")


def run():
    creds = google_creds()
    calendar_service = build("calendar", "v3", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # sync solidarity network events
    events = fetch_events(calendar_service)
    posts = [event_as_post(event, drive_service) for event in events]
    for post in posts:
        post_path = f"./_events/{post.metadata['date']}-{slugify(post.metadata['title'])}.html"
        with open(post_path, "w") as f:
            f.write(frontmatter.dumps(post))

    # sync band events
    band_events = fetch_band_events(calendar_service)
    generate_band_events_include(band_events)


# Example usage
if __name__ == "__main__":
    run()
