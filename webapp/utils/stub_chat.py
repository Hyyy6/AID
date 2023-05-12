class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class Choice:
    def __init__(self, message, finish_reason, index):
        self.message = message
        self.finish_reason = finish_reason
        self.index = index

class ChatResponse:
    def __init__(self, id, object_type, created, model, usage, choices):
        self.id = id
        self.object = object_type
        self.created = created
        self.model = model
        self.usage = usage
        self.choices = choices

def stub_chat(msg, role):
    # create a single example choice with the given role and message content
    message = Message(role, msg)
    choice = Choice(message, 'stop', 0)

    # create the response object with the single choice
    response = ChatResponse(
        id='chatcmpl-6p9XYPYSTTRi0xEviKjjilqrWU2Ve',
        object_type='chat.completion',
        created=1677649420,
        model='gpt-3.5-turbo',
        usage={'prompt_tokens': 56, 'completion_tokens': 31, 'total_tokens': 87},
        choices=[choice]
    )

    # return the response
    return response