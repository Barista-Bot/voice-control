#!/usr/bin/env python2
import os
import urllib2
from globalvariables import *

CONFIDENCE_VALUE = 0.65

def stt_google_wav(filename):

    if not filename:
	res = []
	return res
    else:	
        f = open(os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(filename))), filename),'rb')
    
    flac_cont = f.read()
    f.close()
    print filename
    os.remove(os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(filename))), filename))
    lang_code='en-GB'
    googl_speech_url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6'%(lang_code)
    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",'Content-type': 'audio/x-flac; rate='+str(SAMPLERATE)}
    req = urllib2.Request(googl_speech_url, data=flac_cont, headers=hrs)
    for i in range(3):
        try:
            p = urllib2.urlopen(req)
            break
        except urllib2.HTTPError:
            pass
    else:
        raise Exception('Could not contact speech recognition URL')
    try:
    	hypotheses = eval(p.read())['hypotheses']
    	#print hypotheses
    	if(float(hypotheses[0]['confidence']) > CONFIDENCE_VALUE):
    		res = hypotheses[0]['utterance']
    	else:
    		res = []
    except IndexError:
    	res = []
    except SyntaxError:
        res = []
    return res

if __name__ == '__main__':
	sttresult = stt_google_wav('flacTest.flac')
	print sttresult
	sttresult = stt_google_wav('noSpeech.flac')
	print sttresult
	sttresult = stt_google_wav('murmuringTest.flac')
	print sttresult
