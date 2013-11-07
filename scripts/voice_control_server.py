#!/usr/bin/env python
from flacrecord import listen_for_block_of_speech
from googlewebspeech import stt_google_wav
from witapi import witLookup
from responseprocess import messageResponse
from googletext2speech import googleTTS
from googletext2speech import play_wav

from user_identification import client

from voice_control.srv import *
import rospy, time, os, baristaDB

DB_NAME = "baristaDB.db"
CONFIDENCE_THRESHOLD = 40

def identify_user():
	waitingForUser = True

	while waitingForUser:
		print "looking for person"
		global userID

		person_result = client.queryPerson()
		if person_result.is_person:
			if person_result.is_known_person and person_result.confidence > CONFIDENCE_THRESHOLD:
				userID = person_result.id
				client.definePerson(userID)
			else:
				baristaDB.OpenDatabase(DB_NAME)
				userID = baristaDB.CreateNewUser()
				baristaDB.CloseDatabase(DB_NAME)
				client.definePerson(userID)
		
		waitingForUser = not person_result.is_person

	return (person_result.is_person, person_result.is_known_person, person_result.id, person_result.confidence)

def define_new_user():
	global userCount
	success = client.definePerson(userCount)
	userCount += 1
	if success:
		print "Success!"
	else :
		print "Sad face"
	return success

def begin_interaction():
	global finished
	finished = False
	while not finished:
		flac_file = listen_for_block_of_speech()
		hypothesis = stt_google_wav(flac_file)
		if not hypothesis == []:
			print hypothesis
			if hypothesis.lower() == "what does the fox say":
				play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/fox.wav'))
			else :
				witResult = witLookup(hypothesis)
				if not witResult == []:
					global userID
					responseString, finished = messageResponse(witResult, userID)
				else:
					responseString = "I'm sorry, I didnt understand what you said"
		else:
			responseString = "I'm sorry, I didn't hear you"
		googleTTS(responseString)

def users_found(self):
	foundPerson = False
	while not foundPerson:
		is_person, known_person, user_id, confidence = identify_user()

		if is_person:
			foundPerson = True

			if known_person:
				print "Known %d %.3f" % (user_id, confidence)

			if not known_person or (confidence < 0.3):
				print "added someone new!"
				define_new_user()

	print "Beginning Interaction"

	begin_interaction()
 
	return known_person


def voice_control_server():
	interacting = False
	global userCount
	userCount = 1

	rospy.init_node('voice_control')
	rospy.Service('voice_control', voice_control, users_found)

	rospy.spin()

	#while(True):
	#	if not interacting:
	#		googletext2speech.googleTTS('Hello! Get your coffee here!')
	#		time.sleep(5)

if __name__ == "__main__":
	global userID
	userID = 0
	voice_control_server()
