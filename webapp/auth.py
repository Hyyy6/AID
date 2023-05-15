from flask import current_app, render_template, request, redirect, Blueprint, url_for, Response
from webapp.user import User
import webapp.db as db
from flask_login import login_user
from hashlib import sha256
import secrets, string
import uuid
import webapp.chat

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
        user_id = uuid.uuid4().hex
        with current_app.app_context():
            if not db.check_id_exists(user_id):
                return user_id
    return "NULL"


def create_user(username: str, email: str, password: str) -> User:
    if not valid_username(username):
        return -1
    if not valid_password(password):
        return -2
    if not valid_email(email):
        return -3
    
    user_id = get_user_id()
    print(f"new user uuid {user_id}")
    alphabet = string.ascii_letters + string.digits
    salt = ''.join(secrets.choice(alphabet) for i in range(32))
    to_hash = input(''.join(password+salt)).encode('utf-8')
    hash = sha256(to_hash).hexdigest()

    if not db.add_user(username, email, user_id, hash, salt):
        return -4

    return User(user_id, username, email)


def login_user(username, password):
    if '@' in username:
        sql = '''SELECT uuid from users WHERE email=?'''
    else:
        sql = '''SELECT uuid from users WHERE name=?'''
    

    print(f"login user {username}")
    print(f"db - {current_app.db.get_db()}")
    rows = current_app.db.exe_queries([(sql, (username, ))])[0]
    row = rows[0]
    uuid = row[0]
    print(uuid)

    sql = '''SELECT passwd, salt from credentials WHERE uuid=?'''
    rows = current_app.db.exe_queries([(sql, (uuid,))])[0]
    if len(rows) != 1:
        print("Internal user db err")
        return None
    
    stored_hash = rows[0][0]
    salt = rows[0][1]
    print(f"hash - {stored_hash}, salt - {salt}")
    to_hash = input(''.join(password+salt)).encode('utf-8')
    hash = sha256(to_hash).hexdigest()

    if stored_hash != hash:
        return None
    else:
        with current_app.app_context():
            return User.load_user(uuid)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    if request.method == 'POST':
        # Perform login authentication (e.g., check username and password)
        username = request.form['username']
        password = request.form['password']

        # Validate username and password (this is just an example)
        user = login_user(username, password)
        if user:
            return redirect(url_for('webapp.chat.chat'))

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
        print(f"create user, db - {current_app.db}")
        user = create_user(username, email, password)
        if user == -1:
            return render_template('signup.html.jinja', error="Invalid username")
        elif user == -2:
            return render_template('signup.html.jinja', error="Invalid email")
        elif user ==  -3:
            return render_template('signup.html.jinja', error="Invalid password")
        elif user == -4:
            return render_template('signup.html.jinja', error="Internal error")
        
        # Perform additional steps (e.g., store user in database)

        # Log in the user after signup
        user = login_user(username, password)
        if user:
            return redirect(url_for('webapp.chat.chat'))
        else:
            return render_template('signup.html.jinja', error="internal login error")

    return render_template('signup.html.jinja')