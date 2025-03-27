from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store connected users (in memory - for production use a database)
connected_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('set_username')
def handle_set_username(username):
    if username.strip():
        connected_users[request.sid] = username
        emit('message', {'type': 'notification', 'data': f'{username} has joined the chat'}, broadcast=True)
        emit('user_list', {'users': list(connected_users.values())}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_users:
        username = connected_users[request.sid]
        del connected_users[request.sid]
        emit('message', {'type': 'notification', 'data': f'{username} has left the chat'}, broadcast=True)
        emit('user_list', {'users': list(connected_users.values())}, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(message):
    if request.sid in connected_users:
        username = connected_users[request.sid]
        emit('message', {
            'type': 'message',
            'username': username,
            'data': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
