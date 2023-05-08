import openai
from flask import Flask, render_template, request
import os

debug = 1

dir_path = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(dir_path, "templates")

MODEL_ID = "gpt-3.5-turbo"
RULES_FILE = os.path.join(dir_path, "../model/rules.txt")

app = Flask(__name__)

threads = {}

@app.route('/')
def index():
    print("get request, render char")
    return render_template('chat.html')

@app.route('/send', methods=['POST'])
def send():
    print("receive chat msg")
    print(request)
    print(request.form)
    user_id = request.form['user-id']
    message = request.form['message']
    if (debug):
        print(f'id - {user_id}\nmsg - {message}')
        return f're: {message}'
    # fi debug
    if user_id not in threads:
        # Create a new thread for this user and initialize it with the rules from the file
        with open(RULES_FILE, 'r') as f:
            rules = f.read()
            print(rules)
        threads[user_id] = openai.ChatCompletion.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": rules}
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            user=user_id
        )
    # Continue the thread with the user's message and return the response
    print(threads[user_id].choices[0])

    response = openai.ChatCompletion.create(
        model=MODEL_ID,
        messages=[
            {"role": "user", "content": threads[user_id].choices[0].message.content + message}
        ],
        max_tokens=1024,
        n=1,
        stop=None
    )
    threads[user_id] = response
    print(response.choices[0].message.content)
    return response.choices[0].message.content

def get_reply(message):
    # Your logic to generate a reply goes here
    # For this example, we'll just return a hardcoded reply
    return "I'm sorry, I didn't understand that."

if __name__ == '__main__':
    app.run(debug=True)