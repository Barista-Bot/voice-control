#!/usr/bin/env python2
import shelve
import os
import rospkg
from datetime import datetime
import pywapi
import string


def OpenDatabase(file_path):   
	global CoffeeDatabase
	path = os.path.join(rospkg.get_ros_home(), file_path)
	CoffeeDatabase = shelve.open(path, flag = 'c', writeback = True)

def CreateNewUser():
	global CoffeeDatabase
	userId = GetNumberUsers() + 1
	CoffeeDatabase[str(userId)] = {"Name": '', "Coffee": '', "Course": '', "Agenda": '', "Weather": '', "Mood": '', "Time": [], "Visit": '1', "Level": ''}
	SetInteractionLevel(userId)
	CoffeeDatabase.sync()
	return userId

def GetNumberUsers():
	global CoffeeDatabase
	return len(CoffeeDatabase)

def UserExists(userId):
	global CoffeeDatabase
	if str(userId) in CoffeeDatabase.keys():
		return True
	else:
		return False

def GetNumberVisits(userId):
	global CoffeeDatabase
	try:
		return int(CoffeeDatabase[str(userId)]["Visit"])
	except:
		return ""

def GetUserName(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Name"]
	except:	
		return ""

def GetCoffeePreference(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Coffee"]
	except:	
		return ""

def GetCourse(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Course"]
	except:
		return ""

def GetAgenda(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Agenda"]
	except:
		return ""

def GetWeather(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Weather"]
	except:
		return ""

def GetMood(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Mood"]
	except:
		return ""

def GetTime(userId):
	global CoffeeDatabase
	try:
		return CoffeeDatabase[str(userId)]["Time"]
	except:
		return ""

def GetInteractionLevel(userId):
	global CoffeeDatabase
	try:
		return int(CoffeeDatabase[str(userId)]["Level"])
	except:
		return ""

def SetUserName(userId, Name):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Name"] = Name
	CoffeeDatabase.sync()

def SetCoffeePreference(userId, CoffeePreference):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Coffee"] = CoffeePreference
	CoffeeDatabase.sync()

def SetCourse(userId, Course):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Course"] = Course
	CoffeeDatabase.sync()

def SetAgenda(userId, Agenda):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Agenda"] = Agenda
	CoffeeDatabase.sync()

def SetWeather(userId):
	global CoffeeDatabase

	weather_com_result = pywapi.get_weather_from_weather_com('UKXX0085')
	weather_type = string.lower(weather_com_result['current_conditions']['text'])
	current_temp = weather_com_result['current_conditions']['temperature']
	CoffeeDatabase[str(userId)]["Weather"] = weather_type
	CoffeeDatabase.sync()

def SetMood(userId, Mood):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Mood"] = Mood
	CoffeeDatabase.sync()

def SetTime(userId):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Time"] += [datetime.now()]
	CoffeeDatabase.sync()

def SetInteractionLevel(userId, level=None):
	global CoffeeDatabase
	if level == None:
		# level = (userId-1)%4
		level = 3
	CoffeeDatabase[str(userId)]["Level"] = str(level)
	CoffeeDatabase.sync()

def IncrementNumVisits(userId):
	global CoffeeDatabase
	temp = CoffeeDatabase[str(userId)]["Visit"]
	CoffeeDatabase[str(userId)]["Visit"] = str(int(temp)+1)
	CoffeeDatabase.sync()




def ClearDatabase():
	global CoffeeDatabase
	CoffeeDatabase.clear() 
	CoffeeDatabase.sync()

def CloseDatabase(file_path):
	global CoffeeDatabase
	numberUsers = GetNumberUsers()
	try:
		CoffeeDatabase.close()
		if numberUsers == 0:
			os.remove(os.path.join(rospkg.get_ros_home(), file_path))
	except Exception, e:
		print e



if __name__ == '__main__':
	DbTest = 'DbTest.db'
	OpenDatabase(DbTest)
	print "Get number of users should be 0"
	print GetNumberUsers()
	print "Check user 1 exists - should be false"
	print UserExists(1)
	UId = CreateNewUser()
	print "New user ID should be 1"
	print UId
	print "Check User 1 exists should be true"
	print UserExists(UId)
	print "Interaction Level ="
	print GetInteractionLevel(UId)
	print "User name - should be blank"
	print GetUserName(UId)
	print "Coffee Preference - should be blank"
	print GetCoffeePreference(UId)
	print "GetNumberUsers - should be 1"
	print GetNumberUsers()
	print "Get Num Visits of user 1 - should be 2"
	IncrementNumVisits(UId)
	print GetNumberVisits(UId)
	print "Set and Get User Name"
	SetUserName(UId, 'Frederico')
	print GetUserName(UId)
	print "Set and Get Coffee Preference"
	SetCoffeePreference(UId, 'MochaChocaLatta YA YA')
	print GetCoffeePreference(UId)
	print "Set and Get Course Name"
	SetCourse(UId, 'Electronic and Infomation Engineering')
	print GetCourse(UId)
	print "Set and Get Mood"
	SetMood(UId, 'Happy')
	print GetMood(UId)
	print "Set and Get Weather"
	SetWeather(UId)
	print GetWeather(UId)
	print "Set and get Agenda"
	SetAgenda(UId, 'Studying Studying Studying')
	print GetAgenda(UId)
	print "Set and get Time"
	SetTime(UId)
	#print str(GetTime(UId))
	SetTime(UId)
	print GetTime(UId)[0].isoformat()


	CloseDatabase(DbTest)
	OpenDatabase(DbTest)
	print GetNumberUsers()
	ClearDatabase()
	print GetNumberUsers()
	CloseDatabase(DbTest)



