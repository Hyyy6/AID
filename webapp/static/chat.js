const form = document.querySelector('#message-form');
const chat = document.querySelector('#chat');

function rand_id(max) {
    console.log(`test rand ${Math.random()}`)
    return Math.floor(Math.random() * max)
}

function getUserId() {

    console.log(document.cookie)
    id = document.cookie.match(new RegExp(`(^| )user_id=([^;]+)`))?.at(2);

    if (!id || id == "NaN") {
        id = rand_id(1024);
        console.log(id)
        document.cookie = `user_id=${id}`
    }
    console.log(`get id ${id}`);
    return id;
}

function chat_send() {
    const form = document.querySelector('#message-form');
    const chat = document.querySelector('#chat');
    
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const messageInput = document.querySelector('#message-input');
        const message = messageInput.value;
        // messageInput.value = '';
        console.log(message);
        document.cookie = "abc=3"
        console.log(document.cookie)

        addMessage('You', message);
        id = getUserId()
        console.log(id)
        formData = new FormData(form);
        formData.append('user-id', id);
        console.log(form)
        fetch('/send', {
            method: 'POST',
            body: formData
        })
            .then((response) => {
                console.log(response.clone());
                console.log(response.clone().text())
                return response.text()
            })
            .then((reply) => {
                console.log(reply);
                addMessage('Bot', reply);
            })
    });

    function addMessage(user, message) {
        const p = document.createElement('p');
        p.innerHTML = `<strong>${user}:</strong> ${message}`;
        chat.appendChild(p);
    }
}

chat_send()
