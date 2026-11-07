from flask import Flask, request, jsonify
from pathlib import Path
import os
import json
import requests

# creds for api calls
username = "nomis"
password = Path("/run/secrets/nc_app_password").read_text().strip()

# for deciding what to do with each form submission
form_id_to_type = {
	4: "event_submission"
}

app = Flask(__name__)

@app.post("/row_updated")
def row_updated():
	payload = request.get_json(force=True)
	print(json.dumps(payload, indent=2))

	return "row updated hook received\n"

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
		
		print(form_responses)


		form_type = form_id_to_type[form_id]
		
		return {"form_type": form_type, "responses": form_responses}
	


	def add_event_to_approval_table(form_responses):

		# create row in events approval table
		approval_table_column_ids = {
			"event_name": 175,
			"flyer": 181,
			"date": 177,
			"location": 179,
			"details": 180,
			"approved": 178
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
				approval_table_column_ids["location"]: form_responses["location"]["text"],
				approval_table_column_ids["details"]: form_responses["details"]["text"],
				approval_table_column_ids["flyer"]: f"https://cloud.nm4p.net/f/{form_responses["flyer"]["fileId"]}"
			}})
		)

		create_row_response.raise_for_status()
		create_row_data = create_row_response.json()

		print("created row")
		print(json.dumps(create_row_data, indent=2))



	submission = process_submission()

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



