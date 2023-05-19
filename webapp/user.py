### Class for holding user metadata and login state ###
from flask import current_app, session
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
            print("load user, set ses")
            print(current_app.config['SECRET_KEY'])
            print(current_app.db.get_db())
            result = current_app.db.exe_queries([(user_sql, (uuid, ))])[0]
            if not result:
                return None
            session['uuid'] = uuid
            name, email = result[0]
            print(name + " " + email)
        except Exception as exception:
            print(exception)
            return None

        return User(uuid, name, email)