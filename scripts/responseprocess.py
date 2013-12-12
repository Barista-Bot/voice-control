#!/usr/bin/env python2
import roslib
from flacrecord import listen_for_block_of_speech
from flacrecord import calibrate_input_threshold
from googlewebspeech import stt_google_wav
from witapi import witLookup
from googletext2speech import googleTTS
from googletext2speech import play_wav
import sys
import baristaDB
import rospy
from user_identification import client as UID_client
from random import randint
import time
import coffee_machine_control.srv
DatabaseName = "baristaDB.db"

interaction_status = {}

def passServerGlobals(g):
    global server_globals
    server_globals = g

def dispense_coffee(coffee):
    print "Waiting for Coffee Machine..."
    rospy.wait_for_service('coffee_machine')
    coffee_machine_service = rospy.ServiceProxy('coffee_machine', coffee_machine_control.srv.coffee_machine)
    try:
        for Type in ["caramel", "chocolate", "vanilla", "christmas"]:
            if Type in coffee.lower():
                googleTTS("We're making your coffee now. Please wait")
                print "Requesting a " + Type
                resp = coffee_machine_service(Type)
                print resp
                time.sleep(20)
                return "Your coffee's ready, please take the cup.  Careful, it'll be hot"
        return "That hasn't worked, sorry"
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e
        return "I'm sorry, something's gone wrong.  Please tell the Barista Bot team"

def validCoffeeChoice(coffeeType):
    for Type in ["caramel", "chocolate", "vanilla", "christmas"]:
        if Type in coffeeType.lower():
            return True
    return False

def randomNegative():
    responses = ["I'm sorry, I missed that", "Sorry, I didn't catch that", "Sorry I didn't get that", "I didn't get that", "I couldn't make that out"]
    return responses[randint(0, len(responses) - 1)]

def confirmation(response, stream):
    witResult = {"intent" : None}
    while not (witResult["intent"] in ["affirmative", "negative"]):
        calibrate_input_threshold(stream)
        googleTTS(response)
        flac_file = listen_for_block_of_speech(stream)

        override = server_globals['witResultOverride']
        server_globals['witResultOverride'] = None
        if override:
            witResult = override
            server_globals['pub_speech'].publish(str(override))
        else:
            hypothesis = stt_google_wav(flac_file)
            if hypothesis:
                server_globals['pub_speech'].publish(hypothesis)
                witResult = witLookup(hypothesis)
        if witResult:
            if (witResult["intent"] == "affirmative"):
                return True
            elif (witResult["intent"] == "negative"):
                return False
    return False    


def messageResponse(witResult, userId, stream):
    baristaDB.OpenDatabase(DatabaseName)
    baristaDB.SetTime(userId)
    print "Got UserId " + str(userId) 
    level = baristaDB.GetInteractionLevel(userId)
    interaction_status['user_id'] = userId
    interaction_status['level'] = level

    finished = False
    try:

#************************************** LEVEL 0  ****************************************

        if (level == 0):

            if (witResult["intent"] == "hello"):
                UID_client.definePerson(userId)
                response = "Hello would you like a coffee?"
                confirm = confirmation(response, stream)
                if confirm:
                    googleTTS("Which coffee would you like, we have Caramel, Vanilla, Christmas and chocolate coffees?")
                    response = "Which type would you like?"
                else:
                    finished = True
                    response = "Unfortunately I can only offer you coffee, I hope you have a nice day - Good Bye"
            
            elif (witResult["intent"] == "coffee_question"):
                UID_client.definePerson(userId)
                googleTTS("Which coffee would you like, we have Caramel, Vanilla, Christmas and chocolate coffees?")
                response = "Which type would you like?"

            elif(witResult["intent"] == "request"):
                UID_client.definePerson(userId)
                if "Coffee" in witResult["entities"]:
                    if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
                        if not "coffee" in witResult["entities"]["Coffee"]["value"]:
                            coffee_choice = witResult["entities"]["Coffee"]["value"] + " Coffee" 
                        else:
                            coffee_choice = witResult["entities"]["Coffee"]["value"]
                        response = baristaDB.GetUserName(userId) + " You have ordered a " + coffee_choice + "."
                        googleTTS(response)
                        coffee_request = witResult["entities"]["Coffee"]["value"]
                        baristaDB.SetCoffeePreference(userId, coffee_request)
                        response = dispense_coffee(coffee_request)
                    else:
                        response = "Which coffee would you like, we have Caramel, Vanilla, Christmas and Chocolate coffees"
                
            elif (witResult["intent"] == "finished"):
                finished = True
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
                    user_name = witResult["entities"]["contact"]["value"]
                    response = "It's nice to meet you, " + user_name + ". would you like a coffee?"
                    baristaDB.SetUserName(userId, user_name)
                    interaction_status['user_name'] = user_name
                    confirm = confirmation(response, stream)
                    if confirm:
                        response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel Latte, Vanilla Latte, Christmas Coffee and chocolate"
                    else:
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
                else:
                    response = "I'm sorry, I didn't catch your name"

            elif (witResult["intent"] == "coffee_question"):
                UID_client.definePerson(userId)
                response = "Oh hello there! What is your name?" 

            elif (witResult["intent"] == "request"):
                UID_client.definePerson(userId)
                if "Coffee" in witResult["entities"]:
                    if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
                        if not "coffee" in witResult["entities"]["Coffee"]["value"]:
                            coffee_choice = witResult["entities"]["Coffee"]["value"] + " Coffee" 
                        else:
                            coffee_choice = witResult["entities"]["Coffee"]["value"]
                        response = baristaDB.GetUserName(userId) + " You have ordered a " + coffee_choice + "."
                        googleTTS(response)
                        coffee_request = witResult["entities"]["Coffee"]["value"]
                        baristaDB.SetCoffeePreference(userId, coffee_request)
                        response = dispense_coffee(coffee_request)
                    else:
                        response = baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                else:
                    response = "Sorry we only offer Caramel Latte, Vanilla Latte, Christmas Coffee and Chocolate. Would you like a coffee?"
                
            elif (witResult["intent"] == "finished"):
                finished = True
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
                    user_name = witResult["entities"]["contact"]["value"]
                    response = "It's nice to meet you, " + user_name + ". How are you today?"
                    baristaDB.SetUserName(userId, user_name)
                    interaction_status['user_name'] = user_name
                else:
                    response = "I'm sorry, I didn't catch your name"
                
            elif (witResult["intent"] == "coffee_question"):
                UID_client.definePerson(userId)
                response = "Oh hello there! What is your name?" 

            elif(witResult["intent"] == "emotion"):
                UID_client.definePerson(userId)
                if "Negative_Emotion" in witResult["entities"]:
                    response = "That's a shame, would you like a coffee to make you feel better " + baristaDB.GetUserName(userId)
                    confirm = confirmation(response, stream)
                    if confirm:
                        response = baristaDB.GetUserName(userId) + " we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                    else:
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"

                elif "Positive_Emotion" in witResult["entities"]:
                    UID_client.definePerson(userId)
                    response = "That's great, would a coffee make you feel even better?" + baristaDB.GetUserName(userId)
                    confirm = confirmation(response, stream)
                    if confirm:
                        response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                    else:
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
            
            elif(witResult["intent"] == "feeling_question"):
                if "Self" in witResult["entities"]:
                    response = "I'm pretty good thanks - Brewing Coffee makes me happy! Can I get you a coffee?"
                    confirm = confirmation(response, stream)
                    if confirm:
                        response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                    else:
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
            

            elif (witResult["intent"] == "request"):
                UID_client.definePerson(userId)
                if "Coffee" in witResult["entities"]:
                    if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
                        if not "coffee" in witResult["entities"]["Coffee"]["value"]:
                            coffee_choice = witResult["entities"]["Coffee"]["value"] + " Coffee" 
                        else:
                            coffee_choice = witResult["entities"]["Coffee"]["value"]
                        response = baristaDB.GetUserName(userId) + " You have ordered a " + coffee_choice + "."
                        googleTTS(response)
                        coffee_request = witResult["entities"]["Coffee"]["value"]
                        baristaDB.SetCoffeePreference(userId, coffee_request)
                        response = dispense_coffee(coffee_request)
                    else:
                        response = baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                else:
                    response = "Sorry we only offer Caramel Latte, Vanilla Latte, Christmas Coffee and chocolate. Would you like a coffee?"
                
            elif (witResult["intent"] == "finished"):
                finished = True
                response = "That's great. Goodbye " + baristaDB.GetUserName(userId)
            else:
            
                response = "I'm sorry, could you repeat that?"
                UID_client.definePerson(userId)

#************************************** LEVEL 3  ****************************************
        elif(level == 3):

            if (witResult["intent"] == "hello"):
                UID_client.definePerson(userId)
                if baristaDB.UserExists(userId) and baristaDB.GetUserName(userId) != "":
                    response = "Hello there, nice to see you again " + baristaDB.GetUserName(userId) + ". How are you today?"                   
                else:   
                    response = "Hello there, it's a pleasure to meet you, what's your name?"
            elif (witResult["intent"] == "name"):
                UID_client.definePerson(userId)
                if "contact" in witResult["entities"]:
                    user_name = witResult["entities"]["contact"]["value"]
                    response = "It's nice to meet you, " + user_name + ". How are you?"
                    baristaDB.SetUserName(userId, user_name)              
                    interaction_status['user_name'] = user_name
                else:
                    response = "I'm sorry, I didn't catch your name"
            
            elif (witResult["intent"] == "coffee_question"):
                UID_client.definePerson(userId)
                if baristaDB.UserExists(userId) and baristaDB.GetUserName(userId) != "":
                    response = "Hello there, nice to see you again " + baristaDB.GetUserName(userId) + ". How are you today?"                   
                else:   
                    response = "Hello there, it's a pleasure to meet you, what's your name?"    
        

            #THIS EMOTION IS FOR COURSE Feeling.
            elif(witResult["intent"] == "emotion"):
                UID_client.definePerson(userId)
                if "Negative_Emotion" in witResult["entities"]:
                    response = "That's unfortunate, would you like a coffee to improve your day? " + baristaDB.GetUserName(userId)
                    confirm = confirmation(response, stream)
                    if confirm:
                        if baristaDB.GetCoffeePreference(userId) != "":
                            response = "So," + baristaDB.GetUserName(userId) + ", would you like another" + baristaDB.GetCoffeePreference(userId) +"?"
                            confirm = confirmation(response, stream)    
                            if confirm:
                                coffee_request = witResult["entities"]["Coffee"]["value"]
                                baristaDB.SetCoffeePreference(userId, coffee_request)
                                response = dispense_coffee(coffee_request)
                            else:
                                response = baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"  
                        else:   
                            response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                    else:
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"

                elif "Positive_Emotion" in witResult["entities"]:
                    UID_client.definePerson(userId)
                    response = "That's great, would you like a coffee to improve your productivity?" + baristaDB.GetUserName(userId)
                    confirm = confirmation(response, stream)
                    if confirm:
                        if baristaDB.GetCoffeePreference(userId) != "":
                            response = "So," + baristaDB.GetUserName(userId) + ", would you like another" + baristaDB.GetCoffeePreference(userId) +"?"
                            confirm = confirmation(response, stream)    
                            if confirm:
                                coffee_request = witResult["entities"]["Coffee"]["value"]
                                baristaDB.SetCoffeePreference(userId, coffee_request)
                                response = dispense_coffee(coffee_request)
                            else:
                                response = baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"  
                        else:   
                            response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                    else:                       
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"
            
            elif(witResult["intent"] == "feeling_question"):
                UID_client.definePerson(userId)
                if "Self" in witResult["entities"]:
                    response = "I'm pretty good thanks - Brewing Coffee makes me happy! Can I get you a coffee?"
                    confirm = confirmation(response, stream)
                    if confirm:
                        response = "Today " + baristaDB.GetUserName(userId) + ", we have Caramel, Vanilla, Christmas and chocolate coffees, which would you like?"
                    else:
                        finished = True
                        response = "That's okay.  Have a great day! " + baristaDB.GetUserName(userId) + ". Good Bye"            

            elif (witResult["intent"] == "request"):
                UID_client.definePerson(userId)
                if "Coffee" in witResult["entities"]:
                    if(validCoffeeChoice(witResult["entities"]["Coffee"]["value"])):
                        if not "coffee" in witResult["entities"]["Coffee"]["value"]:
                            coffee_choice = witResult["entities"]["Coffee"]["value"] + " Coffee" 
                        else:
                            coffee_choice = witResult["entities"]["Coffee"]["value"]
                        response = baristaDB.GetUserName(userId) + " You have ordered a " + coffee_choice + "."
                        googleTTS(response)
                        coffee_request = witResult["entities"]["Coffee"]["value"]
                        baristaDB.SetCoffeePreference(userId, coffee_request)
                        response = dispense_coffee(coffee_request)
                        
                else:
                    response = "Sorry we only offer Caramel Latte, Vanilla Latte, Christmas Coffee and chocolate. Which would you like?"
                
            elif (witResult["intent"] == "finished"):
                finished = True
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
