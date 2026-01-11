import shelve
import json
from user import User


class Database:
    #Default Constructor to intialize Db object
    def __init__(self):
        self.shelf = shelve.open('users_db.db')
        try:
            self.users_list = self.shelf['users_list']
        except:
            self.shelf['users_list'] = []
#function to add user into shelve database
    def AddUser(self, user):
        self.LoadDatabase()
        self.users_list.append(json.dumps(user.__dict__))
        self.shelf['users_list'] = self.users_list
#Function to Loaddatabse into a list
    def LoadDatabase(self):
        self.users_list = self.shelf['users_list']
#search for a specific account by username and password
    def getUser(self, name, password):
        self.LoadDatabase()

        for user in self.users_list:
            user = json.loads(user)
            if user['name'] == name and user['password'] == password:
                return user
        return None
#Search for a User by Name
    def getUserbyName(self, name):
        self.LoadDatabase()
        for user in self.users_list:
            user = json.loads(user)
            if user['name'] == name:
                return user
        return None
#Close the database
    def CloseDatabase(self):
        self.shelf.close()
#Update the user data
    def UpdateUser(self, user11):
        temp_list = []
        for user in self.users_list:
            user2 = json.loads(user)
            if user2['name'] != user11.name:
                temp_list.append(user)
        self.users_list = temp_list.copy()
        self.users_list.append(json.dumps(user11.__dict__))
        self.shelf['users_list'] = self.users_list


