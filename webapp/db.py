import sqlite3
import os
import click
from flask import current_app, g
from hashlib import sha256
from flask.cli import with_appcontext

class DBHandler():
    # def __init__(self):
    #     return self
    db = "test"
    def init(self):
        if "db" not in g:
            print("db " + current_app.config["DATABASE"])
            self.db = sqlite3.connect(
                current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
            )
            self.db.row_factory = sqlite3.Row
            print(self.db)
            g.db = self.db
        return self

    def reset(self):
        print ("reset db")
        self.init()
        with current_app.open_resource(os.path.join(current_app.instance_path, "db/db_init")) as f:
            try:
                self.db.executescript(f.read().decode("utf8"))
            except Exception as err:
                print(type(err))
                print(err.args)
                print(err)

    def get_db(self):
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
        try:
            for (query, parameters) in entries:
                self.get_cursor().executemany(query, parameters)

            self.get_db().commit()
        except sqlite3.Error as error:
            self.get_db().rollback()
            return error


def add_user(username, email, uuid, hash, salt):
    """At this point all inputs are validated"""
    err = 0
    
    try:
        db_handle = DBHandler().get_db()
        db_cursor = db_handle.cursor()
        sql = '''INSERT INTO users (uuid, name, email) VALUES (?, ?, ?)'''
        params = (uuid, username, email)
        db_cursor.execute(sql, params)
        if not (err and db_cursor.lastrowid()):
            err = -1

        sql = '''INSERT INTO credentials (uuid, passwd, sald) VALUES (?, ?, ?)'''
        params = (uuid, hash, salt)
        db_cursor.execute(sql, params)
        if not (err and db_cursor.lastrowid()):
            err = -2
    except Exception as exception:
        err = exception

    if not err:
        err = True
        db_handle.commit()
    else:
        db_handle.rollback()
        
    return err

def check_id_exists(user_id):
    db_handle = DBHandler().get_db()
    db_cursor = DBHandler().get_cursor()
    sql = '''SELECT * FROM users WHERE user_id=?'''
    db_cursor.execute(sql, (user_id,))
    rows = db_handle.fetchall()
    if rows:
        return True
    else:
        return False

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    print("get_db")
    if "db" not in g:
        print("db " + current_app.config["DATABASE"])
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()

@click.command("init-db")
# @with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    print("init db from click")
    DBHandler().reset()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    print("init app db")
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)