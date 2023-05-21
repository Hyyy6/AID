const diaryForm = document.querySelector('#diary-message-form');
const diaryChatContent = document.querySelector('#diary-chat-content');
const psychologistForm = document.querySelector('#psychologist-message-form');
const psychologistChatContent = document.querySelector('#psychologist-chat-content');
const diaryMessageInput = document.querySelector('#diary-message-input');
const diaryChatModeSelect = document.querySelector('#diary-chat-mode');
const diaryMessagesContainer = document.querySelector('#diary-messages-container');

// Diary Chat Assistant
diaryForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = diaryMessageInput.value;
  addMessage(diaryChatContent, 'You', message);
  
  // Determine the appropriate route based on the selected chat mode
  const chatMode = diaryChatModeSelect.value;
  const route = (chatMode === 'simple') ? '/diary-chat/simple' : '/diary-chat/conversation';
  
  console.log("SEND MSG")
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
    console.log(html_text)
    parser = new DOMParser()
    html = parser.parseFromString(html_text, 'text/html')
    diaryChatContent.appendChild(html.documentElement);
  })
  .catch((err) => console.log(err))

  diaryMessageInput.value = '';
});
// Psychologist Assistant
psychologistForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = psychologistMessageInput.value;
  addMessage(psychologistChatContent, 'You', message);
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

// Function to add a new message to the chat content
function addMessage(chatContent, sender, message) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message');
  messageElement.dataset.sender = sender;
  messageElement.textContent = `${sender}: ${message}`;
  chatContent.appendChild(messageElement);
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
  addMessage('You', messageText, psychologistChatContent);
});

// Add message to the specified chat
// function addMessage(user, message, chatContent) {
//   const p = document.createElement('p');
//   p.innerText = `${user}: ${message}`;
//   chatContent.appendChild(p);
//   chatContent.scrollTop = chatContent.scrollHeight;
// }

// Rest of the code...
