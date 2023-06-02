import sqlite3
import os
import click
from flask import current_app, Flask
from hashlib import sha256
from .utils.log import MyAppLogger

logger = MyAppLogger('db_logger', 'DEBUG')
# logger.disable
# logger.setLevel(MyAppLogger.read_level())

class DBHandler():
    def __init__(self):
        self.db = None

    def init(self):
            
        logger.log_def("create db connection")
        db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
        )
        self.db = db
        self.db.row_factory = sqlite3.Row
        logger.log_def(self.db)

        return self

    def reset(self):
        self.init()
        logger.log_def(f"reset db {self.db}")
        with current_app.open_resource(os.path.join(current_app.instance_path, "db/db_init")) as f:
            try:
                ret = self.db.executescript(f.read().decode("utf8"))
                return ret
            except Exception as err:
                # logger.log_w(type(err))
                logger.log_with_metadata(100, "Failed to reset DB", True)
                logger.log_with_metadata(100, err)
            return None

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
            logger.log_with_metadata("Can't execute queries - no db attached")
            return []
        try:
            ret = []
            logger.log_def(f"exe queries on db {self.db}")
            for query, parameters in entries:
                logger.log_def(f"execute {query} with {parameters}")
                cursor = self.get_cursor()
                cursor.execute(query, parameters)
                rows = cursor.fetchall()
                for row in rows:
                    logger.log_def(row[0])
                ret.append(rows)

            self.get_db().commit()
            logger.log_def(f'data len {len(ret)}; data {ret}')
            return ret
        except sqlite3.Error as error:
            self.get_db().rollback()
            return error

def check_id_exists(user_id):
    db_cursor = current_app.db.get_cursor()
    sql = '''SELECT * FROM users WHERE uuid=?'''
    rows = []
    try:
        db_cursor.execute(sql, (user_id,))
        rows = db_cursor.fetchall()
    except Exception as err:
        logger.log_with_metadata(100, "Failed to check if id unique: " + err, True)
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
    logger.log_def("init db from click")
    if not DBHandler().reset():
        click.echo("Failed to initialize the database")
        return
    logger.log_def(DBHandler().db)
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    logger.log_def("init app db")
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)