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
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

CLIENT_ACCESS_TOKEN = config('CLIENT_ACCESS_TOKEN')
PAGE_ACCESS_TOKEN = config('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = config('VERIFY_TOKEN')
SERVER_ACCESS_TOKEN = config('SERVER_ACCESS_TOKEN')
IBM_ACCESS_TOKEN = config('IBM_ACCESS_TOKEN')
IBM_URL = config('IBM_URL')

app = Flask(__name__)
client = Wit(SERVER_ACCESS_TOKEN)
authenticator = IAMAuthenticator(IBM_ACCESS_TOKEN)
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)
tone_analyzer.set_service_url(IBM_URL)

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
	location = resp['entities']['wit$location:location'][0]['value']
	print("location is ", location)
	location = location.split(',')
	if len(location) > 1:
		county, state = location
		user_info.update_user(county=county, state=state)
	else:
		county = location[0]
		user_info.update_user(county=county)
	
def update_user_age_sex(resp):
	age = resp['entities']['wit$number:number'][0]['value']
	sex = resp['entities']['sex:sex'][0]['value']

	user_info.update_user(age=age, sex=sex)

def parse_response(sender_id, resp):
	vaccine_dataset = VaccinationsData()
	counties_dataset = USCountiesData('Harris', 'Texas')

	if len(resp['intents']) > 0:
		intent = resp['intents'][0]['name']
		print("the intent is ", intent)
		print(intent == 'userLocation', intent is 'userLocation')
		if intent == 'userLocation':
			update_user_location(resp)
			send_message(sender_id, f"Thanks, one more question. What is your age and sex?")
		elif intent == 'getAgeSex':
			update_user_age_sex(resp)
			send_message(sender_id, f"Awesome thanks! What Covid-19 case and vaccine related questions can I help you with today?")
		elif intent == 'totalVaccinations':
			vaccinations = int(vaccine_dataset.get_total_vaccinations())
			vaccinations = "{:,}".format(vaccinations)

			send_message(sender_id, f"Currently, there have been {vaccinations} total vaccinations in the US")
		elif intent == 'totalCases':
			cumulative_cases = counties_dataset.get_cumulative_cases()
			cumulative_cases = "{:,}".format(cumulative_cases)
			daily_cases = counties_dataset.get_daily_cases()
			daily_cases = "{:,}".format(daily_cases)

			send_message(sender_id, f"In the US there are 3.62M total cases. In your area, there have been {cumulative_cases} total cases and {daily_cases} cases per day.")
		elif intent == 'precautions':
			# Insert hardcoded precautions here 
			send_message(sender_id, f"precautions")
		elif intent == 'symptoms':
			# Insert hardcoded symptoms here 
			send_message(sender_id, f"symptoms")
		elif intent == 'finishCat':
			# Insert hardcoded precautions here 
			send_message(sender_id, f"Thanks so much for chatting today! I hope I could've been of some help. To help us out, it'd be great to know how helpful this was on a scale of 1-5!")
		else:
			db = init_db(resp)
			return db[intent]
	else:
		send_message(sender_id, f"Hello, thanks for reaching out! To get started, this experience will be much better if I can get some information from you. What county and state are you currently in right now?")



def send_message_response(sender_id, message_text):
		tone_analysis = tone_analyzer.tone(
		    {'text': message_text},
		    content_type='application/json',
		    sentences = False
		).get_result()

		#######
		#Send message to wit ai
		#######
		resp = client.message(message_text)
		print("Resp is ", resp)

		# resp = {'text': 'Chicago, Illinois', 'intents': [{'id': '910709439678949', 'name': 'userLocation', 'confidence': 0.9945}], 'entities': {'wit$location:location': [{'id': '193227822570730', 'name': 'wit$location', 'role': 'location', 'start': 0, 'end': 17, 'body': 'Chicago, Illinois', 'confidence': 0.9408, 'entities': [], 'suggested': True, 'value': 'Chicago, Illinois', 'type': 'value'}]}, 'traits': {}}
		# resp = {'text': 'how many people have been vaccinated?', 'intents': [{'id': '880965962687968', 'name': 'totalVaccinations', 'confidence': 0.9983}], 'entities': {'wit$age_of_person:age_of_person': [{'id': '810205969703877', 'name': 'wit$age_of_person', 'role': 'age_of_person', 'start': 4, 'end': 37, 'body': 'many people have been vaccinated?', 'confidence': 0.8855, 'entities': [], 'suggested': True, 'value': 'many people have been vaccinated?', 'type': 'value'}]}, 'traits': {}}
		parse_response(sender_id, resp)

		# send_message(sender_id, f"Hello, you said: {message_text}")

if __name__ == "__main__":
	user_info = UserInfo()
	app.run(threaded=True, port=5000)