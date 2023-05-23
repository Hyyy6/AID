from flask import current_app, render_template, request, redirect, Blueprint, url_for, make_response
from webapp.user import User
import webapp.db as db
from hashlib import sha256
import secrets, string
import uuid
from flask_login import login_user

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
    alphabet = string.ascii_letters + string.digits
    salt = ''.join(secrets.choice(alphabet) for i in range(32))
    to_hash = ''.join(password+salt).encode('utf-8')
    hash = sha256(to_hash).hexdigest()
    print(f"new user uuid {user_id} salt {salt}")

    if not User.add_user(username, email, user_id, hash, salt):
        return -4

    return User(user_id, username, email)


def check_credentials(username, password):
    if '@' in username:
        sql = '''SELECT uuid from users WHERE email=?'''
    else:
        sql = '''SELECT uuid from users WHERE name=?'''
    

    print(f"check user {username}")
    print(f"db - {current_app.db}")
    rows = current_app.db.exe_queries([(sql, (username, ))])[0]
    if not rows:
        print("no such user")
        return 0
    row = rows[0]
    uuid = row[0]
    print(uuid)

    sql = '''SELECT passwd, salt from credentials WHERE uuid=?'''
    rows = current_app.db.exe_queries([(sql, (uuid,))])[0]
    if len(rows) != 1:
        print("Internal user db err")
        return 0
    
    stored_hash = rows[0][0]
    salt = rows[0][1]
    print(f"hash - {stored_hash}, salt - {salt}")
    to_hash = ''.join(password+salt).encode('utf-8')
    hash = sha256(to_hash).hexdigest()

    if stored_hash != hash:
        return 0
    else:
        # with current_app.app_context():
            # sessions.SecureCookieSession.get()
        return 1


@bp.route('/test_form', methods=['POST'])
def test():
    print("test post request " + request.method)
    return redirect(url_for('.login'))

@bp.route('/login', methods=['GET'])
def login():
    # print(request.get_json())
    print(request.method + " login")
    return render_template('login.html.jinja')

@bp.route('/login/enter', methods=['POST'])
def submit_login():
    print(request.method)
    print("login")
    print(request.headers)
    print(request.form.get('username'))
    # Perform login authentication (e.g., check username and password)
    username = request.form['username']
    password = request.form['password']

    # Validate username and password (this is just an example)
    print(username, password)
    ret = check_credentials(username, password)
    # print(user.email)
    if ret:
        response = make_response(redirect(url_for('home.index')))
        user = User.fetch_user_by_name(username)
        ret = login_user(user)
        # response.set_cookie()
        return response
    # else:
        

    # print("login " + user.)
    # Redirect back to login page if login fails
    print(url_for('.login'))
    return redirect(url_for('.login'))
    
    # return redirect(url_for('.login'))


@bp.route('/signup', methods=['GET'])
def signup():
    print("signup " + request.method)
    return render_template('signup.html.jinja')

@bp.route('/signup/enter', methods=['POST'])
def submit_signup():
    print("submit signup " + request.method)
    if request.method == 'POST':
        # Perform signup logic (e.g., validate input and create new user)

        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Create new user object
        # Perform additional steps (e.g., store user in database)
        print(f"create user, db - {current_app.db}")
        user = create_user(username, email, password)
        if user == -1:
            return render_template('signup.html.jinja', resp_err="Invalid username")
        elif user == -2:
            return render_template('signup.html.jinja', resp_err="Invalid email")
        elif user ==  -3:
            return render_template('signup.html.jinja', resp_err="Invalid password")
        elif user == -4 or not user:
            return render_template('signup.html.jinja', resp_err="Internal error")
        print(user.email)
        # Log in the user after signup
        ret = login_user(user)
        if ret:
            print(f"user {user.username} is auth - {user.is_authenticated()}")
            return redirect(url_for('home.index'))
            # return render_template(webapp.home)
        else:
            print(f"could not login {user.username}")
            return render_template('signup.html.jinja', resp_error="internal login error")
        
    print(url_for('url for signup'))
    return redirect(url_for('signup'))