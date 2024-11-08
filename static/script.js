function setApiKey() {
  const apiKey = document.getElementById('api-key-input').value;
  if (!apiKey) {
      alert('Please enter an API key');
      return;
  }

  fetch('/set-api-key', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ api_key: apiKey })
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert(data.error);
      } else {
          document.getElementById('api-key-section').classList.add('hidden');
          document.getElementById('chat-section').classList.remove('hidden');
          addMessage('Welcome! How can I help you today?', 'assistant');
      }
  })
  .catch(error => {
      alert('Error setting API key: ' + error);
  });
}

function sendMessage() {
  const messageInput = document.getElementById('message-input');
  const message = messageInput.value.trim();

  if (!message) return;

  addMessage(message, 'user');
  messageInput.value = '';

  fetch('/chat', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: message })
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert(data.error);
      } else {
          addMessage(data.message, 'assistant');
      }
  })
  .catch(error => {
      alert('Error sending message: ' + error);
  });
}

function addMessage(message, role) {
  const chatMessages = document.getElementById('chat-messages');
  const messageElement = document.createElement('div');
  messageElement.className = `message ${role}-message`;
  messageElement.textContent = message;
  chatMessages.appendChild(messageElement);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle Enter key in message input
document.getElementById('message-input').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') {
      sendMessage();
  }
});