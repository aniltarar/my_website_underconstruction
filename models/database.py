from data import fetch_data_with_param, write_data, fetch_data

def create_room(room_id , player1, datetime):
    write_data("INSERT INTO game_rooms (room_id, player1, created_on) VALUES (%s , %s, %s);", [room_id, player1, datetime])

def add_second_player(room_id, player2):
    write_data("UPDATE game_rooms SET player2=%s WHERE room_id=%s;", [player2, room_id])

def fetch_all_room_id():
    result = fetch_data("SELECT room_id FROM game_rooms;")
    return result

def fetch_player2(room_id):
    result = fetch_data_with_param("SELECT player2 FROM game_rooms WHERE room_id = %s;", [room_id])
    return result

def fetch_player1(room_id):
    result = fetch_data_with_param("SELECT player1 FROM game_rooms WHERE room_id = %s;", [room_id])
    return result

def delete_game(room_id):
    write_data("DELETE FROM game_rooms WHERE room_id=%s;", [room_id])

def fetch_time_created():
    result = fetch_data("SELECT created_on FROM game_rooms;")
    return result