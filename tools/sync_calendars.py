import frontmatter
import os
import pytz
import yaml
import datetime
import requests
from pathlib import PurePosixPath
from caldav import get_davclient
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
            print(event["summary"])

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

    post.metadata["title"] = event["summary"]
    post.metadata["date"] = day.isoformat()
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
        post_path = f"./_events/{post.metadata['date']}-{slugify(post.metadata['title'])}.html"
        with open(post_path, "w") as f:
            f.write(frontmatter.dumps(post))

def get_flyer(attachment_params):
	# download the attachment

	## use the ID to make a WebDAV request for a direct download link
	file_id = attachment_params["X-NC-FILE-ID"]

	url = "https://cloud.nm4p.net/ocs/v2.php/apps/dav/api/v1/direct"

	response = requests.post(
		url,
		auth = (os.getenv("CALDAV_USERNAME"), os.getenv("CALDAV_PASSWORD")),
		headers = {
				"Accept": "application/json",
				"OCS-APIRequest": "true",
			},
			json={
				"fileId": file_id,
				"expirationTime": 300,
			},
			timeout=30,
		)

	response.raise_for_status()
	result = response.json()

	direct_link = result["ocs"]["data"]["url"]

	## construct the name and path to save the file
	extension = f".{attachment_params['FMTTYPE'].split('/')[-1]}"
	filename = slugify(PurePosixPath(attachment_params["FILENAME"]).stem) + extension
	file_path = f"assets/images/event_flyers/{filename}"

	## download the file

	with requests.get(direct_link, stream=True, timeout=60) as response:
		response.raise_for_status()

		with open(file_path, "wb") as f:
			for chunk in response.iter_content(chunk_size=1024 * 1024):
				if chunk:
					f.write(chunk)

	return filename

def create_post_from_event(event):
	start = event.decoded("dtstart")
	end = event.decoded("dtend")

	day = start.date() if isinstance(start, datetime.datetime) else start
	is_all_day = isinstance(start, datetime.date) and not isinstance(start, datetime.datetime)

	post = read_event_template("_events/no-more.md")

	post.metadata["title"] = event.decoded("summary")
	post.metadata["date"] = day.isoformat()

	if event.get("attach") is not None:
		# if it's a list get the first one
		attachment_params = event.get("attach")[0].params if isinstance(event.get("attach"), list) else event.get("attach").params
		post.metadata["flyer"] = get_flyer(attachment_params)
	else:
		post.metadata["flyer"] = ""


	if not is_all_day:
		post.metadata["time"] = f"{start.time()} - {end.time()}"

	if "location" in event:
		post.metadata["location"] = event.decoded("location")

	post.content = event.decoded("description")
	return post


def nextcloud_run():
	print("Nextcloud Run")

	print("do the environment variables exist?")
	for name in ("CALDAV_URL", "CALDAV_USERNAME", "CALDAV_PASSWORD"):
		print(f"{name} set: {bool(os.getenv(name))}")

	with get_davclient() as client:
		print("Connecting to NM4P Cloud Server")

		solidarity_network_calendar = client.calendar(url="https://cloud.nm4p.net/remote.php/dav/calendars/nomis/solidarity-network/")

		# Search for events
		events = solidarity_network_calendar.search(
			start=datetime.datetime.now(),
			end=datetime.datetime.now() + datetime.timedelta(weeks=6),
			event=True,
			expand=True,
		)
		print(f"Found {len(events)} events in the next 6 weeks")

		posts = [create_post_from_event(event.component) for event in events]
		print(posts)
		for post in posts:
			print(post)
			post_path = f"./_events/{post.metadata['date']}-{slugify(post.metadata['title'])}.html"
			print(post_path)
			with open(post_path, "w") as f:
				f.write(frontmatter.dumps(post))


if __name__ == "__main__":
	nextcloud_run()
    #run()
