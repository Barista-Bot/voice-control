def messageResponse(witResult):
	if (witResult["outcome"]["intent"] == "hello"):
		response = "Hello there, it's nice to meet you, what's your name?"

	if (witResult["outcome"]["intent"] == "hello"):
		response = "Hello there, it's nice to meet you, what's your name?"

	elif (witResult["outcome"]["intent"] == "name"):
        	if "contact" in witResult["outcome"]["entities"]:
			response = "It's nice to meet you " + witResult["outcome"]["entities"]["contact"]["value"]
		else:
			response = "I'm sorry, I didn't catch your name"

	elif (witResult["outcome"]["intent"] == "request"):
		if "Coffee" in witResult["outcome"]["entities"]:
			if "Polite" in witResult["outcome"]["entities"] or "Please" in witResult["outcome"]["entities"]:
				response = "Of course you can have a " + witResult["outcome"]["entities"]["Coffee"]["value"]
			else:
				response = "Yes you can have a " + witResult["outcome"]["entities"]["Coffee"]["value"]
	        elif "Drink" in witResult["outcome"]["entities"]:
			response = "Sorry, I don't do " + witResult["outcome"]["entities"]["Drink"]["value"]
		elif "Food" in witResult["outcome"]["entities"]:
			response = "Sorry, I don't do food"    
		elif "Random_Question" in witResult["outcome"]["entities"]:
			response = "Now how am I supposed to know that!?"

	elif witResult["outcome"]["intent"] == "Name_Question":
		response = "What an interesting question.  You know I've never really thought about that.  I just don't know.  From this day forth I shall be known as Barry the Barista Bot"
	
	elif witResult["outcome"]["intent"] == "Product_Question":
		if "Coffee" in witResult["outcome"]["entities"]: 
			response = "We have Coffee X, Coffee Y and Coffee Z"
		elif "Food" in witResult["outcome"]["entities"]: 
			response = "Mate, I'm a bloody coffee machine - I don't serve food... nope, not even those little coffee biscuits"
		elif "Drink" in witResult["outcome"]["entities"]:
			response = "Sorry, unfortunately I only serve Coffee - I'd love it if I could serve Beer, but unfortunately I couldn't get a liquor licence..."

	elif(witResult["outcome"]["intent"] == "Feeling_Question"):
		if "Self" in witResult["outcome"]["entities"]:
			response = "I'm pretty good thanks - Brewing Coffee makes me happy! How are you today?"
	elif(witResult["outcome"]["intent"] == "Emotion"):
		if "Negative_Emotion" in witResult["outcome"]["entities"]:
			response = "That's sad to hear - perhaps a coffee would make you feel better?"
		elif "Positive_Emotion" in witResult["outcome"]["entities"]:
			response = "You know what might make it even better - a coffee!"
	
#        elif "Coffee_Question" in witResult["outcome"]["entities"] and "Self" in witResult["outcome"]["entities"]:
#            response = "I do espresso, Cappuccino and Mocha"
#        elif "Coffee_Question" in witResult["outcome"]["entities"]:
#            response = "I have espresso, Cappuccino and Mocha"
#        elif "Cost_Question" in witResult["outcome"]["entities"] and "Coffee" in witResult["outcome"]["entities"]:
#            response = "The coffee here is free you lucky, lucky thing"
#        elif "Cost_Question" in witResult["outcome"]["entities"] and "Drink" in witResult["outcome"]["entities"]:
#            response = "Sorry I don't do " + witResult["outcome"]["entities"]["Drink"]["value"]
#        elif "Cost_Question" in witResult["outcome"]["entities"] and "Food" in witResult["outcome"]["entities"]:
#            response = "I don't serve food, sorry"
#        elif "Here_Question" in witResult["outcome"]["entities"] and "Time_Question" in witResult["outcome"]["entities"] and "Future" in witResult["outcome"]["entities"]:
#            response = "I'd imagine I'll be here for a good while yet"
#        elif "Here_Question" in witResult["outcome"]["entities"] and "Time_Question" in witResult["outcome"]["entities"] and "Self" in witResult["outcome"]["entities"]:
#            response = "I've been here as long as I can remember... I'm not very old mind you"
#        elif "Here_Question" in witResult["outcome"]["entities"] and "Self" in witResult["outcome"]["entities"]:
#            response = "I'm here to server coffee.  And I'd like to think I bring a smile to peoples faces"
#        elif "How_Question" in witResult["outcome"]["entities"] and "Self" in witResult["outcome"]["entities"]:
#            response = "I'm very well thankyou for asking.  Noone ever asks me how I am. Sad really"
#        else:
#            response = "I'm sorry, I'm not quite sure how to answer that"

#    elif (witResult["outcome"]["intent"] == "plan"):
#        if "location" in witResult["outcome"]["entities"] and "contact" in witResult["outcome"]["entities"]:
#            "Have fun in " + witResult["outcome"]["entities"]["location"]["value"] + ", will " + witResult["outcome"]["entities"]["contact"]["value"] + " be there?"
#        elif "location" in witResult["outcome"]["entities"]:
#            response = "Have fun in " + witResult["outcome"]["entities"]["location"]["value"]
#        elif "agenda_entry" in witResult["outcome"]["entities"]:
#            response = "Enjoy your " + witResult["outcome"]["entities"]["agenda_entry"]["value"]
#    elif (witResult["outcome"]["intent"] == "statement"):
#        if "Positive_Emotion" in witResult["outcome"]["entities"] and "Self" in witResult["outcome"]["entities"]:
#            response = "I feel the same"
#        elif "Negative_Emotion" in witResult["outcome"]["entities"] and "Self" in witResult["outcome"]["entities"]:
#            response = "That's not very nice is it"
#        elif "Negative_Emotion" in witResult["outcome"]["entities"] and "datetime" in witResult["outcome"]["entities"]:
#            response = "If it makes you feel any better I'm having an awful day too"
#        elif "Negative_Emotion" in witResult["outcome"]["entities"] and "Weather" in witResult["outcome"]["entities"]:
#           response = "I know right, isn't it just the worst"
#        elif "Positive_Emotion" in witResult["outcome"]["entities"] and "Weather" in witResult["outcome"]["entities"]:
#            response = "It's amazing, I love it too"
#        elif "Positive_Emotion" in witResult["outcome"]["entities"] and "datetime" in witResult["outcome"]["entities"]:
#            response = "It is one of the better days I've had"
#        else:
#            response = "I think I need a hearing aid, I didn't quite catch that"

#    elif (witResult["outcome"]["intent"] == "command"):
#        if "Vulgar" in witResult["outcome"]["entities"]:
#            response = "I'll not be spoken to like that, please leave"
#        elif "Please" in witResult["outcome"]["entities"] or "Polite" in witResult["outcome"]["entities"]:
#            response = "Thankyou for being polite, but i'd rather you not order me around"
#        else:
#            response = "I'm not taking orders, ask me nicely"

#    elif (witResult["outcome"]["intent"] == "affirmative"):
#        response = "Thanks, that's great news"

#    elif (witResult["outcome"]["intent"] == "negative"):
#        response = "I'm sorry"

#    elif (witResult["outcome"]["intent"] == "emotion"):
#        if "Positive_Emotion" in witResult["outcome"]["entities"]:
#            response = "That's great to hear"
#        elif "Negative_Emotion" in witResult["outcome"]["entities"]:
#            response = "That's a shame, here, have a coffee to cheer you up"

#    elif (witResult["outcome"]["intent"] == "apology"):
#        response = "Don't worry about it, I'm used to it by now"

	elif (witResult["outcome"]["intent"] == "good_bye"):
		response = "Bye!"
	else:
		response = "I'm sorry, I didn't catch that"

	print "Running response: " + response
  

	return response

if __name__ == '__main__':
	fakeWitResult = { 'outcome' : {'intent' : "hello"}}
	baristaResponse = messageResponse(fakeWitResult)
	print baristaResponse
