import roslib; roslib.load_manifest('coffee_machine_control')
from flacrecord import listen_for_block_of_speech
from googlewebspeech import stt_google_wav
from witapi import witLookup
from googletext2speech import googleTTS
from googletext2speech import play_wav
import sys
import baristaDB
import rospy
from coffee_machine_control.srv import *
DatabaseName = "baristaDB.db"

## Out of coffee and update order
## Successful please take a cup put it under nozzle push the button and please be careful the coffee is hot. 
def dispense_coffee(coffee):
	#rospy.wait_for_service('coffee_machine')
	#coffee_machine_control = rospy.ServiceProxy('coffee_machine', coffee_machine)
	try:
	    #resp = coffee_machine_control(coffee)
	    #print resp
	    googleTTS("Take a cup, place it under the nozzle and push the button - be careful the coffee will be hot!")
	    return "Let me know when you're done"
	except rospy.ServiceException, e:
	    print "Service call failed: %s"%e
	    return "I'm sorry, something's gone wrong.  Please tell the Barista Bot team"

def validCoffeeChoice(coffeeType):
	for Type in ["caramel", "mocha", "vanilla", "espresso"]:
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
	level = baristaDB.GetInteractionLevel(userId)
	
	finished = False
	try:

#************************************** LEVEL 0  ****************************************

		if (level == 0):

			if (witResult["intent"] == "hello"):
				response = "Hello would you like a coffee?"
				confirm = confirmation(response)
				if confirm:
					response = "What kind of coffee would you like, we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
				else:
					finished = True
					response = "Unfortunately I can only offer you coffee, I hope you have a nice day - Good Bye"
			elif(witResult["intent"] == "request"):
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = "You have ordered a" + witResult["entities"]["Coffee"]["value"] + " are you sure?"
						confirm = confirmation(response)
						if confirm:
							coffee_request = witResult["entities"]["Coffee"]["value"]
							baristaDB.SetCoffeePreference(userId, coffee_request)
							response = dispense_coffee(coffee_request)

						else:
							response = "What kind of coffee would you like, we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
				else:
					response = "Sorry we only offer Caramel Latte, Vanilla Latte, Espresso and Mocha.  Would you like a coffee?"
			elif (witResult["intent"] == "finished"):
				finished = True
				response = "That's great.  Goodbye"
			else:
				response = "I'm sorry, could you repeat that?"


#************************************** LEVEL 1  ****************************************


		elif (level == 1):
			
			if (witResult["intent"] == "hello"):
				response = "Hi, I'm Barista Bot.  What's your name?" 
			
			elif (witResult["intent"] == "name"):			
				if "contact" in witResult["entities"]:
					response = "It's nice to meet you, " + witResult["entities"]["contact"]["value"] + ". would you like a coffee?"
					baristaDB.SetUserName(userId, witResult["entities"]["contact"]["value"])
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
					else:
						finished = True
						response = "Unfortunately I only offer coffee, I hope you have a nice day " + baristaDB.GetUserName(userId) + ". Good Bye"
				else:
					response = "I'm sorry, I didn't catch your name"
			elif (witResult["intent"] == "request"):
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = baristaDB.GetUserName(userId) + " You have ordered a " + witResult["entities"]["Coffee"]["value"] + "; are you sure?"
						confirm = confirmation(response)
						if confirm:
							coffee_request = witResult["entities"]["Coffee"]["value"]
							baristaDB.SetCoffeePreference(userId, coffee_request)
							response = dispense_coffee(coffee_request)
						else:
							response = baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
				else:
					response = "Sorry we only offer Caramel Latte, Vanilla Latte, Espresso and Mocha. Would you like a coffee?"
				
			elif (witResult["intent"] == "finished"):
				finished = True
				response = "That's great. Goodbye " + baristaDB.GetUserName(userId)
			else:
				response = "I'm sorry, could you repeat that?"

#************************************** LEVEL 2  ****************************************

#Need to add weather
		elif (level == 2):

			if (witResult["intent"] == "hello"):
				response = "Hi, I'm Barista Bot.  What's your name?" 
			
			elif (witResult["intent"] == "name"):			
				if "contact" in witResult["entities"]:
					response = "It's nice to meet you, " + witResult["entities"]["contact"]["value"] + " How are you today?"
					baristaDB.SetUserName(userId, witResult["entities"]["contact"]["value"])					
				else:
					response = "I'm sorry, I didn't catch your name"


			elif(witResult["intent"] == "statement"):
				if "Negative_Emotion" in witResult["entities"]:
					response = "That's a shame, would you like a coffee to make you fell better" + baristaDB.GetUserName(userId)
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
					else:
						finished = True
						response = "Unfortunately I only offer coffee, I hope you have a nice day " + baristaDB.GetUserName(userId) + ". Good Bye"

				elif "Positive_Emotion" in witResult["entities"]:
					response = "That's great, would a coffee make you feel even better?" + baristaDB.GetUserName(userId)
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
					else:
						finished = True
						response = "Unfortunately I only offer coffee, I hope you have a nice day " + baristaDB.GetUserName(userId) + ". Good Bye"
				
			elif (witResult["intent"] == "request"):
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = baristaDB.GetUserName(userId) + " You have ordered a " + witResult["entities"]["Coffee"]["value"] + "; are you sure?"
						confirm = confirmation(response)
						if confirm:
							coffee_request = witResult["entities"]["Coffee"]["value"]
							baristaDB.SetCoffeePreference(userId, coffee_request)
							response = dispense_coffee(coffee_request)
						else:
							response = baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
				else:
					response = "Sorry we only offer Caramel Latte, Vanilla Latte, Espresso and Mocha. Would you like a coffee?"
				
			elif (witResult["intent"] == "finished"):
				finished = True
				response = "That's great. Goodbye " + baristaDB.GetUserName(userId)
			else:
			
				response = "I'm sorry, could you repeat that?"


#************************************** LEVEL 3  ****************************************
		else:	
			finished = False
			finished = True

#************************************ ALL LEVELS **************************************

		if (witResult["intent"] == "good_bye"):
				finished = True
				response = "Bye!"
		
	except TypeError:
		response = "I'm sorry, I didn't quite get that"
	except SyntaxError:
		response = "Could you repeat that please?"
	
	baristaDB.CloseDatabase(DatabaseName)
	return (response, finished)

if __name__ == '__main__':
	fakeWitResult = { 'outcome' : {'intent' : "hello"}}
	baristaResponse = messageResponse(fakeWitResult)
	print baristaResponse
