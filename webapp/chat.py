import openai
from flask import current_app, render_template, request, flash, Response, Blueprint, session, make_response
from flask_login import login_required
from webapp.utils.stub_chat import stub_chat
from .user import User, ChatMessage
import os

bp = Blueprint("chat", __name__)

threads = {}


@bp.route('/chat', methods=['GET'])
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
    append_chat(current_app.db, user, ChatMessage(user_id, message, "user", chat_type).spread())
    if user_id not in threads:
        # current_app.db.get_cursor().execute("INSERT INTO users (name) VALUES (?)", (f'user_{user_id}',))
        # Create a new thread for this user and initialize it with the rules from the file
        try:
            # with open(os.path.join(current_app.config['RULES_DIR'], f'/models/{chat_type}_rules.txt'), 'r') as f:
                # rules = f.read()
            with get_rules(current_app.db, user, chat_type) as rules:
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
    append_chat(current_app.db, user, message.spread())
    chat_history = render_template("chat/message.html.jinja", chat_messages=[message])
    # import flask
    # flask.re
    return chat_history


@bp.route('/<chat_type>/chat/history', methods=['GET'])
@login_required
def get_history(chat_type):
    user = User.fetch_user_by_id(session['uuid'])
    print(f'get for {user.uuid} {chat_type}')
    messages = load_chat(current_app.db, user, chat_type)
    # print(len(messages))
    print(messages)
    # resp = Response()
    if not messages:
        print("empty history")
        return Response(status=204)
    return render_template("chat/message.html.jinja", chat_messages=messages)

@bp.route('/<chat_type>/clear', methods=['POST'])
@login_required
def clear_history(chat_type):
    user = User.fetch_user_by_id(session['uuid'])
    ret = clear_chat(current_app.db, user, chat_type)
    if not ret:
        return Response(status=500)
    else:
        return Response(status=200)

@bp.route('/<chat_type>/rules/get', methods=['GET'])
def get_file(chat_type):
    print("get rules")
    rules = None
    try:
        user = User.fetch_user_by_id(session['uuid'])
        rules = get_rules(current_app.db, user, chat_type)
        # rules = rows[0]
    except Exception as e:
        print(e)

    if not rules:
        return Response("Can't get chat rules", status=404)
    
    print(f'rules get {rules}')
    response = make_response(rules, 200)
    response.mimetype = 'text/plain'
    return response
    # filename = f'rules_{chat_type}.txt'
    # filepath = os.path.join(current_app.config['RULES_DIR'], filename)
    # if os.path.exists(filepath):
    #     return send_file(filepath, as_attachment=True)
    # else:
    #     return "File not found."

@bp.route('/<chat_type>/rules/set', methods=['POST'])
def set_file(chat_type):
    # print(request.headers)
    # print(len(request.form))
    # print(request.data)
    file = request.form['file']
    print(file)
    if file:
        try:
            user = User.fetch_user_by_id(session['uuid'])
            ret = save_rules(current_app.db, user, chat_type, file)
        except Exception as e:
            print(e)
        return "File uploaded successfully."
    else:
        return "No file uploaded."
    


def load_chat(db, user, chat_type):
    load_chat_sql = '''SELECT user_id, sender, message, chat_type, created from chats where user_id=? AND chat_type=?'''
    result = None
    messages = []

    try:
        print(f'load {user.username} {chat_type} chats')
        # result = current_app.db.exe_queries([(load_chat_sql, (self.uuid, chat_type))])
        result = db.exe_queries([(load_chat_sql, (user.uuid, chat_type, ))])[0]
        print(len(result))
        if not result or len(result) == 0:
            print('error loading chat')
            return None
        for message_db in result:
            # print(message_db)
            # print(*message_db)
            messages.append(ChatMessage(*message_db))
            # print(messages[-1].content)

    except Exception as e:
        print(f"Could not load {user.username} chat")
        print(e)
        return None
    return messages

def append_chat(db, user, data):
    add_chat_sql = '''INSERT INTO chats (user_id, sender, message, chat_type) VALUES (?,?,?,?)'''
    result = None

    try:
        print(f'append {user.username} chat')
        result = db.exe_queries([(add_chat_sql, data)])
    except Exception as e:
        print(f'Could not append to {user.username} chat')
        print(e)
        return result
    return result

def clear_chat(db, user, chat_type):
    clear_chat_sql = '''DELETE FROM chats WHERE user_id=? AND chat_type=?'''
    ret = None
    print(f'clear {chat_type} chat')
    try:
    # db_handle = DBHandler.get_cursor()
        ret = db.exe_queries([(clear_chat_sql, (user.get_id(), chat_type, ))])
        print(f'clear {chat_type} chat for {user.username}; ret - {ret}')
    except Exception as e:
        print(e)
    return ret

def save_rules(db, user, chat_type, rules):
    insert_rules_sql = '''INSERT OR IGNORE INTO chat_rules (rules, user_id, chat_type) VALUES (?, ?, ?)'''
    save_rules_sql = '''UPDATE chat_rules SET rules = ? WHERE user_id = ? AND chat_type = ?'''
    ret = None
    print(f'save ${chat_type} rules')
    try:
        ret = db.exe_queries([
            (insert_rules_sql, (rules, user.uuid, chat_type,)),
            (save_rules_sql, (rules, user.uuid, chat_type,)),
            ])
        print(f'ret ${ret}')
    except Exception as e:
        print(e)
    return ret

def get_rules(db, user, chat_type):
    get_rules_sql = '''SELECT rules FROM chat_rules WHERE user_id = ? AND chat_type = ?'''
    ret = None
    print(f'get {chat_type} rules')
    try:
        query_ret = db.exe_queries([(get_rules_sql, (user.uuid, chat_type,))])[0] #rows
        rules = query_ret[0][0] #first row, first (and only) column
        print(f'ret {rules}')
    except Exception as e:
        print(e)
    return rules