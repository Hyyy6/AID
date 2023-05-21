import openai
from flask import current_app, render_template, request, flash, Response, Blueprint, session
from flask_login import login_required
from webapp.utils.stub_chat import stub_chat
from .user import User, ChatMessage

bp = Blueprint("chat", __name__)

threads = {}

@bp.route('/chat', methods=['GET', 'POST'])
@login_required
def index():
    print("get chat " + request.method)
    flash("chat", "info")
    return render_template('chat/chat.html.jinja')

@bp.route('/diary-chat/<mode>', methods=['POST'])
@login_required
def send(mode="simple"):
    debug = current_app.config['DEBUG'] # enable debug
    print("receive chat msg")

    user_id = session['uuid']
    message = request.get_json()

    user = User.fetch_user(user_id)
    print(user, user.get_id(), user.get_name())
    user.append_chat(ChatMessage(user_id, message, "user", "diary").spread())
    if user_id not in threads:
        # db_handle.execute("INSERT INTO users (name) VALUES (?)", (f'user_{user_id}',))
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
    # db_log_append(user_id, message, response.choices[0].message.content, db_handle)
    message = ChatMessage(user_id, response.choices[0].message.content, "assistant", "diary")
    user.append_chat(message.spread())
    return render_template("chat/message.html.jinja", chat_messages=[message])

