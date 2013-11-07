import shelve
filename = "test.txt"
d = shelve.open(filename) # open -- file may get suffix added by low-level

d["User1"] = {'Name': 'Revans', 'Coffee': 'MochaChocalatte'}

print len(d)

print d["User1"]['Name']


d.close()       # close it