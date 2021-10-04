from data import write_data
from flask import Flask, render_template, redirect, request, session
from flask_socketio import SocketIO, send, emit
from models.database import create_room, add_second_player, delete_game, fetch_all_room_id, fetch_player1, fetch_player2, fetch_time_created
from decouple import config
from datetime import datetime
from time import sleep

app = Flask(__name__)
app.config['SECRET_KEY'] = config('FLASK_SECRET_KEY')
sleep(3)
socketio = SocketIO(app)

now = datetime.now()
created_on = now.strftime("%Y-%m-%d %H:%M:%S")



############################ HOME PAGE ################################


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/multiplayer-tic-tac-toe', methods=["GET", "POST"])
def tic_tac_toe():
    return render_template("tic-tac-toe.jinja")

########################## SOCKET CONNECTIONS #######################################################

# Create game rooms and save on a database (postgresql) or add players joining to a game room.
# Rooms will look like the example below. User id of whom created the room will be used the room id.
# Second user's name will be saved with their own id seperated by space.
# If a room is inactive for 33 minutes, the key will be deleted from the database.

#  id  |             room_id              | player1 |                 player2                 |     created_on
# -----+----------------------------------+---------+-----------------------------------------+---------------------
#  128 | 9f698f9b65054edfbb11337c1d93577f | george  | c6ca2e25c1a9472e80f3c91d81558945 lily   | 2021-09-28 17:43:45
#  129 | afe3f6ca933c4c03b98d4df61955fea8 | lily    | a2233334f2574003be8fabbcd27c28bf george | 2021-09-28 17:43:45
#  130 | 489bffb0fa964240933db03b5e3ec342 | lily    | 1a9142ead5e24a7f8feb737dcc4c8963 Susan  | 2021-09-28 17:43:45

@socketio.on("game_type")
def game_type(type):
    all_rooms = fetch_all_room_id()
    # for rooms in all_rooms:
    #     created_on = fetch_time_created()
    #     print(created_on[0])
    type = type.split("-")
    user_name = type[1]
    if type[0] == "new_game":
        game_id = request.sid
        create_room(game_id, user_name, created_on)
        emit('session_id', game_id, room=game_id)
    else:
        game_id = type[0]
        user_id = request.sid
        all_rooms = fetch_all_room_id()
        for rooms in all_rooms:
            if rooms[0][-10:] == game_id and fetch_player2(rooms)[0][0] != None:
                emit('session_id', "full", room=user_id)

            elif rooms[0][-10:] == game_id:
                player2 = user_id + " " + type[1]
                add_second_player(rooms[0], player2)
                emit('session_id', game_id, room=user_id)

            elif game_id != rooms[0][-10:]:
                emit('session_id', "none", room=user_id)

# Get the confirmation when the second player joins the game
@socketio.on('start_game')
def start_game(start):
    all_rooms = fetch_all_room_id()
    game_id = start.split("-")[0]
    message = start.split("-")[1]
    for room in all_rooms:
        if room[0][-10:] == game_id:
            socketio.send(message, room=room[0])

# Listenening for the play of 'X' and 'O' then broadcast it to the players in individual rooms
@socketio.on('message')
def receive_message_event(message):
    all_rooms = fetch_all_room_id()
    for rooms in all_rooms:
        try:
            if message == "restart" and (request.sid == (fetch_player2(rooms[0])[0][0].split(" "))[0] or request.sid == rooms[0]):
                room_1 = rooms[0]
                room_2 = (fetch_player2(rooms[0])[0][0].split(" "))[0]
                socketio.send("restart", room=room_1)
                socketio.send("restart", room=room_2)
        except AttributeError:
            print('Empty player2 section on the db')
            pass
        if request.sid == rooms[0]:
            room_1 = rooms[0]
            room_2 = (fetch_player2(rooms[0])[0][0].split(" "))[0]
            user_name = fetch_player1(rooms[0])[0][0]
            socketio.send(message, room=room_2)

            if(message == 'win'):
                socketio.send(f'{user_name} <br> WINS!!!', room=room_1)
                socketio.send(f"{user_name} <br> WINS!!!", room=room_2)
                sleep(0.1)
                socketio.send(f"{user_name} <br> WINS!!!", room=room_1)
                socketio.send(f"{user_name} <br> WINS!!!", room=room_2)
            elif(message == 'draw'):
                socketio.send('draw', room=room_1)
                socketio.send('draw', room=room_2)
                sleep(0.1)
                socketio.send('draw', room=room_1)
                socketio.send('draw', room=room_2)
        # (fetch_player2(rooms[0])[0][0].split(" "))[0] == Id of Player_2
        elif fetch_player2(rooms)[0][0] != None and request.sid == (fetch_player2(rooms[0])[0][0].split(" "))[0]:
            room_1 = rooms[0]
            room_2 = (fetch_player2(rooms[0])[0][0].split(" "))[0]
            user_name = (fetch_player2(rooms[0])[0][0].split(" "))[1]
            socketio.send(message, room=room_1)
            print("player2 sent: " + message)

            if(message == 'win'):
                socketio.send(f"{user_name} <br> WINS!!!", room=room_1)
                socketio.send(f"{user_name} <br> WINS!!!", room=room_2)
                sleep(0.1)
                socketio.send(f"{user_name} <br> WINS!!!", room=room_1)
                socketio.send(f"{user_name} <br> WINS!!!", room=room_2)
            elif(message == 'draw'):
                socketio.send('draw', room=room_1)
                socketio.send('draw', room=room_2)
                sleep(0.1)
                socketio.send('draw', room=room_1)
                socketio.send('draw', room=room_2)

# Listening for the chat message and broadcast it to all clients
@socketio.on('chat_message')
def send_chat_message(chat_message):
    all_rooms = fetch_all_room_id()
    for rooms in all_rooms:
        if request.sid == rooms[0]:
            room_1 = rooms[0]
            room_2 = (fetch_player2(rooms[0])[0][0].split(" "))[0]
            user_1 = fetch_player1(rooms[0])[0][0]
            socketio.emit('private_chat_message',
                          f"{user_1}: {chat_message}", room=room_1)
            socketio.emit('private_chat_message',
                          f"{user_1}: {chat_message}", room=room_2)
        elif fetch_player2(rooms)[0][0] != None and request.sid == (fetch_player2(rooms[0])[0][0].split(" "))[0]:
            room_1 = rooms[0]
            room_2 = (fetch_player2(rooms[0])[0][0].split(" "))[0]
            user_2 = (fetch_player2(rooms[0])[0][0].split(" "))[1]
            socketio.emit('private_chat_message',
                          f"{user_2}: {chat_message}", room=room_1)
            socketio.emit('private_chat_message',
                          f"{user_2}: {chat_message}", room=room_2)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9000)
    #  ssl_context=('cert.pem', 'key.pem')