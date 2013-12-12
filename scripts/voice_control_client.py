#!/usr/bin/env python2
import roslib; roslib.load_manifest('voice_control')

import sys

import rospy
from voice_control.srv import *

def voice_control_client():
	rospy.wait_for_service('voice_control')
	service = rospy.ServiceProxy('voice_control', voice_control)
	try:
		success = service()
		print success
	except:
		print "voice control server failed to respond"

if __name__ == "__main__":
	voice_control_client()
