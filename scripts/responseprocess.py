import roslib; roslib.load_manifest('coffee_machine_control')
from googlewebspeech import stt_google_wav
from witapi import witLookup
from googletext2speech import googleTTS
from googletext2speech import play_wav
import sys
import baristaDB
import rospy
from coffee_machine_control.srv import *
from googletext2speech import googleTTS
DatabaseName = "baristaDB.db"

## Out of coffee and update order
## Successful please take a cup put it under nozzle push the button and please be careful the coffee is hot. 
def dispense_coffee(response, coffee):
	googleTTS(response)
	googleTTS("I will just pour you one now")
	rospy.wait_for_service('coffee_machine')
	coffee_machine_control = rospy.ServiceProxy('coffee_machine', coffee_machine)
	try:
	    resp = coffee_machine_control(coffee)
	    print resp
	    return "There you go, enjoy your " + coffee
	except rospy.ServiceException, e:
	    print "Service call failed: %s"%e

def validCoffeeChoice(coffeeType):
	for Type in ["caramel latte", "mocha", "vanilla latte", "espresso"]
		if Type in coffeeType.lower():
			return True
	return False	

def confirmation(response):
	googleTTS(response)
	flac_file = listen_for_block_of_speech()
	hypothesis = stt_google_wav(flac_file)
	if not hypothesis == []:
		witResult = witLookup(hypothesis)
		if not witResult == []:
			if (witResult["intent"] == "affirmative"):
				return True
	return False	


def messageResponse(witResult, userId):
	baristaDB.OpenDatabase(DatabaseName)
	
	print "Got UserID " + str(userId) 
	level = GetInteractionLevel(userId)
	
	finished = False
	try:
		if (level == 0):

			if (witResult["intent"] == "hello"):
				response = "Hello would you like a coffee?"
				confirm = confirmation(response)
				if confirm:
					response = "What kind of coffee would you like, we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
				else
					response = "Unfortunately I can only offer you coffee, I hope you have a nice day - Good Bye"
			elif "Coffee" in witResult["entities"]:
				if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
					response = "You have ordered a" + witResult["entities"]["Coffee"]["value"] + " are you sure?"
					confirm = confirmation(response)
					if confirm:
						coffee_request = witResult["entities"]["Coffee"]["value"]
						baristaDB.SetCoffeePreference(userId, coffee_request)
						response = "Take a cup, place it under the nozzle and push the button - be careful the coffee will be hot!"
						googleTTS(response)
						finished = True
						response = dispense_coffee(response, coffee_request)

					else
						response = "What kind of coffee would you like, we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
				else
					response = "Sorry we only offer Caramel Latte, Vanilla Latte, Espresso and Mocha.  Would you like a coffee?"
			else
				response = "I'm sorry, could you repeat that?"

		elif (level == 1):
			finished = False
			finished = True

		elif (level == 2):
			finished = False
			finished = True

		else:	
			finished = False
			finished = True

		if (witResult["intent"] == "good_bye"):
				finished = True
				response = "Bye!"
		
	except TypeError:
		response = "I'm sorry, I didn't quite get that"
	
	baristaDB.CloseDatabase(DatabaseName)
	return (response, finished)

if __name__ == '__main__':
	fakeWitResult = { 'outcome' : {'intent' : "hello"}}
	baristaResponse = messageResponse(fakeWitResult)
	print baristaResponse
