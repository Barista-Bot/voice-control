#!/usr/bin/env python2
from StringIO import StringIO
import pycurl, urllib, json

CONFIDENCE_VALUE = 0.65

def witLookup(message):

	message = urllib.quote(message)

	c = pycurl.Curl()

	storage = StringIO()

	c.setopt(c.URL, "https://api.wit.ai/message?q=" + message)
	c.setopt(c.HTTPHEADER, ['Authorization: Bearer 64ZXFRIL27NFGCJQ4WQH4VYQY7DD3QQK'])
	c.setopt(c.WRITEFUNCTION, storage.write)
	c.perform()
	c.close()

	try:
		resultJSON = json.loads(storage.getvalue())
		print resultJSON['outcome']['confidence']
		if (float(resultJSON['outcome']['confidence']) > CONFIDENCE_VALUE):
			return resultJSON['outcome']
		else:
			return []
	except:
		return []

if __name__ == '__main__':
	witResult = witLookup('Hello')
	print witResult