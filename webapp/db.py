import sqlite3
import os
import click
from flask import current_app, Flask
from hashlib import sha256

class DBHandler():
    def __init__(self):
        self.db = None

    def init(self):
            
        print("create db connection")
        db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
        )
        self.db = db
        self.db.row_factory = sqlite3.Row
        print(self.db)

        return self

    def reset(self):
        self.init()
        print (f"reset db {self.db}")
        with current_app.open_resource(os.path.join(current_app.instance_path, "db/db_init")) as f:
            try:
                self.db.executescript(f.read().decode("utf8"))
            except Exception as err:
                print(type(err))
                print(err.args)
                print(err)

    def get_db(self):
        # print(self.db)
        return self.db

    def get_cursor(self):
        if self.db:
            return self.db.cursor()
        else:
            return None
        
    def close_db(self):
        if self.db:
            self.db.close

    def exe_queries(self, entries):
        if not self.db:
            print("Can't execute queries - no db attached")
            return []
        try:
            ret = []
            print(f"exe queries on db {self.db}")
            for query, parameters in entries:
                print(f"execute {query} with {parameters}")
                cursor = self.get_cursor()
                cursor.execute(query, parameters)
                rows = cursor.fetchall()
                # for row in rows:
                #     print(row[0])
                ret.append(rows)

            self.get_db().commit()
            print(f'data len {len(ret)}')
            return ret
        except sqlite3.Error as error:
            self.get_db().rollback()
            return error


def add_user(username, email, uuid, hash, salt):
    """At this point all inputs are validated"""
    err = 0
    
    try:
        db_handle = current_app.db.get_db()
        db_cursor = db_handle.cursor()
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


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    DBHandler().close_db()

@click.command("init-db")
# @with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    print("init db from click")
    DBHandler().reset()
    print(DBHandler().db)
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    print("init app db")
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)