#!/usr/bin/env python2
import shelve
import os
import rospkg

def open():
    return UserDB()

class UserDB(object):
    def __init__(self, file_name="baristaDB.db"):
        path = os.path.join(rospkg.get_ros_home(), file_name)
        self.storage = shelve.open(path, flag = 'c', writeback = True)
        print "Opening db"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.storage.close()
        print "Closing db"

    def newUser(self):
        id = len(self.storage) + 1
        user = User(id, self.storage, initialise=True)
        return user

    def getUser(self, id):
        return User(id, self.storage)

    def __len__(self):
        return len(self.storage)

class User(object):
    __attr_creation_allowed = True

    def __init__(self, id, storage, initialise=False):
        self.id = id
        self.sync = storage.sync
        self.user_key = str(self.id)
        self.storage = storage
        if initialise:
            self.storage[self.user_key] = {}
            self['Time'] = []
            self.n_visits = 1
            self.level = (id-1)%4
        self.__attr_creation_allowed = False

    def __getitem__(self, key):
        try:
            val = self.storage[self.user_key][key]
            if val == '':
                raise AttributeError, str(key)+' is empty'
            return val
        except KeyError as e:
            raise AttributeError, e

    def __setitem__(self, key, value):
        self.storage[self.user_key][key] = value
        self.sync()

    def __setattr__(self, attr, value):
        if self.__attr_creation_allowed or attr in dir(self):
            object.__setattr__(self, attr, value)
        else:
            raise AttributeError, "New attribute '" + attr + "' cannot be created"

    #name
    @property
    def name(self):
        return self['Name']
    @name.setter
    def name(self, value):
        self['Name'] = value

    #coffee
    @property
    def coffee(self):
        return self['Coffee']
    @coffee.setter
    def coffee(self, value):
        self['Coffee'] = value

    #n_visits
    @property
    def n_visits(self):
        return int(self['Visit'])
    @n_visits.setter
    def n_visits(self, value):
        self['Visit'] = int(value)

    #level
    @property
    def level(self):
        return int(self['Level'])
    @level.setter
    def level(self, value):
        self['Level'] = int(value)