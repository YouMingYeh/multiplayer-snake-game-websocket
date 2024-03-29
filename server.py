from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from MultiplayerSnakeGame import MultiplayerSnakeGame
import json
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
game = MultiplayerSnakeGame()

players = {}
game_active = True
next_player_id = 0
FRAME_RATE = 0.5

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

def register_player(sid, player_id):
    global game, players
    if player_id in players.values():
        print(f"Player ID {player_id} is already in use.")
        return None
    game.spawn_snake(player_id)
    players[sid] = player_id
    return player_id

def unregister_player(sid):
    global players, game
    player_id = players.pop(sid, None)
    if player_id is not None:
        game.remove_snake(player_id)

@socketio.on('connect')
def handle_connect():
    print("New connection:", request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print("Connection closed:", request.sid)
    unregister_player(request.sid)

@socketio.on('register')
def handle_register(data):
    print("Registering player:", data["player_id"])
    player_id = register_player(request.sid, data["player_id"])
    if player_id is not None:
        emit('register', {"type": "register", "player_id": player_id})
    else:
        emit('register_failed')

@socketio.on('register')
def handle_register(data):
    player_id = register_player(request.sid, data["player_id"])
    if player_id is not None:
        emit('register', {"type": "register", "player_id": player_id})
    else:
        emit('register_failed')

@socketio.on('move')
def handle_move(data):
    global game, players
    player_id = players[request.sid]
    direction = (0, 0)
    if data["direction"] == "up":
        direction = (0, -1)
    elif data["direction"] == "down":
        direction = (0, 1)
    elif data["direction"] == "left":
        direction = (-1, 0)
    elif data["direction"] == "right":
        direction = (1, 0)
    game.change_direction(player_id, direction)

@socketio.on('exit')
def handle_exit():
    disconnect(request.sid)

def game_loop():
    global game_active, game
    while game_active:
        socketio.sleep(FRAME_RATE)
        game.update()
        broadcast_game_state()

def broadcast_game_state():
    global game
    snakes_pos = {snake.player_id: {"body": snake.body, "direction": snake.direction} for snake in game.snakes}
    foods_pos = [food.position for food in game.foods]
    state = json.dumps({"type": "state", "map": game.map, "snakes_pos": snakes_pos, "foods_pos": foods_pos})
    socketio.emit('state', state, broadcast=True)

socketio.start_background_task(target=game_loop)
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
if __name__ == '__main__':
    
    socketio.run(app, debug=True, host='localhost', port=3000)
