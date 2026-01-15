const socket = io();

// DOM elements
const messageInput = document.getElementById('messageInput');
const messageList = document.getElementById('messageList');
const sendButton = document.getElementById('sendButton');

// Send message
sendButton.addEventListener('click', () => {
    const message = messageInput.value;
    if (message) {
        socket.emit('sendMessage', message);
        messageInput.value = '';
    }
});

// Receive message
socket.on('receiveMessage', (message) => {
    const listItem = document.createElement('li');
    listItem.textContent = message;
    messageList.appendChild(listItem);
});

// Handle enter key for sending messages
messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendButton.click();
    }
});