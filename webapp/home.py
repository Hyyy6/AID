import openai
from flask import current_app, render_template, request, flash, Response, Blueprint, session
from webapp.db import get_db
from webapp.utils.stub_chat import stub_chat
# from stub_chat import

# template_dir = os.path.join(dir_path, "templates")



# app = Flask(__name__)
bp = Blueprint("home", __name__)

threads = {}

def db_log_append(user_id, user_message, assistant_message, db_handle):
    db_handle.execute("SELECT history FROM chats WHERE user_id=?", (user_id,))
    result = db_handle.fetchone()[0]
    # print(ret)
    # result = ret[0]
    print(result)
    
    chat_log = result + "User:" + user_message + "\n"
    chat_log += chat_log + "Assistant:" + assistant_message + "\n"
    print(chat_log)
    db_handle.execute("INSERT INTO chats (user_id, history) VALUES (?, ?)", (user_id, chat_log))

@bp.route('/chat', methods=['GET'])
def index():
    print("get request, render chat")
    flash("welcome", "info")
    return render_template('chat.html.jinja')

@bp.route('/chat/send', methods=['POST'])
def send():
    debug = current_app.config['DEBUG'] # enable debug
    db_con = current_app.db.get_db()
    db_handle = db_con.cursor()
    print("receive chat msg")
    print(request)
    print(request.form)
    user_id = session['uuid']
    message = request.form['message']

    if user_id not in threads:
        # db_handle.execute("INSERT INTO users (name) VALUES (?)", (f'user_{user_id}',))
        db_handle.execute("INSERT INTO chats (user_id, history) VALUES (?, ?)", (user_id, ""))
        # Create a new thread for this user and initialize it with the rules from the file
        with open(current_app.config['RULES_FILE'], 'r') as f:
            rules = f.read()
            print(rules)
        if not debug:
            threads[user_id] = openai.ChatCompletion.create(
                model=current_app.config['MODEL_ID'],
                messages=[
                    {"role": "system", "content": rules}
                ],
                max_tokens=1024,
                n=1,
                stop=None,
                user=user_id
            )
        else:
            threads[user_id] = stub_chat("test", "test")
    # Continue the thread with the user's message and return the response
    print(threads[user_id])


    if not debug:
        response = openai.ChatCompletion.create(
            model=current_app.config['MODEL_ID'],
            messages=[
                {"role": "user", "content": threads[user_id].choices[0].message.content + message}
            ],
            max_tokens=1024,
            n=1,
            stop=None
        )
    else:
        response = stub_chat(f"answer for {message}", "assistant")

    threads[user_id] = response
    print(response.choices)
    print(response.choices[0].message.content)
    db_log_append(user_id, message, response.choices[0].message.content, db_handle)
    return Response(response.choices[0].message.content)

