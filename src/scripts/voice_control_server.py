#!/usr/bin/env python
import flacrecord
import googlewebspeech
import witapi
import responseprocess
import googletext2speech

from voice_control.srv import *
import rospy

def deal_with_voice(user_id):
	print('I\'m a massive cunt')
	return voice_controlResponse(True)

def voice_control_server():
	rospy.init_node('voice_control')
	rospy.Service('voice_control', voice_control, deal_with_voice)

	rospy.spin()

if __name__ == "__main__":
	voice_control_server()