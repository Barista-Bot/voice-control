import roslib; roslib.load_manifest('coffee_machine_control')
from flacrecord import listen_for_block_of_speech
from googlewebspeech import stt_google_wav
from witapi import witLookup
from googletext2speech import googleTTS
from googletext2speech import play_wav
import sys
import baristaDB
import rospy
from user_identification import client as UID_client
from random import randint
from coffee_machine_control.srv import *
DatabaseName = "baristaDB.db"

## Out of coffee and update order
## Successful please take a cup put it under nozzle push the button and please be careful the coffee is hot. 
def dispense_coffee(coffee):
	print "Waiting for Coffee Machine..."
	rospy.wait_for_service('coffee_machine')
	coffee_machine_control = rospy.ServiceProxy('coffee_machine', coffee_machine)
	try:
		for Type in ["caramel", "mocha", "vanilla", "espresso"]:
			if Type in coffee.lower():
				googleTTS("We're making your coffee now. Please wait")
				print "Requesting a " + Type
				resp = coffee_machine_control(Type)
				print resp
				time.sleep(20)
				return "Your coffee's ready, please take the cup.  Careful, it'll be hot"
		return "That hasn't worked, sorry"
	except rospy.ServiceException, e:
		print "Service call failed: %s"%e
		return "I'm sorry, something's gone wrong.  Please tell the Barista Bot team"

def validCoffeeChoice(coffeeType):
	for Type in ["caramel", "mocha", "vanilla", "espresso"]:
		if Type in coffeeType.lower():
			return True
	return False

def randomNegative():
	responses = ["I'm sorry, I didn't hear you", "Sorry, I didn't catch that", "Sorry I didn't get that", "I didn't hear you", "I didn't get that", "I couldn't make that out"]
	return responses[randint(0, len(responses) - 1)]

def confirmation(response):
	witResult = {"intent" : None}
	while not (witResult["intent"] in ["affirmative", "negative"]):
		googleTTS(response)
		flac_file = listen_for_block_of_speech()
		hypothesis = stt_google_wav(flac_file)
		if not hypothesis == []:
			witResult = witLookup(hypothesis)
			if not witResult == []:
				if (witResult["intent"] == "affirmative"):
					return True
				elif (witResult["intent"] == "negative"):
					return False
	return False	


def messageResponse(witResult, userId):
	baristaDB.OpenDatabase(DatabaseName)
	baristaDB.SetTime(userId)
	print "Got UserId " + str(userId) 
	level = baristaDB.GetInteractionLevel(userId)
	
	finished = False
	try:

#************************************** LEVEL 0  ****************************************

		if (level == 0):

			if (witResult["intent"] == "hello"):
				UID_client.definePerson(userId)
				response = "Hello would you like a coffee?"
				confirm = confirmation(response)
				if confirm:
					googleTTS("What kind of coffee would you like, we have Caramel Latte, Vanilla Latte, Espresso and Mocha")
					response = "Which type would you like?"
				else:
					#finished = True
					response = "Unfortunately I can only offer you coffee, I hope you have a nice day - Good Bye"
			elif(witResult["intent"] == "request"):
				UID_client.definePerson(userId)
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = "You have ordered a" + witResult["entities"]["Coffee"]["value"] + " is that correct??"
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
				#finished = True
				response = "That's great.  Goodbye"
			else:
				response = "I'm sorry, could you repeat that?"
				UID_client.definePerson(userId)

#************************************** LEVEL 1  ****************************************


		elif (level == 1):
			
			if (witResult["intent"] == "hello"):
				response = "Hi, I'm Barista Bot.  What's your name?" 
			elif (witResult["intent"] == "name"):	
				UID_client.definePerson(userId)		
				if "contact" in witResult["entities"]:
					response = "It's nice to meet you, " + witResult["entities"]["contact"]["value"] + ". would you like a coffee?"
					baristaDB.SetUserName(userId, witResult["entities"]["contact"]["value"])
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha"
					else:
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
				else:
					response = "I'm sorry, I didn't catch your name"
			elif (witResult["intent"] == "request"):
				UID_client.definePerson(userId)
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = baristaDB.GetUserName(userId) + " You have ordered a " + witResult["entities"]["Coffee"]["value"] + "; is that correct??"
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
				#finished = True
				response = "That's great. Goodbye " + baristaDB.GetUserName(userId)
			else:
				response = "I'm sorry, could you repeat that?"
				UID_client.definePerson(userId)

#************************************** LEVEL 2  ****************************************

#Need to add weather
		elif (level == 2):

			if (witResult["intent"] == "hello"):
				response = "Hi, I'm Barista Bot.  What's your name?" 
			elif (witResult["intent"] == "name"):		
				UID_client.definePerson(userId)	
				if "contact" in witResult["entities"]:
					response = "It's nice to meet you, " + witResult["entities"]["contact"]["value"] + ". How are you today?"
					baristaDB.SetUserName(userId, witResult["entities"]["contact"]["value"])					
				else:
					response = "I'm sorry, I didn't catch your name"


			elif(witResult["intent"] == "emotion"):
				UID_client.definePerson(userId)
				if "Negative_Emotion" in witResult["entities"]:
					response = "That's a shame, would you like a coffee to make you feel better " + baristaDB.GetUserName(userId)
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
					else:
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"

				elif "Positive_Emotion" in witResult["entities"]:
					UID_client.definePerson(userId)
					response = "That's great, would a coffee make you feel even better?" + baristaDB.GetUserName(userId)
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
					else:
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
			
			elif(witResult["intent"] == "feeling_question"):
				if "Self" in witResult["entities"]:
					response = "I'm pretty good thanks - Brewing Coffee makes me happy! Can I get you a coffee?"
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
					else:
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
			

			elif (witResult["intent"] == "request"):
				UID_client.definePerson(userId)
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = baristaDB.GetUserName(userId) + " You have ordered a " + witResult["entities"]["Coffee"]["value"] + "; is that correct??"
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
				#finished = True
				response = "That's great. Goodbye " + baristaDB.GetUserName(userId)
			else:
			
				response = "I'm sorry, could you repeat that?"
				UID_client.definePerson(userId)

#************************************** LEVEL 3  ****************************************
		else:

			if (witResult["intent"] == "hello"):
				UID_client.definePerson(userId)
				if baristaDB.UserExists(userId) and baristaDB.GetUserName(userId) != "" and baristaDB.GetCourse(userId) != "":
					response = "Hello there, nice to see you again " + baristaDB.GetUserName(userId) + "How is " + GetCourse(userId) + "going?"					
				else:	
					response = "Hello there, it's a pleasure to meet you, what's your name?"
			elif (witResult["intent"] == "name"):
				UID_client.definePerson(userId)
				if "contact" in witResult["entities"]:
					response = "It's nice to meet you, " + witResult["entities"]["contact"]["value"] + ". What course do you do?"
					baristaDB.SetUserName(userId, witResult["entities"]["contact"]["value"])					
				else:
					response = "I'm sorry, I didn't catch your name"
			
			#THIS EMOTION IS FOR COURSE Feeling.
			elif(witResult["intent"] == "emotion"):
				UID_client.definePerson(userId)
				if "Negative_Emotion" in witResult["entities"]:
					response = "That's frustrating, would you like a coffee to improve your day? " + baristaDB.GetUserName(userId)
					confirm = confirmation(response)
					if confirm:
						if baristaDB.GetCoffeePreference(userId) != "":
							response = "So," + baristaDB.GetUserName(userId) + ", would you like another" + baristaDB.GetCoffeePreference(userId) +"?"
							confirm = confirmation(response)	
							if confirm:
								coffee_request = witResult["entities"]["Coffee"]["value"]
								baristaDB.SetCoffeePreference(userId, coffee_request)
								response = dispense_coffee(coffee_request)
							else:
								response = baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"	
						else:	
							response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
					else:
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"

				elif "Positive_Emotion" in witResult["entities"]:
					UID_client.definePerson(userId)
					response = "That's great, would you like a coffee to improve your productivity?" + baristaDB.GetUserName(userId)
					confirm = confirmation(response)
					if confirm:
						if baristaDB.GetCoffeePreference(userId) != "":
							response = "So," + baristaDB.GetUserName(userId) + ", would you like another" + baristaDB.GetCoffeePreference(userId) +"?"
							confirm = confirmation(response)	
							if confirm:
								coffee_request = witResult["entities"]["Coffee"]["value"]
								baristaDB.SetCoffeePreference(userId, coffee_request)
								response = dispense_coffee(coffee_request)
							else:
								response = baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"	
						else:	
							response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
					else:						
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
			
			elif(witResult["intent"] == "feeling_question"):
				UID_client.definePerson(userId)
				if "Self" in witResult["entities"]:
					response = "I'm pretty good thanks - Brewing Coffee makes me happy! Can I get you a coffee?"
					confirm = confirmation(response)
					if confirm:
						response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Espresso and Mocha, which would you like?"
					else:
						#finished = True
						response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"			

			elif (witResult["intent"] == "request"):
				UID_client.definePerson(userId)
				if "Coffee" in witResult["entities"]:
					if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
						response = baristaDB.GetUserName(userId) + " You have ordered a " + witResult["entities"]["Coffee"]["value"] + "; is that correct??"
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
				#finished = True
				response = "That's great. Goodbye " + baristaDB.GetUserName(userId)
			else:
				response = "I'm sorry, could you repeat that?"

#************************************ ALL LEVELS **************************************

		if (witResult["intent"] == "good_bye"):
				finished = True
				response = "Bye!"
		
	except TypeError:
		response = "I'm sorry, I didn't quite get that"
	except SyntaxError:
		response = "Could you repeat that please?"
	
	baristaDB.CloseDatabase(DatabaseName)
	if 'response' in locals():
		return (response, finished)
	else:
		return ("", finished)

if __name__ == '__main__':
	fakeWitResult = { 'outcome' : {'intent' : "hello"}}
	baristaResponse = messageResponse(fakeWitResult)
	print baristaResponse
