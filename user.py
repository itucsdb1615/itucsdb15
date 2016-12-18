#from server import app
import psycopg2 as dbapi2
from flask import current_app
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context
#from passlib.ext.django.models import password_context

class User(UserMixin):
    def __init__(self, fullName, userName, eMail, password, description, follower_count, following_count):
        self.fullName = fullName
        self.userName = userName
        self.email = eMail
        self.password = password
        self.description = description
        self.follower_count = follower_count
        self.following_count = following_count
        self.active = True
        #self.is_admin = False

    def get_id(self):
        return self.userName

    @property
    def is_active(self):
        return self.active

#    def set_user(self, fullName, userName, eMail):
#        self.fullName = fullName
#        self.userName = userName
#        self.email = eMail

