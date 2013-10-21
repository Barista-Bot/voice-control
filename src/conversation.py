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
	if (response["outcome"]["intent"] == "hello"):
		speak = "Hello there, it's nice to meet you, what's your name?"

	elif (response["outcome"]["intent"] == "name"):
		if "contact" in response["outcome"]["entities"]:
			speak = "It's nice to meet you " + response["outcome"]["entities"]["contact"]["value"]
		else:
			speak = "I'm sorry, I didn't catch your name"

	elif (response["outcome"]["intent"] == "request"):
		if "Coffee" in response["outcome"]["entities"]:
			if "Polite" in response["outcome"]["entities"] or "Please" in response["outcome"]["entities"]:
				speak = "Of course you can have a " + response["outcome"]["entities"]["Coffee"]["value"]
			else:
				speak = "Yes you can have a " + response["outcome"]["entities"]["Coffee"]["value"]
		elif "Drink" in response["outcome"]["entities"]:
			speak = "Sorry, I don't do " + response["outcome"]["entities"]["Drink"]["value"]
		elif "Food" in response["outcome"]["entities"]:
			speak = "Sorry, I don't do food"

	elif (response["outcome"]["intent"] == "question"):
		if "Random_Question" in response["outcome"]["entities"]:
			speak = "Now how am I supposed to know that!?"
		elif "Name_Question" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "What an interesting question.  You know I've never really thought about that.  I just don't know.  From this day forth I shall be known as Bob the Barista"
		elif "Coffee_Question" in response["outcome"]["entities"] and "Time_Question" in response["outcome"]["entities"]:
			speak = "The coffee take around 25 seconds to make"
		elif "Coffee_Question" in response["outcome"]["entities"] and "Cost_Question" in response["outcome"]["entities"]:
			speak = "I don't charge for my services... I would if I could though"
		elif "Coffee_Question" in response["outcome"]["entities"] and "Drink" in response["outcome"]["entities"]:
			speak = "Sorry I don't serve " + response["outcome"]["entities"]["Drink"]["value"]
		elif "Coffee_Question" in response["outcome"]["entities"] and "Food" in response["outcome"]["entities"]:
			speak = "Sorry, I don't do food"
		elif "Coffee_Question" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "I do espresso, Cappuccino and Mocha"
		elif "Coffee_Question" in response["outcome"]["entities"]:
			speak = "I have espresso, Cappuccino and Mocha"
		elif "Cost_Question" in response["outcome"]["entities"] and "Coffee" in response["outcome"]["entities"]:
			speak = "The coffee here is free you lucky, lucky thing"
		elif "Cost_Question" in response["outcome"]["entities"] and "Drink" in response["outcome"]["entities"]:
			speak = "Sorry I don't do " + response["outcome"]["entities"]["Drink"]["value"]
		elif "Cost_Question" in response["outcome"]["entities"] and "Food" in response["outcome"]["entities"]:
			speak = "I don't serve food, sorry"
		elif "Here_Question" in response["outcome"]["entities"] and "Time_Question" in response["outcome"]["entities"] and "Future" in response["outcome"]["entities"]:
			speak = "I'd imagine I'll be here for a good while yet"
		elif "Here_Question" in response["outcome"]["entities"] and "Time_Question" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "I've been here as long as I can remember... I'm not very old mind you"
		elif "Here_Question" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "I'm here to server coffee.  And I'd like to think I bring a smile to peoples faces"
		elif "How_Question" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "I'm very well thankyou for asking.  Noone ever asks me how I am. Sad really"
		else:
			speak = "I'm sorry, I'm not quite sure how to answer that"

	elif (response["outcome"]["intent"] == "plan"):
		if "location" in response["outcome"]["entities"] and "contact" in response["outcome"]["entities"]:
			"Have fun in " + response["outcome"]["entities"]["location"]["value"] + ", will " + response["outcome"]["entities"]["contact"]["value"] + " be there?"
		elif "location" in response["outcome"]["entities"]:
			speak = "Have fun in " + response["outcome"]["entities"]["location"]["value"]
		elif "agenda_entry" in response["outcome"]["entities"]:
			speak = "Enjoy your " + response["outcome"]["entities"]["agenda_entry"]["value"]

	elif (response["outcome"]["intent"] == "statement"):
		if "Positive_Emotion" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "I feel the same"
		elif "Negative_Emotion" in response["outcome"]["entities"] and "Self" in response["outcome"]["entities"]:
			speak = "That's not very nice is it"
		elif "Negative_Emotion" in response["outcome"]["entities"] and "datetime" in response["outcome"]["entities"]:
			speak = "If it makes you feel any better I'm having an awful day too"
		elif "Negative_Emotion" in response["outcome"]["entities"] and "Weather" in response["outcome"]["entities"]:
			speak = "I know right, isn't it just the worst"
		elif "Positive_Emotion" in response["outcome"]["entities"] and "Weather" in response["outcome"]["entities"]:
			speak = "It's amazing, I love it too"
		elif "Positive_Emotion" in response["outcome"]["entities"] and "datetime" in response["outcome"]["entities"]:
			speak = "It is one of the better days I've had"
		else:
			speak = "I think I need a hearing aid, I didn't quite catch that"

	elif (response["outcome"]["intent"] == "command"):
		if "Vulgar" in response["outcome"]["entities"]:
			speak = "I'll not be spoken to like that, please leave"
		elif "Please" in response["outcome"]["entities"] or "Polite" in response["outcome"]["entities"]:
			speak = "Thankyou for being polite, but i'd rather you not order me around"
		else:
			speak = "I'm not taking orders, ask me nicely"

	elif (response["outcome"]["intent"] == "affirmative"):
		speak = "Thanks, that's great news"

	elif (response["outcome"]["intent"] == "negative"):
		speak = "I'm sorry"

	elif (response["outcome"]["intent"] == "emotion"):
		if "Positive_Emotion" in response["outcome"]["entities"]:
			speak = "That's great to hear"
		elif "Negative_Emotion" in response["outcome"]["entities"]:
			speak = "That's a shame, here, have a coffee to cheer you up"


	elif (response["outcome"]["intent"] == "apology"):
		speak = "Don't worry about it, I'm used to it by now"

	elif (response["outcome"]["intent"] == "good_bye"):
		speak = "Bye!"
		call(["espeak", "\"" + speak + "\""])
		sys.exit(0)
	else:
		speak = "I'm sorry, I didn't catch that"

	call(["espeak", "\"" + speak + "\""])


if __name__ == '__main__':
	if len(sys.argv) > 1 :
		message = sys.argv[1]
		message = urllib.quote(message)

		response = witLookup(message)
		messageResponse(response)
		
	else:
		while (1):
			try:
				message = str(raw_input('Say something to me\n'))
				message = urllib.quote(message)
			except:
				print "That's not a valid question!"
			if message:
				response = witLookup(message)
				messageResponse(response)