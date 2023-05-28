### Class for holding user metadata and login state ###
from flask import current_app, session
from flask_login import UserMixin, current_user
from .db import DBHandler

class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.uuid = user_id
        self.id = self.uuid
        self.username = username
        self.email = email

        self.is_auth = 1

    def is_authenticated(self):
        return self.is_auth

    def is_active(self):   
        return self.is_active           

    def is_anonymous(self):
        return self.is_anonymous          

    def get_id(self):         
        return str(self.id)
    
    def get_user():
        return current_user
    
    def get_name(self):
        return self.username

    def fetch_user_by_id(uuid):
        user_sql = '''SELECT name, email from users WHERE uuid=?'''

        try:
            # print("load user, set ses")
            # print(current_app.config['SECRET_KEY'])
            # print(current_app.db)
            # # db = DBHandler
            # print(current_app.db.get_db())
            # result = current_app.db.exe_queries([(user_sql, (uuid, ))])[0]
            result = current_app.db.exe_queries([(user_sql, (uuid, ))])[0]
            if not result:
                return None
            # session['uuid'] = uuid
            name, email = result[0]
            print("return " + name + " " + email)
        except Exception as exception:
            print(exception)
            return None

        return User(uuid, name, email)
    
    def fetch_user_by_name(name):
        user_sql = '''SELECT uuid, email from users WHERE name=?'''

        try:
            result = current_app.db.exe_queries([(user_sql, (name, ))])[0]
            if not result:
                return None
            # session['uuid'] = uuid
            uuid, email = result[0]
            print("return " + uuid + " " + email)
        except Exception as exception:
            print(exception)
            return None

        return User(uuid, name, email)
    
    def add_user(username, email, uuid, hash, salt):
        """At this point all inputs are validated"""
        err = 0
        
        try:
            db_handle = current_app.db.get_db()
            db_cursor = current_app.db.get_cursor()
            print(f"add user, db handle - {db_handle}, cursor - {db_cursor}")
            sql = '''INSERT INTO users (uuid, name, email) VALUES (?, ?, ?)'''
            params = (uuid, username, email)
            db_cursor.execute(sql, params)
            if not (err and db_cursor.lastrowid()):
                err = -1

            print("insert new credentials")
            sql = '''INSERT INTO credentials (uuid, passwd, salt) VALUES (?, ?, ?)'''
            params = (uuid, hash, salt)
            db_cursor.execute(sql, params)
            if not (err and db_cursor.lastrowid):
                err = -2
        except Exception as exception:
            err = exception
            print(type(err))
            print(err.args)
            print(err)

        if err != 0:
            print("succ")
            err = True
            db_handle.commit()
        else:
            db_handle.rollback()
            
        return err

    def check_id_exists(user_id):
        db_cursor = current_app.db.get_cursor()
        sql = '''SELECT * FROM users WHERE uuid=?'''
        rows = []
        try:
            db_cursor.execute(sql, (user_id,))
            rows = db_cursor.fetchall()
        except Exception as err:
            print(err)
        if rows:
            return True
        else:
            return False
        

class ChatMessage():
    def __init__(self, user_id, content, sender, type, timestamp=None):
        self.user_id = user_id
        self.content = content
        self.sender = sender
        self.type = type
        self.timestamp = timestamp

    def spread(self):
        return (self.user_id, self.content, self.sender, self.type, )
