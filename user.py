from flask import current_app
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context
#from passlib.ext.django.models import password_context

class User(UserMixin):
    def __init__(self, fullName, userName, eMail, password):
        self.fullName = fullName
        self.userName = userName
        self.email = eMail
        self.password = password
        self.active = True
        #self.is_admin = False

    def get_userName(self):
        return self.userName

    @property
    def is_active(self):
        return self.active

#    def set_user(self, fullName, userName, eMail):
#        self.fullName = fullName
#        self.userName = userName
#        self.email = eMail

def get_user(userName):
    password = current_app.config['PASSWORDS'].get(user_id)
    user = User(user_id, password) if password else None
    if user is not None:
        user.is_admin = user.username in current_app.config['ADMIN_USERS']
    return user