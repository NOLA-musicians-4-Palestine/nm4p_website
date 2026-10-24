from flask import Flask, request

app = Flask(__name__)

@app.post("/")
def form_submitted():
	print("Webhook Recieved")
	return "<p>Webhook Recieved</p>"

app.run(host="0.0.0.0", port=8080)



