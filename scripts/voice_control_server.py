#!/usr/bin/env python
from flacrecord import listen_for_block_of_speech
from googlewebspeech import stt_google_wav
from witapi import witLookup
from responseprocess import messageResponse
from googletext2speech import googleTTS

from user_identification import client

from voice_control.srv import *
import rospy, time

def identify_user():
	waitingForUser = True

	while waitingForUser:
		print "looking for person"
		person_result = client.queryPerson()
		if person_result.is_person:
			print "found someone"
		else :
			print "no luck"
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
	finished = False
	while not finished:
		flac_file = listen_for_block_of_speech()
		hypothesis = stt_google_wav(flac_file)
		if not hypothesis == []:
			print hypothesis
			witResult = witLookup(hypothesis)
			if not witResult == []:
				responseString, finished = messageResponse(witResult)
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
	voice_control_server()
