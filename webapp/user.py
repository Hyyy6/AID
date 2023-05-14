### Class for holding user metadata and login state ###
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.uuid = user_id
        self.username = username
        self.email = email

    def load_user(uuid):
        return 