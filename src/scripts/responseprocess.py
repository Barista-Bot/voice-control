def messageResponse(witResult):
	if (witResult["outcome"]["intent"] == "hello"):
		response = "Hello there, it's nice to meet you, what's your name?"

	return response

if __name__ == '__main__':
	fakeWitResult = { 'outcome' : {'intent' : "hello"}}
	baristaResponse = messageResponse(fakeWitResult)
	print baristaResponse