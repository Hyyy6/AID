### Class for holding user metadata and login state ###
from flask_login import UserMixin
from .db import DBHandler

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.uuid = user_id
        self.username = username
        self.email = email

    def load_user(uuid):
        user_sql = '''SELECT name, email from users WHERE uuid=?'''

        try:
            (name, email) = DBHandler.exe_queries({(user_sql, uuid)})[0]
        except Exception as exception:
            print(exception)
            return None

        return User(uuid, name, email)