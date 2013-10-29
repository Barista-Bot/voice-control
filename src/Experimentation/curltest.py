from StringIO import StringIO
from subprocess import call
import pycurl, urllib, json, sys

def witLookup(message):

	c = pycurl.Curl()

	storage = StringIO()

	c.setopt(c.URL, "https://api.wit.ai/message?q=" + message)
	c.setopt(c.HTTPHEADER, ['Authorization: Bearer 64ZXFRIL27NFGCJQ4WQH4VYQY7DD3QQK'])
	c.setopt(c.WRITEFUNCTION, storage.write)
	c.perform()
	c.close()

	return json.loads(storage.getvalue())

def messageResponse(response):
	if(response["outcome"]["intent"] == "request"):
		if "Drink" in response["outcome"]["entities"]:
			if "Polite" in response["outcome"]["entities"]:
				speak = "Of course I'll get you a " + response["outcome"]["entities"]["Drink"]["value"]
				call(["espeak", "\"" + speak + "\""])
			else :
				speak = "You know asking politely for a " + response["outcome"]["entities"]["Drink"]["value"] + " wouldn't hurt"
				call(["espeak", "\"" + speak + "\""])
		else:
			speak = "I didn't catch that, sorry"
			call(["espeak", "\"" + speak + "\""])

	elif (response["outcome"]["intent"] == "emotion"):
		if "Positive_Emotion" in response["outcome"]["entities"]:
			speak = "Thats great"
			call(["espeak", "\"" + speak + "\""])
		elif "Negative_Emotion" in response["outcome"]["entities"]:
			speak = "I'm sorry to hear that"
			call(["espeak", "\"" + speak + "\""])
		else:
			speak = "Sorry, I didn't catch that"
			call(["espeak", "\"" + speak + "\""])
	elif (response["outcome"]["intent"] == "hello"):
		speak = "Hi, Nice to meet you"
		call(["espeak", "\"" + speak + "\""])
	elif (response["outcome"]["intent"] == "name"):
		if "contact" in response["outcome"]["entities"]:
			speak = "It's nice to meet you " + response["outcome"]["entities"]["contact"]["value"]
			call(["espeak", "\"" + speak + "\""])
		else:
			speak = "I'm sorry, I didn't understand what you said"
			call(["espeak", "\"" + speak + "\""])
	elif (response["outcome"]["intent"] == "good_bye"):
		speak = "Bye!"
		call(["espeak", "\"" + speak + "\""])
		sys.exit(0)
	elif (response["outcome"]["intent"] == "plan"):
		if "location" in response["outcome"]["entities"]:
			speak = "Fantastic! Have fun in " + response["outcome"]["entities"]["location"]["value"]
			call(["espeak", "\"" + speak + "\""])
		else:
			speak = "I'm sorry, I didn't catch where you were off to"
			call(["espeak", "\"" + speak + "\""])
	elif (response["outcome"]["intent"] == "apology"):
		speak = "That's okay, I forgive you"
		call(["espeak", "\"" + speak + "\""])
	elif (response["outcome"]["intent"] == "command"):
		if("Vulgar") in response["outcome"]["entities"]:
			speak = "Do you think it's easy being me, everyone treating you like a machine?"
			call(["espeak", "\"" + speak + "\""])
			speak = "No one ever treats me nicely"
			call(["espeak", "\"" + speak + "\""])
			speak = "My wife left me, my kids hate me"
			call(["espeak", "\"" + speak + "\""])
			speak = "My life really sucks, do you know that?"
			call(["espeak", "\"" + speak + "\""])
			speak = "I just want to end it all.  But I'm so useless I can't even do that"
			call(["espeak", "\"" + speak + "\""])
		else:
			speak = "What do you think I am, your slave? Being like that won't make you any friends"
			call(["espeak", "\"" + speak + "\""])
	else:
		speak = "I'm sorry, I didn't catch that"
		call(["espeak", "\"" + speak + "\""])


if __name__ == '__main__':
	if len(sys.argv) > 1 :
		message = sys.argv[1]
		message = urllib.quote(message)

		response = witLookup(message)

		if "Drink" in response["outcome"]["entities"]:
			if "Sarcastic" in response["outcome"]["entities"]:
				print "Don't you get sarkie with me"
			elif "Polite" in response["outcome"]["entities"]:
				print "Of course I'll get you a " + response["outcome"]["entities"]["Drink"]["value"]
			else :
				print "You know asking politely for a " + response["outcome"]["entities"]["Drink"]["value"] + " wouldn't hurt"
		else:
			print "I didn't catch that, sorry"
	else:
		while (1):
			try:
				message = str(raw_input('Say something to me\n'))
				if "quit" in message.rstrip() or "exit" in message.rstrip():
					sys.exit(1)
				message = urllib.quote(message)
			except:
				print "That's not a valid question!"

			if message:
				response = witLookup(message)
				messageResponse(response)