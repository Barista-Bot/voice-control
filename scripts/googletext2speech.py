#!/usr/bin/env python2
import os
import urllib2
import urllib
import rospy
import time
from face.msg import faceRequests

def googleTTS(text='hello', lang='en', fname='result.wav', player='mplayer'):
	""" Send text to Google's text to speech service
	and returns created speech (wav file). """
	pub_face_commands = rospy.Publisher('/face/control', faceRequests)
	face = faceRequests()        
	limit = min(100, len(text))#100 characters is the current limit.
	text = text[0:limit]
	url = "http://translate.google.com/translate_tts"
	values = urllib.urlencode({"q": text, "textlen": len(text), "tl": lang})
	hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"}
	req = urllib2.Request(url, data=values, headers=hrs)
	while True:
		try:
			p = urllib2.urlopen(req)
			break
		except urllib2.HTTPError:
			print "------ Caught Exception in google text to speech urlopen --------"
			time.sleep(0.2)
	f = open(fname, 'wb')
	f.write(p.read())
	f.close()
	face.talking = True
	face.question = text
	pub_face_commands.publish(face)
	play_wav(fname, player)
	face.talking = False
	face.question = ""
	pub_face_commands.publish(face)
	os.remove(fname)

def play_wav(filep, player='mplayer'):
	#print "Playing %s file using %s" % (filep, player)
	os.system(player + " " + filep)

if __name__ == '__main__':
	googleTTS('why hello there')