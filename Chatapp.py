from flask import Flask, render_template_string, request, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

users = {}
theme_color = "#6200EA"  # Default theme color

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            text-align: center;
        }
        input[type="text"] {
            padding: 10px;
            margin: 10px;
            width: 200px;
        }
        button {
            padding: 10px 20px;
            background-color: {{ theme_color }};
            color: white;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Login</h1>
        <form action="/chat" method="POST">
            <input type="text" name="username" placeholder="Enter your username" required />
            <br />
            <button type="submit">Join Chat</button>
        </form>
    </div>
</body>
</html>
''', theme_color=theme_color)

@app.route('/chat', methods=['POST'])
def chat():
    username = request.form['username']
    session['username'] = username
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Chat</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .navbar {
            background-color: {{ theme_color }};
            color: white;
            padding: 10px;
            display: flex;
            align-items: center;
        }
        .navbar .menu {
            font-size: 24px;
            cursor: pointer;
            margin-right: 20px;
        }
        .navbar h1 {
            margin: 0;
            flex-grow: 1;
        }
        .chat-container {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding: 10px;
        }
        .messages {
            flex-grow: 1;
            overflow-y: auto;
        }
        .message {
            margin: 5px 0;
        }
        .message .username {
            font-size: 12px;
            color: gray;
        }
        .message .bubble {
            display: inline-block;
            padding: 10px;
            border-radius: 20px;
        }
        .message.me .bubble {
            background-color: {{ theme_color }};
            color: white;
            align-self: flex-end;
        }
        .message.them .bubble {
            background-color: #E0E0E0;
            align-self: flex-start;
        }
        .message-input {
            display: flex;
            align-items: center;
            border-top: 1px solid #E0E0E0;
            padding: 10px;
        }
        .message-input input {
            flex-grow: 1;
            padding: 10px;
            border: none;
            border-radius: 20px;
            margin-right: 10px;
        }
        .message-input button {
            background-color: {{ theme_color }};
            color: white;
            padding: 10px;
            border: none;
            border-radius: 50%;
            cursor: pointer;
        }
        .sidebar {
            height: 100%;
            width: 0;
            position: fixed;
            z-index: 1;
            top: 0;
            left: 0;
            background-color: #111;
            overflow-x: hidden;
            transition: 0.5s;
            padding-top: 60px;
        }
        .sidebar a {
            padding: 8px 8px 8px 32px;
            text-decoration: none;
            font-size: 25px;
            color: #818181;
            display: block;
            transition: 0.3s;
        }
        .sidebar a:hover {
            color: #f1f1f1;
        }
        .sidebar .closebtn {
            position: absolute;
            top: 0;
            right: 25px;
            font-size: 36px;
            margin-left: 50px;
        }
        .open-sidebar {
            cursor: pointer;
            display: inline-block;
            margin: 15px;
        }
        .status {
            font-size: 14px;
            color: #999;
            display: block;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="menu" onclick="openNav()">☰</div>
        <h1>Chat</h1>
    </div>
    <div id="sidebar" class="sidebar">
        <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
        <a href="#">Online Users</a>
        <ul id="online-users"></ul>
        <a href="#" onclick="changeTheme()">Change Theme</a>
    </div>
    <div class="chat-container">
        <div id="messages" class="messages"></div>
        <div class="message-input">
            <input id="message-input" type="text" placeholder="Type a message..." />
            <button id="send-button">➤</button>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script>
        var socket = io();
        var username = "{{ username }}";
        var room = "main";
        socket.emit('join', {username: username, room: room});

        document.getElementById('send-button').addEventListener('click', function() {
            var input = document.getElementById('message-input');
            var message = input.value;
            if (message.trim() !== "") {
                socket.emit('message', {username: username, msg: message});
                input.value = "";
                addMessage("me", message);
            }
        });

        socket.on('message', function(data) {
            addMessage(data.user, data.msg);
        });

        socket.on('update_users', function(users) {
            var onlineUsers = document.getElementById('online-users');
            onlineUsers.innerHTML = '';
            users.forEach(function(user) {
                var li = document.createElement('li');
                li.textContent = user.username;
                if (user.online) {
                    li.innerHTML += ' <span class="status">(online)</span>';
                }
                onlineUsers.appendChild(li);
            });
        });

        function addMessage(user, message) {
            var messages = document.getElementById('messages');
            var messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (user === username ? 'me' : 'them');

            var usernameDiv = document.createElement('div');
            usernameDiv.className = 'username';
            usernameDiv.innerText = user;

            var bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'bubble';
            bubbleDiv.innerText = message;

            messageDiv.appendChild(usernameDiv);
            messageDiv.appendChild(bubbleDiv);
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function openNav() {
            document.getElementById("sidebar").style.width = "250px";
        }

        function closeNav() {
            document.getElementById("sidebar").style.width = "0";
        }

        function changeTheme() {
            var newColor = prompt("Enter a new theme color (hex code):", "{{ theme_color }}");
            if (newColor) {
                socket.emit('change_theme', newColor);
            }
        }

        socket.on('theme_changed', function(color) {
            document.documentElement.style.setProperty('--theme-color', color);
        });
    </script>
</body>
</html>
''', username=username, theme_color=theme_color)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    users[username] = {'room': room, 'online': True}
    send(f'{username} has entered the room.', to=room)
    emit('update_users', list(users.values()), to=room)

@socketio.on('message')
def on_message(data):
    room = users[data['username']]['room']
    emit('message', {'user': data['username'], 'msg': data['msg']}, to=room)

@socketio.on('change_theme')
def on_change_theme(color):
    global theme_color
    theme_color = color
    emit('theme_changed', color, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    username = session.get('username')
    if username in users:
        room = users[username]['room']
        users[username]['online'] = False
        send(f'{username} has left the room.', to=room)
        emit('update_users', list(users.values()), to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)