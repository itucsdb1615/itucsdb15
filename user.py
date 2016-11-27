class User:
    def __init__(self, fullName, userName, eMail):
        self.fullName = fullName
        self.userName = userName
        self.email = eMail

    def get_userName(self):
        return self.userName

    def set_user(self, fullName, userName, eMail):
        self.fullName = fullName
        self.userName = userName
        self.email = eMail