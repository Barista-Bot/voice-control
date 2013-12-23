#!/usr/bin/env python2
from gi.repository import Gst
import urllib
import time
Gst.init([])


def play_file(path, cancelled=lambda:False):
	uri = 'file://' + path
	play_by_uri(uri, cancelled=cancelled)
	

def say(text, cancelled=lambda:False):
	query_string = urllib.urlencode({"q": text, "textlen": len(text), "tl": 'en'})
	uri = 'http://translate.google.com/translate_tts?' + query_string
	play_by_uri(uri, cancelled=cancelled)


def play_by_uri(uri, cancelled=lambda:False):
	pl = Gst.ElementFactory.make("playbin", "player")
	pl.props.uri = uri
	pl.set_state(Gst.State.PLAYING)
	try:
	    while not cancelled():
	        time.sleep(0.1)
	        msg = pl.bus.pop_filtered(Gst.MessageType.EOS | Gst.MessageType.ERROR)
	        if msg is not None:
	            break
	finally:
	    pl.set_state(Gst.State.NULL)


if __name__ == '__main__':
	say('hello there')