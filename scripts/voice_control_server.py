#!/usr/bin/env python
from flacrecord import listen_for_block_of_speech
from googlewebspeech import stt_google_wav
from witapi import witLookup
from responseprocess import messageResponse
from googletext2speech import googleTTS
from googletext2speech import play_wav

from user_identification import client as UID_client
import user_identification
import flacrecord
import responseprocess

from std_msgs.msg import String
import std_srvs.srv

from voice_control.srv import *
import rospy, time, os, baristaDB

DB_NAME = "baristaDB.db"
CONFIDENCE_THRESHOLD = 40

def sayCallback(data):
	googleTTS(data.data)

def identify_user():
	waitingForUser = True

	while waitingForUser:
		print "looking for person"
		global userID, interactionLevel

		person_result = UID_client.queryPerson()
		if person_result.is_person:
			if person_result.is_known_person:
				userID = person_result.id
				baristaDB.OpenDatabase(DB_NAME)

				baristaDB.IncrementNumVisits(userID)
				print "Found existing person userID: " + str(userID) + " Level: " + str(baristaDB.GetInteractionLevel(userID))
				baristaDB.CloseDatabase(DB_NAME)
				UID_client.definePerson(userID)
			else:
				baristaDB.OpenDatabase(DB_NAME)
				userID = baristaDB.CreateNewUser()
				print "Created new person userID: " + str(userID) + " Level: " + str(baristaDB.GetInteractionLevel(userID))
				baristaDB.CloseDatabase(DB_NAME)
				UID_client.definePerson(userID)
		
		waitingForUser = not person_result.is_person

def begin_interaction(stream):
	global finished, Paused, pub_speech
	flacrecord.calibrate_input_threshold(stream)
	googleTTS("Greetings! After the tone, please speak clearly towards my face. Don't forget to say Hello!")
	Paused = False
	finished = False

	while not finished:
		while (Paused):
			pass
		flac_file = listen_for_block_of_speech(stream)
		if finished:
			break
		if finished:
			break
		if not flac_file == []:
			hypothesis = stt_google_wav(flac_file)
			if finished:
				break
			if not hypothesis == []:
				print "I heard: " + hypothesis
				pub_speech.publish(hypothesis)
				if hypothesis.lower() == "what does the fox say":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/fox.wav'))
				elif hypothesis.lower() == "do you have a license":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/mate.wav'))
				elif hypothesis.lower() == "do you work out":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/work.wav'))
				elif hypothesis.lower() == "something strange in the neighborhood":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/ghost.wav'))
				elif hypothesis.lower() == "attention":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/attention.wav'))
				elif hypothesis.lower() == "i'm talking to you":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/talking.wav'))
				elif hypothesis.lower() == "i don't want you":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/want.wav'))
				elif hypothesis.lower() == "how did we meet":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/met.wav'))
				elif hypothesis.lower() == "do you have any popcorn":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/popcorn.wav'))
				elif hypothesis.lower() == "how did you get to work today":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/underground.wav'))
				elif hypothesis.lower() == "which man are you":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/tetris.wav'))
				elif hypothesis.lower() == "what are you":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/blue.wav'))
				elif hypothesis.lower() == "the dogs are out":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/dogs.wav'))
				elif hypothesis.lower() == "what did she say":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/love.wav'))
				elif hypothesis.lower() == "is there a house in new orleans":
					play_wav(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'easter_eggs/orleans.wav'))
				else :
					witResult = witLookup(hypothesis)
					if not witResult == []:
						global userID
						responseString, finished = messageResponse(witResult, userID, stream)
					else:
						responseString = responseprocess.randomNegative()
					
					flacrecord.calibrate_input_threshold(stream)
					googleTTS(responseString)
			else:
				responseString = responseprocess.randomNegative()
				flacrecord.calibrate_input_threshold(stream)
				googleTTS(responseString)
		else:
				responseString = responseprocess.randomNegative()
				flacrecord.calibrate_input_threshold(stream)
				googleTTS(responseString)

def users_found(self):
	stream = flacrecord.open_stream()
	identify_user()
	print "Beginning Interaction"
	begin_interaction(stream)
 	flacrecord.close_stream(stream)
	return True

def userPresenceChange(message):
	global finished
	if not finished:
		finished = not message.is_person
		if not message.is_person:
			flacrecord.cancel_interaction()
			rospy.loginfo(rospy.get_name() + ": User Lost. Terminating")

def pause_callback(message):
	global Paused
	if (message.data == 'pause'):
		Paused = True
	else:
		Paused = False

def calibrate_callback(in_data):
	flacrecord.calibrate_input_threshold()
	std_srvs.srv.EmptyResponse()
	

def voice_control_server():
	global userCount, finished
	userCount = 1
	finished = True

	rospy.init_node('voice_control')

	rospy.Subscriber('~say', String, sayCallback)
	global pub_speech
	pub_speech = rospy.Publisher('~speech', String)

	#UID_client.subscribe(userPresenceChange)

	rospy.Service('voice_control', voice_control, users_found)
	rospy.Service('/voice_control/calibrate', std_srvs.srv.Empty, calibrate_callback)

	rospy.Subscriber('~commands', String, pause_callback)
	rospy.spin()

if __name__ == "__main__":
	global userID, interactionLevel
	userID = 0
	interactionLevel = 0
	voice_control_server()
