import shelve
import os

def OpenDatabase(filename):   
	global CoffeeDatabase
	CoffeeDatabase = shelve.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), filename), flag = 'c', writeback = True)

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

def GetNumberUsers():
	global CoffeeDatabase
	return len(CoffeeDatabase)

def UserExists(userId):
	global CoffeeDatabase
	if str(userId) in CoffeeDatabase.keys():
		return True
	else:
		return False

def CreateNewUser():
	global CoffeeDatabase
	userId = GetNumberUsers() + 1
	CoffeeDatabase[str(userId)] = {"Name": '', "Coffee": '', "Course": '', "Agenda": '', "Weather": '', "Mood": ''}
	return userId

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

def ClearDatabase():
	global CoffeeDatabase
	CoffeeDatabase.clear() 
	CoffeeDatabase.sync()

def CloseDatabase(DbName):
	global CoffeeDatabase
	numberUsers = GetNumberUsers()
	try:
		CoffeeDatabase.close()
		if numberUsers == 0:
			os.remove(DbName)
	except Exception, e:
		print e



if __name__ == '__main__':
	DbTest = 'DbTest.db'
	OpenDatabase(DbTest)
	print GetNumberUsers()
	print UserExists(1)
	UId = CreateNewUser()
	print UId
	print GetUserName(UId)
	print GetCoffeePreference(UId)
	print GetNumberUsers()
	print UserExists(UId)
	SetUserName(UId, 'Frederico')
	print GetUserName(UId)
	SetCoffeePreference(UId, 'MochaChocaLatta YA YA')
	print GetCoffeePreference(UId)
	SetCourse(UId, 'Electronic and Infomation Engineering')
	print GetCourse(UId)
	SetMood(UId, 'Happy')
	print GetMood(UId)
	SetWeather(UId, "Sunny")
	print GetWeather(UId)
	SetAgenda(UId, 'Studying Studying Studying')
	print GetAgenda(UId)

	CloseDatabase(DbTest)
	OpenDatabase(DbTest)
	print GetNumberUsers()
	ClearDatabase()
	print GetNumberUsers()
	CloseDatabase(DbTest)



