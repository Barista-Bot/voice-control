#!/usr/bin/env python2
import requests

CONFIDENCE_THRESHOLD = 0.65

class SpeechNotUnderstoodException(Exception):
    pass

def query(message):

	url = 'https://api.wit.ai/message'
	query_params = {'q': message}
	headers = {'Authorization': 'Bearer 64ZXFRIL27NFGCJQ4WQH4VYQY7DD3QQK'}
	response = requests.get(url, params=query_params, headers=headers)

	response_dict = response.json()['outcome']
	if (response_dict['confidence'] > CONFIDENCE_THRESHOLD):
		return response_dict
	else:
		raise SpeechNotUnderstoodException()


if __name__ == '__main__':
	witResult = query('Hello')
	print witResult