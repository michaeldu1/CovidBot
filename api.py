import credentials
import requests
from flask import Flask, request
import os 
from decouple import config
import json
import pickle5 as pickle
import urllib.request
import speech_recognition as sr
import ffmpeg
from data_exploration import VaccinationsData
from data_exploration import USCountiesData
from user_info import UserInfo
from wit import Wit


CLIENT_ACCESS_TOKEN = config('CLIENT_ACCESS_TOKEN')
PAGE_ACCESS_TOKEN = config('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = config('VERIFY_TOKEN')
SERVER_ACCESS_TOKEN = config('SERVER_ACCESS_TOKEN')

app = Flask(__name__)
client = Win(SERVER_ACCESS_TOKEN)

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
		print("data is ",data)
		if data["object"] == "page":
				for entry in data["entry"]:
						for messaging_event in entry["messaging"]:
								if messaging_event.get("message"):  
										sender_id = messaging_event["sender"]["id"]        
										recipient_id = messaging_event["recipient"]["id"] 
										message_text = messaging_event["message"]
										if 'attachments' in message_text:
											if message_text['attachments'][0]['type'] == 'audio':
												video_url = message_text['attachments'][0]['payload']['url']
												print("video url is ", video_url)
												if os.path.exists('speech.mp4'):
													os.remove('speech.mp4') 
												saved = urllib.request.urlretrieve(video_url, 'speech.mp4') 
												print("saved is ", saved)
												speech_transcript = convert_audio_to_text()
												send_message_response(sender_id, speech_transcript)

										else:
											send_message_response(sender_id, message_text["text"]) 

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

def convert_audio_to_text():
	if os.path.exists('speech.mp3'):
		os.remove('speech.mp3') 
	if os.path.exists('speech.wav'):
		os.remove('speech.wav')
	command2mp3 = "ffmpeg -i speech.mp4 speech.mp3"
	command2wav = "ffmpeg -i speech.mp3 speech.wav"
	os.system(command2mp3)
	os.system(command2wav)

	r = sr.Recognizer()
	with sr.AudioFile('speech.wav') as source:
		audio = r.record(source, duration=120) 
	print("speech is ", r.recognize_google(audio))
	return r.recognize_google(audio)

def init_db(resp):
	vaccine_dataset = VaccinationsData()
	counties_dataset = USCountiesData('Harris', 'Texas')

	return {
		'userLocation': update_user_location(resp),
		'totalVaccinations': vaccine_dataset.get_total_vaccinations(),
	}

def update_user_location(resp):
	print('resp is ', resp)
	return 'Dallas, Texas'

def parse_response(resp):
	intent = resp['intents'][0]['name']
	db = init_db(resp)

	return db[intent]


def send_message_response(sender_id, message_text):
		#######
		# TODO: send message text to sentiment analysis
		#######

		#######
		#Send message to wit ai
		#######
		resp = client.message(message_text)

		# resp = {'text': 'Chicago, Illinois', 'intents': [{'id': '910709439678949', 'name': 'userLocation', 'confidence': 0.9945}], 'entities': {'wit$location:location': [{'id': '193227822570730', 'name': 'wit$location', 'role': 'location', 'start': 0, 'end': 17, 'body': 'Chicago, Illinois', 'confidence': 0.9408, 'entities': [], 'suggested': True, 'value': 'Chicago, Illinois', 'type': 'value'}]}, 'traits': {}}
		# resp = {'text': 'how many people have been vaccinated?', 'intents': [{'id': '880965962687968', 'name': 'totalVaccinations', 'confidence': 0.9983}], 'entities': {'wit$age_of_person:age_of_person': [{'id': '810205969703877', 'name': 'wit$age_of_person', 'role': 'age_of_person', 'start': 4, 'end': 37, 'body': 'many people have been vaccinated?', 'confidence': 0.8855, 'entities': [], 'suggested': True, 'value': 'many people have been vaccinated?', 'type': 'value'}]}, 'traits': {}}
		parse_response(resp)

		send_message(sender_id, f"Hello, you said: {message_text}")

if __name__ == "__main__":
	user_info = UserInfo()
	app.run(threaded=True, port=5000)