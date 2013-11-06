#!/usr/bin/env python
import roslib; roslib.load_manifest('voice_control')

import sys

import rospy
from voice_control.srv import *

def voice_control_client():
	rospy.wait_for_service('voice_control')
	voice_control_server = rospy.ServiceProxy('voice_control', voice_control)
	try:
		success = voice_control_server()
		print success
	except:
		print "voice control server failed to respond"

if __name__ == "__main__":
	voice_control_client()
