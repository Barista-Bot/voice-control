import shelve
import os
import rospkg
from datetime import datetime
#level of interaction

def OpenDatabase(file_path):   
	global CoffeeDatabase
	CoffeeDatabase = shelve.open(file_path, flag = 'c', writeback = True)

def CreateNewUser():
	global CoffeeDatabase
	userId = GetNumberUsers() + 1
	CoffeeDatabase[str(userId)] = {"Name": '', "Coffee": '', "Course": '', "Agenda": '', "Weather": '', "Mood": '', "Time": '', "Visit": '0'}
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
		return CoffeeDatabase[str(userId)]["Visit"]
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

def SetWeather(userId, Weather):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Weather"] = Weather
	CoffeeDatabase.sync()

def SetMood(userId, Mood):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Mood"] = Mood
	CoffeeDatabase.sync()

def SetTime(userId):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Time"] = str(datetime.now())
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
			os.remove(file_path)
	except Exception, e:
		print e



if __name__ == '__main__':
	DbTest = 'DbTest.db'
	file_path = os.path.join(rospkg.get_ros_home(), DbTest)
	OpenDatabase(file_path)
	print GetNumberUsers()
	print UserExists(1)
	UId = CreateNewUser()
	print UId
	print GetUserName(UId)
	print GetCoffeePreference(UId)
	print GetNumberUsers()
	print "Get Num Visits"
	IncrementNumVisits(UId)
	print GetNumberVisits(UId)
	print UserExists(UId)
	SetUserName(UId, 'Frederico')
	print GetUserName(UId)
	SetCoffeePreference(UId, 'MochaChocaLatta YA YA')
	print GetCoffeePreference(UId)
	SetCourse(UId, 'Electronic and Infomation Engineering')
	print GetCourse(UId)
	SetMood(UId, 'Happy')
	print GetMood(UId)
	SetWeather(UId, "Cloudy with a Chance of Meatballs")
	print GetWeather(UId)
	SetAgenda(UId, 'Studying Studying Studying')
	print GetAgenda(UId)
	SetTime(UId)
	print GetTime(UId)


	CloseDatabase(file_path)
	OpenDatabase(file_path)
	print GetNumberUsers()
	ClearDatabase()
	print GetNumberUsers()
	CloseDatabase(file_path)



