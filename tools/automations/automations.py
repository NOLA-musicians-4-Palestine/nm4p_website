from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.post("/form_submitted")
def form_submitted():
	print("form submission recieved")
	payload = request.get_json(force=True)
	print(json.dumps(payload, indent=2))

	# Event Submission form:
	# - [ ] get submission
	# - [ ] format data/get flyer url/get question names
	# - [ ] create row in events approval table
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



