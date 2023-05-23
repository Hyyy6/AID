import openai
from flask import current_app, render_template, request, flash, Response, Blueprint, session, send_file
from flask_login import login_required
from webapp.utils.stub_chat import stub_chat
from .user import User, ChatMessage
import os

bp = Blueprint("chat", __name__)

threads = {}


@bp.route('/chat', methods=['GET', 'POST'])
@login_required
def index():
    print("get chat " + request.method)
    flash("chat", "info")
    return render_template('chat/chat.html.jinja')

@bp.route('/<chat_type>/send/<mode>', methods=['POST'])
@login_required
def send(chat_type, mode="simple"):
    debug = current_app.config['DEBUG'] # enable debug
    print(f"receive chat type {chat_type} msg")

    user_id = session['uuid']
    message = request.get_json()

    user = User.fetch_user_by_id(user_id)
    print(user, user.get_id(), user.get_name())
    user.append_chat(ChatMessage(user_id, message, "user", chat_type).spread())
    if user_id not in threads:
        # db_handle.execute("INSERT INTO users (name) VALUES (?)", (f'user_{user_id}',))
        # Create a new thread for this user and initialize it with the rules from the file
        try:
            with open(os.path.join(current_app.config['RULES_DIR'], f'/models/{chat_type}_rules.txt'), 'r') as f:
                rules = f.read()
                print(rules)
        except Exception as e:
            print(f'could not send chat ')
            print(e)

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
    chat_history = render_template("chat/message.html.jinja", chat_messages=[message])
    # import flask
    # flask.re
    return chat_history


@bp.route('/<chat_type>/chat/history', methods=['GET'])
@login_required
def get_history(chat_type):
    user = User.fetch_user_by_id(session['uuid'])
    print(user.uuid + chat_type)
    messages = user.load_chat(chat_type)
    # print(messages)
    return render_template("chat/message.html.jinja", chat_messages=messages)

@bp.route('/<chat_type>/clear', methods=['POST'])
@login_required
def clear_history(chat_type):
    user = User.fetch_user_by_id(session['uuid'])
    ret = user.clear_chat(chat_type)
    if not ret:
        return Response(status=500)
    else:
        return Response(status=200)

@bp.route('/<chat_type>/rules/get', methods=['GET'])
def get_file(chat_type):
    filename = f'rules_{chat_type}.txt'
    filepath = os.path.join(current_app.config['RULES_DIR'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "File not found."

@bp.route('/<chat_type>/rules/set', methods=['POST'])
def set_file(chat_type):
    print(request.headers)
    print(len(request.form))
    file = request.form['file']
    print(file)
    if file:
        # filename = f'rules_{chat_type}.txt'
        # filepath = os.path.join(current_app.config['RULES_DIR'], filename)
        # file.save(filepath)
        return "File uploaded successfully."
    else:
        return "No file uploaded."