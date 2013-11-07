import shelve
import os

def OpenDatabase(filename):   
	global CoffeeDatabase
	CoffeeDatabase = shelve.open(filename, flag = 'c', writeback = True)

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
	CoffeeDatabase[str(userId)] = {"Name": '', "Coffee": ''}
	return userId

def SetUserName(userId, Name):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Name"] = Name
	CoffeeDatabase.sync()

def SetCoffeePreference(userId, CoffeePreference):
	global CoffeeDatabase
	CoffeeDatabase[str(userId)]["Coffee"] = CoffeePreference

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
	CloseDatabase(DbTest)
	OpenDatabase(DbTest)
	print GetNumberUsers()
	ClearDatabase()
	print GetNumberUsers()
	CloseDatabase(DbTest)



