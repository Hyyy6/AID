import openai
from flask import current_app, render_template, request, flash, Response, Blueprint, session, make_response
from flask_login import login_required
from webapp.utils.stub_chat import stub_chat, Message
from .user import User, ChatMessage
from .utils.log import MyAppLogger, CustomLoggerWrapper
import json
import pickle

bp = Blueprint("chat", __name__)

user_threads = {}

logger = MyAppLogger('app_logger')
logger.set_log_level('DEBUG')
logg = CustomLoggerWrapper("chat")

@bp.route('/chat', methods=['GET'])
@login_required
def index():
    logger.defualt("get chat " + request.method)
    logg.error("get chat with stack")
    # logg.critical("get chat with stack")
    flash("chat", "info")
    return render_template('chat/chat.html.jinja')

@bp.route('/<chat_type>/export', methods=['GET'])
@login_required
def export_thread(chat_type, mode="simple"):
    return "OK"

@bp.route('/<chat_type>/import', methods=['POST'])
@login_required
def import_thread(chat_type, mode="simple"):
    return "OK"

@bp.route('/<chat_type>/send', methods=['POST'])
@login_required
def send(chat_type, mode="simple"):
    debug = current_app.config['DEBUG'] # enable debug
    logger.defualt(f"receive chat type {chat_type} msg (debug {debug})")

    user_id = session['uuid']
    user_request = request.get_json()

    chat_mode = user_request['mode']
    msg_content = user_request['message']
    role = user_request['role']
    user = User.fetch_user_by_id(user_id)
    logger.defualt(f' user {user} id {user.get_id()} name {user.get_name()}')
    new_message = ChatMessage(user_id, msg_content, chat_mode, role, chat_type)
    response = None
    if mode == "conversation":
        if user_id not in user_threads:
            # current_app.db.get_cursor().execute("INSERT INTO users (name) VALUES (?)", (f'user_{user_id}',))
            # Create a new thread for this user and initialize it with the rules from the file
            # try:
                # with open(os.path.join(current_app.config['RULES_DIR'], f'/models/{chat_type}_rules.txt'), 'r') as f:
                    # rules = f.read()
            rules = get_rules(current_app.db, user, chat_type)
            logger.defualt(rules)
            # except Exception as e:
            #     logger.log_with_metadata(100, f'could not send chat ', True)
            #     logger.log_with_metadata(100, e)
            thread = []
            user_threads[user_id] = thread
            rule_message = ChatMessage(user_id, rules, chat_mode, role, chat_type)
            thread.append(rule_message)
        else: #user in threads
            # new_message = ChatMessage(user_id, msg_content, chat_mode, role, chat_type)
            append_chat(current_app.db, user, new_message.spread())
            thread = user_threads[user_id]
            thread.append(new_message)
        # Continue the thread with the user's message and return the response
        if not debug:
            response = openai.ChatCompletion.create(
                model=current_app.config['MODEL_ID'],
                messages=user_threads[user_id],
                max_tokens=1024,
                n=1,
                stop=None,
                user=user_id
            )
            print(json.dumps(response))
            # print(response.choices)
            # print(response.choices[0].message.content)
        else:
            # print(user_threads[user_id])
            response = stub_chat("test", "test")
        new_message = ChatMessage(user_id, response.choices[0].message.content, chat_mode, "assistant", chat_type)
        user_threads[user_id].append(new_message)
        append_chat(current_app.db, user, new_message.spread())
        logger.defualt(f'append as {response.choices[0].message.role}')
    elif mode == "simple": ### mode simple ###
        if user_id not in user_threads:
            thread = []
            user_threads[user_id] = thread
        logger.info("add to simple chat")
    # new_message = ChatMessage(user_id, msg_content, chat_mode, role, chat_type)
        append_chat(current_app.db, user, new_message.spread())
        thread = user_threads[user_id]
        thread.append(new_message)
        # logger.log_def(user_threads[user_id])


        # if not debug:
        #     # logger.log_def(user_threads[user_id])
        #     new_content_msg = Message('user', message)

        #     user_threads[user_id].append(new_content_msg)
        #     response = openai.ChatCompletion.create(
        #         model=current_app.config['MODEL_ID'],
        #         messages=user_threads[user_id],
        #         max_tokens=1024,
        #         n=1,
        #         stop=None,
        #     )
        # else:
        #     response = stub_chat(f"answer for {message}", "assistant")

        # print(response)
        # user_threads[user_id].append(response.choices[0].message)
        # logger.log_def(response.choices)
        # logger.log_def(response.choices[0].message.content)
        # # db_log_append(user_id, message, response.choices[0].message.content, db_handle)
        # message = ChatMessage(user_id, response.choices[0].message.content, "assistant", "diary")
        # append_chat(current_app.db, user, message.spread())

        chat_history = render_template("chat/message.html.jinja", chat_messages=[new_message])
        respBodyJson = {
            'metadata': "a",
            'messages': chat_history
            }
        respBody = json.dumps(respBodyJson)
        # import flask
        # flask.re
        response = Response(respBody, status = 200, mimetype='application/json')
        return chat_history
    elif mode == "simple":
        return "OK"


@bp.route('/<chat_type>/chat/history', methods=['GET'])
@login_required
def get_history(chat_type):
    user = User.fetch_user_by_id(session['uuid'])
    logger.defualt(f'get for {user.uuid} {chat_type}')
    messages = load_thread(current_app.db, user, chat_type)
    # logger.log_def(len(messages))
    logger.defualt(messages)
    # resp = Response()
    if not messages:
        logger.error("empty history")
        return Response(status=204)
    return render_template("chat/message.html.jinja", chat_messages=messages)

@bp.route('/<chat_type>/clear/<dst>', methods=['POST'])
@login_required
def clear_history(chat_type, dst):
    if dst in "chat":
        user = User.fetch_user_by_id(session['uuid'])
        ret = clear_chat(current_app.db, user, chat_type)
        if not ret:
            return Response(status=500)
        else:
            return Response(status=200)
    if dst in "thread":
        return "OK"

@bp.route('/<chat_type>/rules/get', methods=['GET'])
def get_file(chat_type):
    logger.defualt("get rules")
    rules = None
    try:
        user = User.fetch_user_by_id(session['uuid'])
        rules = get_rules(current_app.db, user, chat_type)
        # rules = rows[0]
    except Exception as e:
        logger.error(100, e)

    if not rules:
        return Response("Can't get chat rules", status=404)
    
    logger.defualt(f'rules get {rules}')
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
def set_rules(chat_type):
    # logger.log_def(request.headers)
    # logger.log_def(len(request.form))
    # logger.log_def(request.data)
    user_id = session['uuid']
    file = request.form['file']
    logger.defualt(file)
    if file:
        try:
            user = User.fetch_user_by_id(session['uuid'])
            ret = save_rules(current_app.db, user, chat_type, file)
            response = openai.ChatCompletion.create(
                    model=current_app.config['MODEL_ID'],
                    messages=[
                        {"role": "system", "content": file}
                    ],
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    user=user_id
                )
            logger.defualt(response.choices[0].message.content)
        except Exception as e:
            logger.log_with_metadata(100, e, True)
            return Response("Failed to set rules", status=500)
        return "File uploaded successfully."
    else:
        return "No file uploaded."
    


def load_chat(db, user, chat_type):
    load_chat_sql = '''SELECT user_id, sender, message, chat_type, created from chats where user_id=? AND chat_type=?'''
    result = None
    messages = []

    try:
        logger.defualt(f'load {user.username} {chat_type} chats')
        # result = current_app.db.exe_queries([(load_chat_sql, (self.uuid, chat_type))])
        result = db.exe_queries([(load_chat_sql, (user.uuid, chat_type, ))])[0]
        logger.defualt(len(result))
        if not result or len(result) == 0:
            logger.log_with_metadata(40, 'error loading chat')
            return None
        for message_db in result:
            # logger.log_def(message_db)
            # logger.log_def(*message_db)
            messages.append(ChatMessage(*message_db))
            # logger.log_def(messages[-1].content)

    except Exception as e:
        logger.log_with_metadata(100, f"Could not load {user.username} chat", True)
        logger.log_with_metadata(100, e)
        return None
    return messages

def load_thread(db, user, chat_type):
    load_thread_sql = '''SELECT sender, message, chat_type, chat_mode, created from chats where user_id=? AND chat_type=?'''
    result = None
    messages = []

    try:
        logger.defualt(f'load {user.username} {chat_type} chats db {db}')
        # result = current_app.db.exe_queries([(load_chat_sql, (self.uuid, chat_type))])
        result = db.exe_queries([(load_thread_sql, (user.uuid, chat_type, ))])[0]
        logger.defualt(len(result))
        if not result or len(result) == 0:
            logger.log_with_metadata(40, 'error loading chat')
            return None
        for message_db in result:
            # logger.log_def(message_db)
            # logger.log_def(*message_db)
            messages.append(ChatMessage(*message_db))
            # logger.log_def(messages[-1].content)

    except Exception as e:
        logger.log_with_metadata(100, f"Could not load {user.username} chat", True)
        logger.log_with_metadata(100, e)
        return None
    return messages

def append_chat(db, user, data):
    add_chat_sql = '''INSERT INTO chats (user_id, sender, chat_mode, message, chat_type) VALUES (?,?,?,?,?)''' #append 
    result = None

    try:
        logger.defualt(f'append {user.username} chat')
        result = db.exe_queries([(add_chat_sql, data)])
    except Exception as e:
        logger.log_with_metadata(100, f'Could not append to {user.username} chat', True)
        logger.log_with_metadata(100, e)
        return result
    return result

def clear_chat(db, user, chat_type):
    clear_chat_sql = '''DELETE FROM chats WHERE user_id=? AND chat_type=?'''
    ret = None
    # logger.log_def(f'clear {chat_type} chat')
    try:
    # db_handle = DBHandler.get_cursor()
        ret = db.exe_queries([(clear_chat_sql, (user.get_id(), chat_type, ))])
        logger.log_with_metadata(30, f'clear {chat_type} chat for {user.username}; ret - {ret}')
    except Exception as e:
        logger.log_with_metadata(100, e, True)
    return ret

def save_rules(db, user, chat_type, rules):
    insert_rules_sql = '''INSERT OR IGNORE INTO chat_rules (rules, user_id, chat_type) VALUES (?, ?, ?)'''
    save_rules_sql = '''UPDATE chat_rules SET rules = ? WHERE user_id = ? AND chat_type = ?'''
    ret = None
    logger.defualt(f'save ${chat_type} rules')
    try:
        ret = db.exe_queries([
            (insert_rules_sql, (rules, user.uuid, chat_type,)),
            (save_rules_sql, (rules, user.uuid, chat_type,)),
            ])
        logger.defualt(f'ret ${ret}')
    except Exception as e:
        logger.log_with_metadata(100, e, True)
    return ret

def get_rules(db, user, chat_type):
    get_rules_sql = '''SELECT rules FROM chat_rules WHERE user_id = ? AND chat_type = ?'''
    ret = None
    logger.defualt(f'get {chat_type} rules')
    try:
        query_ret = db.exe_queries([(get_rules_sql, (user.uuid, chat_type,))])[0] #rows
        rules = query_ret[0][0] #first row, first (and only) column
        logger.defualt(f'ret {rules}')
    except Exception as e:
        logger.log_with_metadata(100, e, True)
    return rules


@bp.route('/debug', methods=['POST'])
def set_debug():
    debug = request.json
    logger.log_with_metadata(30, f' set debug to {debug["debug"]}')
    # logger.log_def(debug['debug'])
    current_app.config['DEBUG'] = debug['debug']
    return f'Set debug to {debug}'



# Write archive order
def write_archive_order(db, archive_id, order):
    order_blob = pickle.dumps(order)
    db.get_cursor().execute('UPDATE archives SET "order" = ? WHERE id = ?', (order_blob, archive_id))
    db.commit()

# Read archive order
def read_archive_order(db, archive_id):
    db.get_cursor.execute('SELECT "order" FROM archives WHERE id = ?', (archive_id,))
    result = db.get_cursor.fetchone()
    if result is not None and result[0] is not None:
        order_blob = result[0]
        order = pickle.loads(order_blob)
        return order
    return []

# Write chat order
def write_chat_order(db, chat_id, order):
    order_blob = pickle.dumps(order)
    db.get_cursor.execute('UPDATE user_chats SET "order" = ? WHERE id = ?', (order_blob, chat_id))
    db.commit()

# Read chat order
def read_chat_order(db, chat_id):
    db.get_cursor.execute('SELECT "order" FROM user_chats WHERE id = ?', (chat_id,))
    result = db.get_cursor.fetchone()
    if result is not None and result[0] is not None:
        order_blob = result[0]
        order = pickle.loads(order_blob)
        return order
    return []

def get_messages_by_order(db, order):
    order_str = ','.join(str(id) for id in order)
    query = f'SELECT * FROM messages WHERE id IN ({order_str}) ORDER BY FIELD(id, {order_str})'
    db.get_cursor.execute(query)
    result = db.get_cursor.fetchall()
    return result