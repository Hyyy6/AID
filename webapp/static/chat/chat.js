const diaryForm = document.querySelector('#diary-message-form');
const diaryChatContent = document.querySelector('#diary-chat-content');
const psychologistForm = document.querySelector('#psychologist-message-form');
const psychologistChatContent = document.querySelector('#psychologist-chat-content');
const diaryMessageInput = document.querySelector('#diary-message-input');
const diaryChatModeSelect = document.querySelector('#diary-chat-mode');
const diaryMessagesContainer = document.querySelector('#diary-messages-container');

function getRoute(node) {
  try {
    route_node = node.closest('[route]')
    // console.log(route_node.outerHTML)
    route = route_node.getAttribute("route")
  } catch(e) {
    route = "/error/"
    console.log(e);
  }
  return route
}

// Diary Chat Assistant
diaryForm.addEventListener('submit', (event) => {
  console.log(document.cookie);
  event.preventDefault();
  const message = diaryMessageInput.value;
  addMessage(diaryChatContent, 'user', message);
  
  // Determine the appropriate route based on the selected chat mode
  const chatMode = diaryChatModeSelect.value;
  // const base_route = getRoute(this)
  element = event.target
  console.log(element)
  base_route = element.closest('[route]').getAttribute('route') + "/send"
  const route = (chatMode === 'simple') ? base_route + '/simple' : base_route + '/conversation';
  
  console.log(`SEND MSG to ${route}`)
  console.log(diaryForm)
  // console.log,
  // form = new FormData(diaryForm)
  // console.log(form.get('message'))
  
  // console.log(JSON.stringify(form.get('message')))
  
  console.log(JSON.stringify(message))
  // console.log(diaryChatContent)
  fetch(route, {
    method: 'POST',
    body: JSON.stringify(message),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then((response) => response.text())
  .then((html_text) => {
    // console.log(html_text)
    parser = new DOMParser()
    html = parser.parseFromString(html_text, 'text/html')
    messages = html.querySelectorAll('.message')
    messages.forEach(message => {
      diaryChatContent.append(message)
    })
    diaryChatContent.scrollTop = diaryChatContent.scrollHeight
  })
  .catch((err) => console.log(err))

  diaryMessageInput.value = '';
});
// Psychologist Assistant
psychologistForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = psychologistMessageInput.value;
  addMessage(psychologistChatContent, 'user', message);
  psychologistMessageInput.value = '';

  // Collect all the diary messages and attach them to the psychologist's message
  const diaryMessages = diaryMessagesContainer.querySelectorAll('.message');
  const diaryMessageIds = Array.from(diaryMessages).map(message => message.dataset.messageId);

  const payload = {
    message,
    diaryMessages: diaryMessageIds
  };

  fetch('/psychologist-chat', {
    method: 'POST',
    body: JSON.stringify(payload),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(reply => {
      addMessage(psychologistChatContent, 'Psychologist', reply);
      showPopup();
    });
});

// Function to add a message to the chat window
function addMessage(chatContent, sender, content) {
  // const chatContent = document.querySelector('#chat-content');

  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${sender.toLowerCase()}`;

  const contentP = document.createElement('p');
  contentP.textContent = `${content}`;

  // messageDiv.appendChild(timestampSpan);
  messageDiv.appendChild(contentP);
  chatContent.appendChild(messageDiv);

  // Scroll to the bottom of the chat window
  chatContent.scrollTop = chatContent.scrollHeight;
}

// Function to get the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'
function getCurrentTimestamp() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}


// Function to show the popup
function showPopup() {
  const popup = document.getElementById('popup');
  popup.classList.remove('hidden');
  setTimeout(closePopup, 3000); // Close the popup after 3 seconds
}

// Function to close the popup
function closePopup() {
  const popup = document.getElementById('popup');
  popup.classList.add('hidden');
}


// const diaryChatContent = document.querySelector('#diary-chat-content');
// const psychologistChatContent = document.querySelector('#psychologist-chat-content');

// Enable dragging of messages from the diary chat
diaryChatContent.addEventListener('dragstart', (event) => {
  const message = event.target;
  event.dataTransfer.setData('text/plain', message.innerText);
});

// Enable dropping of messages to the psychologist chat
psychologistChatContent.addEventListener('dragover', (event) => {
  event.preventDefault();
});

psychologistChatContent.addEventListener('drop', (event) => {
  event.preventDefault();
  const messageText = event.dataTransfer.getData('text/plain');
  addMessage( psychologistChatContent, 'You', messageText);
});

async function loadChats() {
  console.log("LOAD CHATS")
  chats = document.querySelectorAll('.chat-content')
  chats.forEach(chat => {
    // console.log(chat)
    loadChatHistory(chat)
  })
}

async function loadChatHistory(chat) {
  // chats = document.getElementsByClassName
  // console.log(chat.outerHTML)
  let route = getRoute(chat)
  console.log("route to load chat: " + route)
  try {
    console.log(`load chat for ${route} into ${chat.id}`)
    const response = await fetch(route + '/chat/history');
    if (response.status == 200) {
      chatHistory = await response.text();
      // console.log(`loaded ${chatHistory}} for ${route}`)
      if (chatHistory) {
        parser = new DOMParser()
        html = parser.parseFromString(chatHistory, 'text/html')
        messages = html.querySelectorAll('.message')
        chat.innerHTML = ""
        messages.forEach(message => {
          // console.log(message)
          chat.append(message)
          chat.scrollTop = chat.scrollHeight
        })
      }
    } else if (response.status == 204) {
      console.log("empty history for " + route)
    }
  }
  catch (error) {
    console.log('Error loading chat history:', error);
  }
}

window.addEventListener('DOMContentLoaded', (event) => {
  loadChats()
  console.log("DOM loaded")
  // const messageInput = document.getElementById('diary-message-input');

  diaryMessageInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      if (!event.shiftKey) {
        // diaryForm.submit(); // Handle sending the message
      } else {
        event.preventDefault(); // Prevent form submission  
        // Append a new line to the input value
        // console.log(event.target)

        // console.log(this.value)
        this.value += '\n';
        // console.log(this.value)
      }
    }
  });

  diaryMessageInput.addEventListener('input', function (event) {
    console.log(this)
    console.log(event)
    console.log(this.value)
    this.style.height = 'auto';
    this.style.height = `${this.scrollHeight}px`;



    const diaryChatContent = document.getElementById('diary-chat-content');
    diaryChatContent.scrollTop = diaryChatContent.scrollHeight; // Scroll to the bottom
  });

  // clear_diary = document.getElementById("clear-diary-chat")
  console.log(clear_diary)
  clear_diary.addEventListener('click', function (event) {
    route = getRoute(this) + "/clear"

    fetch(route, {
      method: 'POST',
    })
      .then((response) => response.status)
      .then((status) => {
        console.log(status)
        if (status == 200) {
          diaryChatContent.innerHTML = '';
        } else {
          alert("could not clear chat"
          )
        }
      })
      .catch((err) => console.log(err))

  })
});


const clear_diary = document.getElementById("clear-diary-chat")


console.log(diaryForm);