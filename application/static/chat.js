// Connect to the SocketIO server
const socket = io.connect();

// Function to send a message
function sendMessage() {
    const message = document.getElementById('message').value;
    if (message.trim() === "") return;

    const sender = "You";  // Can dynamically change based on the user

    // Emit the message to the server
    socket.emit('send_message', { sender: sender, message: message });

    // Clear the input field
    document.getElementById('message').value = '';
}

// Function to display messages
function displayMessage(data) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(data.sender === "You" ? 'sender' : 'receiver');
    messageDiv.textContent = `${data.sender}: ${data.message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Listen for incoming messages
socket.on('receive_message', function(data) {
    displayMessage(data);
});

// Listen for the initial set of messages when a client connects
socket.on('load_messages', function(data) {
    data.messages.forEach(displayMessage);
});
