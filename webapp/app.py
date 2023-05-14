import os
from flask import Flask
from flask_login import LoginManager
from flask_login import LoginManager
from .user import User


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    print(f'name {__name__}, inst path {app.instance_path}')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    # apply the blueprints to the app
    from webapp import auth
    app.register_blueprint(auth.bp)

    from webapp import chat
    app.register_blueprint(chat.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="auth.login")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @app.login_manager.user_loader
    def load_user(user_id):
    # Load user from user_id (e.g., fetch user from database)
    # Return the User object or None if not found
        return User.load_user(user_id)
    
    # register the database commands
    from webapp import db
    print('register db')
    db.init_app(app)

    return app