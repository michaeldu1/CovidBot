import credentials
import requests
from flask import Flask, request
import os 
from decouple import config
import json

CLIENT_ACCESS_TOKEN = config('CLIENT_ACCESS_TOKEN')
PAGE_ACCESS_TOKEN = config('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = config('VERIFY_TOKEN')

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

# Adds support for GET requests to our webhook
@app.route('/webhook',methods=['GET'])
def webhook_authorization():
		print(CLIENT_ACCESS_TOKEN)
		if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):     
				print("succefully verified")
				return request.args.get('hub.challenge', '')
		else:
				print("Wrong verification token!")
				return "Wrong validation token"

@app.route('/webhook', methods=['POST'])
def handle_message():
		'''
		Handle messages sent by facebook messenger to the applicaiton
		'''
				
		data = request.get_json()
		if data["object"] == "page":
				for entry in data["entry"]:
						for messaging_event in entry["messaging"]:
								if messaging_event.get("message"):  
										sender_id = messaging_event["sender"]["id"]        
										recipient_id = messaging_event["recipient"]["id"] 
										message_text = messaging_event["message"]["text"]  
										send_message_response(sender_id, message_text) 

		return "ok"


def send_message(sender_id, message_text):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": PAGE_ACCESS_TOKEN},

        headers={"Content-Type": "application/json"}, 

        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))


def send_message_response(sender_id, message_text):
		#######
		# TODO: send message text to sentiment analysis
		#######

		#######
		# TODO: Send message to wit ai
		#######

		######
		# TODO: Query database based on witai response
		######

		# Return message to messenger UI
    send_message(sender_id, "hello!")

if __name__ == "__main__":
		app.run(threaded=True, port=5000)