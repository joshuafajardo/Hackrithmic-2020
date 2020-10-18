from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import chess
import chess.variant
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AOPHROETNKATLNLFBNAGNPAG'
socketio = SocketIO(app, cors_allowed_origins="*")
user_ids = {}


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on('connect')
def handle_connect():
    global user_ids
    print('connected to ', request.sid)
    user_ids.setdefault(request.sid, chess.variant.AtomicBoard())

@socketio.on('playerMove')
def handle_move(move):
    global user_ids
    print(move)
    board = user_ids[request.sid]
    if board.is_game_over():
        emit('move_validation', {'valid': False})
    game_move = chess.Move(chess.parse_square(move['from_square']), chess.parse_square(move['to_square']), promotion=5)
    if game_move in board.legal_moves:
        board.push(random.choice(list(board.legal_moves)))
        emit('botMove', {'fen': board.fen()})
    else:
        emit('move_validation', {'valid': False})

@socketio.on('disconnect')
def handle_disconnect():
    global user_ids
    if request.sid in user_ids:
        print('user deleted')
        del user_ids[request.sid]
    print('user left')


@socketio.on_error()
def error_handler(e):
    print('Error!')
    print(e)
    

if __name__ == '__main__':
    socketio.run(app)