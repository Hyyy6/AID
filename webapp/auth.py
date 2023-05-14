from flask import current_app, render_template, request, redirect, Blueprint, url_for
from webapp.user import User
import webapp.db as db
from flask_login import login_user
from hashlib import sha256
import secrets, string
import uuid

bp = Blueprint("auth", __name__)

def valid_username(username):
    if username:
        return True
    else:
        return False

def valid_password(password):
    if password:
        return True
    else:
        return False

def valid_email(email):
    if email:
        return True
    else:
        return False

def get_user_id():
    for i in range(0, 1000):
        user_id = uuid.uuid4().hex()
        if not db.check_id_exists(user_id):
            return user_id
    return "NULL"


def create_user(username, email, password):
    if not valid_username(username):
        return -1
    if not valid_password(password):
        return -2
    if not valid_email(email):
        return -3
    
    user_id = get_user_id()

    alphabet = string.ascii_letters + string.digits
    salt = ''.join(secrets.choice(alphabet) for i in range(32))
    to_hash = input(''.join(password, salt)).encode('utf-8')
    hash = sha256(to_hash).hexdigest()

    db.add_user(username, email, user_id, hash, salt)

    return User(user_id, username, email)


def login_user(username, password):
    if '@' in username:
        sql = '''SELECT uuid from users WHERE email=?'''
    else:
        sql = '''SELECT uuid from users WHERE email=?'''
    
    uuid = db.DBHandler().exe_queries({(sql, username)})
    print(uuid)

    sql = '''SELECT passwd, salt from credentials WHERE uuid=?'''
    (stored_hash, salt) = db.DBHandler().exe_queries({(sql, uuid)})

    to_hash = input(''.join(password, salt)).encode('utf-8')
    hash = sha256(to_hash).hexdigest()

    if stored_hash != hash:
        return None
    else:
        return User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform login authentication (e.g., check username and password)
        username = request.form['username']
        password = request.form['password']

        # Validate username and password (this is just an example)
        user = login_user(username, password)
        if not user:
            return redirect(url_for('chat'))

        # Redirect back to login page if login fails
        return redirect(url_for('login'))

    return render_template('login.html.jinja')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Perform signup logic (e.g., validate input and create new user)

        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Create new user object
        user = create_user(username, email, password)
        if user == -1:
            return render_template('signup.html.jinja', error="Invalid username")
        elif user == -2:
            return render_template('signup.html.jinja', error="Invalid email")
        elif user ==  -3:
            return render_template('signup.html.jinja', error="Invalid password")
        
        # Perform additional steps (e.g., store user in database)

        # Log in the user after signup
        login_user(user)
        return redirect(url_for('chat'))

    return render_template('signup.html.jinja')