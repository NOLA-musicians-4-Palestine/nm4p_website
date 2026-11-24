from flask import Flask, request, jsonify
from pathlib import Path
from caldav import get_davclient
import os
import json
import requests
import datetime
from zoneinfo import ZoneInfo


# creds for api calls
username = "nomis"
password = Path("/run/secrets/nc_app_password").read_text().strip()

# for deciding what to do with each form submission
form_id_to_type = {
	4: "event_submission"
}

app = Flask(__name__)

@app.post("/approval_table_updated")
def approval_table_updated():
	payload = request.get_json(force=True)
	print("row updated payload:")
	print(json.dumps(payload, indent=2))
	# payload is the old event and new event
	# use that to format an event_info object that only has the information needed for creating an event

	# ignore events that aren't now approved
	approved = payload["event"]["dataByAlias"]["approved"]["value"] == "true"
	if(not approved): 
		print("event not approved")
		return "Event was not approved\n"

	# reject if it was already approved, that means some other field was changed, and we don't want to make duplicates
	approved_column_id = payload["event"]["dataByAlias"]["approved"]["columnId"]
	previous_values_array = payload["event"]["previousValues"] # that's an array of objects {columnId, value}

	previously_approved = False
	for a in previous_values_array:
		if a["columnId"] == approved_column_id:
			previously_approved = a["value"] == "true"
	
	if(previously_approved):
		print("event already approved")
		print(previously_approved)
		return "Event was previously approved\n"
	
	# format the info for creating a calendar event
	event_info = {}
	for key, val in payload["event"]["dataByAlias"].items():
		event_info[key] = val["value"]

	def create_calendar_event(event_info):
		with get_davclient(
			url = "http://nextcloud-aio-apache:8000/remote.php/dav/",
			username = username,
			password = password
		) as client:
			solidarity_network_calendar = client.calendar(url="http://nextcloud-aio-apache:8000/remote.php/dav/calendars/nomis/solidarity-network/")

			print("Saving an event")

			new_orleans_tz = ZoneInfo("America/Chicago")

			dstart = datetime.date.fromisoformat(event_info["date"])
			tstart = datetime.time.fromisoformat(event_info["time"])
			dtstart = datetime.datetime.combine(dstart, tstart, tzinfo=new_orleans_tz)
			print(dstart, tstart, dtstart)

			new_event = solidarity_network_calendar.add_event(
				# title
				summary = event_info["event_name"],
				# where
				location = event_info["location"],
				# when
				dtstart = dtstart,
				dtend = dtstart + datetime.timedelta(hours=1), # default to one hour event length
				# description
				description = event_info["details"],
			)

			print("Saved an event")

			# attachment
			with new_event.edit_icalendar_component() as component:
				component.add(
					"ATTACH",
					f"/index.php/f/{event_info['flyer_file_id']}",
					parameters={
						"VALUE": "URI",
						"FILENAME": "flyer",
						"X-NC-FILE-ID": event_info['flyer_file_id'],
					},
				)


			new_event.save()

			print(new_event.data)
	
	create_calendar_event(event_info)

	return "approval table updated hook received\n"

@app.post("/form_submitted")
def form_submitted():

	def process_submission():
		print("form submission recieved")

		# recieve the form submitted hook
		payload = request.get_json(force=True)
		print(json.dumps(payload, indent=2))

		form_id = payload["event"]["form"]["id"]
		submission_id = payload["event"]["submission"]["id"]

		# get the submissions
		print("getting submission")
		submission_response = requests.get(
			f"http://nextcloud-aio-apache:8000/ocs/v2.php/apps/forms/api/v3/forms/{form_id}/submissions/{submission_id}",
			auth=(username, password),
			headers={"OCS-APIRequest": "true", "Accept": "application/json"},
			timeout=15,
		)
		print("got submission")

		submission_response.raise_for_status()
		submission = submission_response.json()

		print(json.dumps(submission, indent=2))

		# get the questions
		print("getting questsion")
		questions_response = requests.get(
			f"http://nextcloud-aio-apache:8000/ocs/v2.php/apps/forms/api/v3/forms/{form_id}/questions",
			auth=(username, password),
			headers={"OCS-APIRequest": "true", "Accept": "application/json"},
			timeout=15,
		)
		print("got questsions")

		questions_response.raise_for_status()
		questions = questions_response.json()

		print(json.dumps(questions, indent=2))

		# collect questions and answers {"question_name": answer_obj}
		form_responses = {};
		for answer in submission["ocs"]["data"]["answers"]:
			question_obj = next(q for q in questions["ocs"]["data"] if q["id"] == answer["questionId"])

			answer["question"] = question_obj # store the question with the answer for later
			form_responses[question_obj["name"]] = answer
		
		print("collected form responses:")
		print(json.dumps(form_responses, indent=2))

		form_type = form_id_to_type[form_id]
		
		return {"form_type": form_type, "responses": form_responses}
	
	def add_event_to_approval_table(form_responses):
		# create row in events approval table
		approval_table_column_ids = {
			"event_name": 175,
			"flyer": 181,
			"date": 177,
			"time": 182,
			"location": 179,
			"details": 180,
			"approved": 178,
			"flyer_file_id": 183,
		}

		print("creating row")
		create_row_response = requests.post(
			"http://nextcloud-aio-apache:8000/ocs/v2.php/apps/tables/api/2/tables/29/rows",
			auth = (username, password),
			headers = {"OCS-APIRequest": "true", "Content-Type": "application/json", "Accept": "application/json"},
			timeout = 15,
			data = json.dumps({'data': {
				approval_table_column_ids["event_name"]: form_responses["event_name"]["text"],
				approval_table_column_ids["date"]: form_responses["date"]["text"],
				approval_table_column_ids["time"]: form_responses["time"]["text"],
				approval_table_column_ids["location"]: form_responses["location"]["text"],
				approval_table_column_ids["details"]: form_responses["details"]["text"],
				approval_table_column_ids["flyer"]: f"https://cloud.nm4p.net/f/{form_responses["flyer"]["fileId"]}",
				approval_table_column_ids["flyer_file_id"]: form_responses["flyer"]["fileId"],
			}})
		)

		create_row_response.raise_for_status()
		create_row_data = create_row_response.json()

		print("created row")
		print(json.dumps(create_row_data, indent=2))


	submission = process_submission()
	# submission is an object: {"form_type": form_type, "responses": form_responses}

	if submission["form_type"] == "event_submission":
		add_event_to_approval_table(submission["responses"])

	

	# - [x] get submission
	# - [x] format data
	# - [x] get flyer url
	# - [x] get question names
	# - [x] create row in events approval table

	# - [ ] later make a webhook for when things are marked approved from that table

	# Krewe of Zeitoun Membership Form
	# - create row in Zeitoun Members table
	# - email loomio with form content

	# Hanoun Brass Band Booking Form
	# - email loomio with form content

	# Solidarity Statement
	# - create row in solidarity statement signatories table

	return "form submission received\n"

app.run(host="0.0.0.0", port=8080)



