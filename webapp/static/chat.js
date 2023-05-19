const form = document.querySelector('#message-form');
const chat = document.querySelector('#chat-content');
const diaryChatToggle = document.querySelector('#diary-chat-toggle');
const chatModeButton = document.querySelector('#chat-mode-button');
let chatMode = 'log';

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const messageInput = document.querySelector('#message-input');
  const message = messageInput.value;
  console.log(message);

  addMessage('You', message);

  if (chatMode === 'assistant') {
    // Send message to AI assistant chat
    sendToAssistant(message);
  } else {
    // Send message to diary chat
    sendToDiaryChat(message);
  }

  messageInput.value = '';
});

diaryChatToggle.addEventListener('click', () => {
  if (chatMode === 'assistant') {
    chatMode = 'log';
    diaryChatToggle.textContent = 'Switch to Conversation Mode';
    chatModeButton.textContent = 'Log Mode';
  } else {
    chatMode = 'assistant';
    diaryChatToggle.textContent = 'Switch to Log Mode';
    chatModeButton.textContent = 'Conversation Mode';
  }
});

function sendToAssistant(message) {
  fetch('/assistant/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: message })
  })
    .then(response => response.json())
    .then(reply => {
      console.log(reply);
      addMessage('Assistant', reply);
      showPopup();
    });
}

function sendToDiaryChat(message) {
  fetch('/diary_chat/send', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: message })
  })
    .then(response => response.json())
    .then(reply => {
      console.log(reply);
      addMessage('Diary Chat', reply);
      showPopup();
    });
}

function addMessage(user, message) {
  const p = document.createElement('p');
  p.innerHTML = `<strong>${user}:</strong> ${message}`;
  chat.appendChild(p);
  chat.scrollTop = chat.scrollHeight;
}

function showPopup() {
  const popup = document.getElementById('popup');
  popup.classList.remove('hidden');
  setTimeout(closePopup, 3000); // Close popup after 3 seconds
}

function closePopup() {
  const popup = document.getElementById('popup');
  popup.classList.add('hidden');
}
