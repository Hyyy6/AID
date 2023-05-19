import os
from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from .user import User


def init_app(app):
    """Create and configure an instance of the Flask application."""
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

    from webapp import home
    app.register_blueprint(home.bp)

    print("SECRET KEY")
    print(app.config['SECRET_KEY'])

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
        with app.app_context():
            return User.load_user(user_id)

    Session(app)



    return app