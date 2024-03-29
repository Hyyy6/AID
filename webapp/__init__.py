import os
from .app import init_app
from flask import Flask

def my_func():
    a = 1
    return a


def main():
    print("main")
    app = Flask(__name__, instance_relative_config=True)
    app_dir = os.path.dirname(os.path.realpath(__file__))
    test_config = os.path.join(app_dir, "test_conf.py")
    prod_config = os.path.join(app.instance_path, "config.py")
    
    if (os.path.exists(test_config)):
        print("conf from test conf")
        # app.config.from_pyfile(test_config)
    elif (os.path.exists(prod_config)):
        print("conf from prod conf")
        app.config.from_pyfile(prod_config)
    else:
        print("conf from mapping")
        app.config.from_mapping(
            # a default secret that should be overridden by instance config
            SECRET_KEY="dev",
            SESSION_TYPE="filesystem",
            # store the database in the instance folder
            DATABASE=os.path.join(app.instance_path, "db/user.db"),
            MODEL_ID = "gpt-3.5-turbo",
            # RULES_DIR = os.path.join(app.instance_path, "model/rules"),
        )

    app = init_app(app)
    print(app.config['SECRET_KEY'])
    # register the database commands
    from webapp import db
    with app.app_context():
        print('register db')
        db.init_app(app)
        app.db = db.DBHandler()
        print('init db')
        app.db.init()

    print(app.db)
        
    return app
