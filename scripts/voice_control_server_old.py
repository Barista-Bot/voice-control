#!/usr/bin/env python2
from flacrecord import listen_for_block_of_speech
from googlewebspeech import stt_google_wav
from witapi import witLookup
from googletext2speech import googleTTS
from googletext2speech import play_wav

from user_identification import client as UID_client
import user_identification
import flacrecord
import responseprocess

from std_msgs.msg import String
import std_srvs.srv

import voice_control.srv
import rospy, time, os, baristaDB
import ast

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
    global finished, Paused, userID, witResultOverride

    flacrecord.calibrate_input_threshold(stream)
    googleTTS("Greetings! After the tone, please speak clearly towards my face. Don't forget to say Hello!")
    Paused = False
    finished = False

    while not finished and not rospy.is_shutdown():
        while (Paused):
            pass
        flac_file = listen_for_block_of_speech(stream)
        if finished:
            break
        if not flac_file == []:
            if finished:
                break
            override = witResultOverride
            witResultOverride = None
            if override:
                pub_speech.publish(str(override))
                responseString, finished = responseprocess.messageResponse(override, userID, stream)
                print responseString
                googleTTS(responseString)
            else:
                hypothesis = stt_google_wav(flac_file)
                if hypothesis:
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
                        if witResult != []:
                            responseString, finished = responseprocess.messageResponse(witResult, userID, stream)
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

def startInteraction():
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
    global Paused, finished
    if (message.data == 'pause'):
        Paused = True
    elif (message.data == 'stop'):
        finished = True
    else:
        Paused = False

def calibrateCallback(in_data):
    flacrecord.calibrate_input_threshold()
    return std_srvs.srv.EmptyResponse()

def witOverrideCallback(ros_msg):
    print "override callback called with", ros_msg.data
    dict_msg = None
    try:
        dict_msg = ast.literal_eval(ros_msg.data)
        print dict_msg
    except ValueError:
        print "Malformed string"
    global witResultOverride
    witResultOverride = dict_msg
    
def requestInteractionStartCallback(in_data):
    global start_requested
    start_requested = True
    return std_srvs.srv.EmptyResponse()

def interactionStatusCallback(in_data):
    response_dict = {
        'is_active': interaction_is_active,
    }
    for t, key in [(int, 'level'), (int, 'user_id'), (str, 'user_name')]:
        try:   
            response_dict[key] = responseprocess.interaction_status[key]
        except KeyError:
            if t == str:
                response_dict[key] = ''
            else:
                response_dict[key] = -1

    return voice_control.srv.interaction_statusResponse(**response_dict)

def voice_control_server():
    global userCount, finished, witResultOverride, start_requested, pub_speech, interaction_is_active

    userCount = 1
    finished = True
    witResultOverride = None
    start_requested = False
    interaction_is_active = False

    rospy.init_node('voice_control')

    rospy.Subscriber('/voice_control/say', String, sayCallback)
    pub_speech = rospy.Publisher('/voice_control/speech', String)

    #UID_client.subscribe(userPresenceChange)

    rospy.Service('voice_control/start', std_srvs.srv.Empty, requestInteractionStartCallback)
    rospy.Service('/voice_control/calibrate', std_srvs.srv.Empty, calibrateCallback)
    rospy.Service('/voice_control/interaction_status', voice_control.srv.interaction_status, interactionStatusCallback)

    rospy.Subscriber('/voice_control/wit_override', String, witOverrideCallback)

    rospy.Subscriber('/voice_control/commands', String, pause_callback)

    flacrecord.init_faceid_subscription()
    flacrecord.init_ros_override_services()
    responseprocess.passServerGlobals(globals())
    
    while not rospy.is_shutdown():
        if start_requested:
            interaction_is_active = True
            responseprocess.interaction_status = {}
            startInteraction()
            interaction_is_active = False
            start_requested = False
        else:
            time.sleep(0.5)
            print "Waiting to start"


if __name__ == "__main__":
    global userID, interactionLevel
    userID = 0
    interactionLevel = 0
    voice_control_server()
