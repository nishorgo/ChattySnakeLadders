import socket
import threading
from _thread import *
import json

from game import Game

HOST = '127.0.0.1'
GAME_PORT = 5555

games = {}
reset_request_count = 0
game_id_count = 0


def send_game_data(client, current_game, dice_result):
    """
    Send game data to a client.
    @param client - the client to send the data to
    @param current_game - the current game object
    @param dice_result - the result of the dice roll
    @return None
    """
    context = {
        'type': 'game_data',
        'dice_result': dice_result,
        'is_ready': current_game.is_ready,
        'total_players': len(current_game.get_players()),
        'current_turn': current_game.current_turn,
        'players': [
            {
                'name': player.get_name(),
                'serial': player.get_serial(),
                'token_color': player.get_token_color(),
                'position': player.get_position(),
                'rank': player.get_rank(),
            } for player in current_game.get_players()
        ],
    }

    try:
        json_data = json.dumps(context) + '\x00'
        client.sendall(json_data.encode())
    except Exception as e:
        print(e)
        exit()


def send_game_to_all_clients(current_game, dice_result=None):
    """
    Send the current game and dice result (if provided) to all clients connected to the players in the game.
    @param current_game - the current game object
    @param dice_result - the result of the dice roll (optional)
    @return None
    """
    for player in current_game.get_players():
        client = player.get_network()
        send_game_data(client, current_game, dice_result)


def handle_player_start_game_request(data, current_game):
    """
    Handle a player's request to start or reset the game.
    @param data - the data containing the player's name, serial, and request
    @param current_game - the current game object
    @return None
    """
    context = {
        'type': 'chat_data',
        'sender': 'server',
    }

    player_name = data.get('player_name')
    player_serial = data.get('player_serial')
    request = data.get('request')

    if request == 'reset':
        context['message'] = player_name + " has requested for reset.\n"

    elif request == 'start':
        context['message'] = player_name + " has requested to start the game with current number of players.\n"

    send_to_chat(current_game, context)
    current_game.handle_start_game_request(player_serial)
    send_game_to_all_clients(current_game)


def update_game_data(data, current_game):
    """
    Update the game data based on the received data and the current game state.
    @param data - the received data
    @param current_game - the current game state
    @return None
    """
    request = data.get('request', None)

    if request and len(current_game.get_players()) > 1:
        handle_player_start_game_request(data, current_game)

    elif request is None:
        player_serial = data.get('player_serial')
        dice_result = data.get('dice_result')

        current_player = current_game.get_players()[player_serial]

        if dice_result == 1:
            current_player.set_ready()

        current_position = current_player.get_position()
        next_position = current_game.board.get_next_position(current_position, dice_result)

        if current_game.can_move(current_player, next_position):
            current_game.move_player(current_player, next_position)

        if current_game.can_play():
            current_game.change_turn(dice_result)
        else:
            print("Game Ended")

        send_game_to_all_clients(current_game, dice_result)


def forward_chat_data(data, current_game):
    """
    Send chat data to all players in the current game.
    @param data - the chat data to be sent
    @param current_game - the current game object
    @return None
    """
    for player in current_game.get_players():
        client = player.get_network()
        try:
            client.sendall((json.dumps(data) + '\x00').encode())
        except Exception as e:
            print(e)


def handle_incoming_data(data, current_game):
    """
    Handle incoming data by checking its type. If the type is 'chat_data', forward the data to the appropriate function for processing. 
    Otherwise, update the game data using the provided data.
    @param data - the incoming data
    @param current_game - the current game state
    @return None
    """
    if data.get('type') == 'chat_data':
        forward_chat_data(data, current_game)
    else:
        update_game_data(data, current_game)


def listen_for_events(client, game_id):
    """
    Listen for events from a client for a specific game. Continuously receive data from the client and handle it accordingly.
    @param client - the client connection
    @param game_id - the ID of the game to listen for events
    @return None
    """
    json_data = b''
    while True:
        if game_id in games:
            current_game = games[game_id]

            try:
                chunk = client.recv(512)
                json_data += chunk

                while b'\x00' in json_data:
                    end_indx = json_data.index(b'\x00')
                    data = json_data[:end_indx]
                    json_data = json_data[end_indx + 1:]

                    handle_incoming_data(json.loads(data), current_game)
            except Exception as e:
                print(e)
                exit()
        else:
            print("Game not found")

    print('Connection Lost')

    if game_id_count in games:
        if len(current_game.get_players()) <= 1:
            del games[game_id_count]
            print("Closing game", game_id_count)

    client.close()


def send_to_chat(current_game, context):
    """
    Send a message to each player in the current game's network.
    @param current_game - the current game object
    @param context - the message to send
    @return None
    """
    for player in current_game.get_players():
        client = player.get_network()
        json_data = json.dumps(context) + '\x00'
        try:
            client.sendall(json_data.encode())
        except Exception as e:
            print(e)


def send_player_serial(client, game_id):
    """
    Send the player serial number to the client for a specific game.
    @param client - the client socket connection
    @param game_id - the ID of the game
    @return None
    """
    player_serial = len(games[game_id].get_players()) - 1
    data = {
        'player_serial': player_serial
    }
    try:
        client.sendall((json.dumps(data) + '\x00').encode())
    except Exception as e:
        print(e)
        exit()


def main():
    """
    The main function sets up a server socket and listens for incoming connections from clients. 
    Once a client connects, it receives the player's name and checks if a game is already in progress. 
    If not, it creates a new game and assigns the player to it. If a game is already in progress and there are less than 3 players, 
    the player is added to the existing game. If there are already 3 players in the game, a new game is created and the player is added to it. 
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Connecting the server on {HOST} {GAME_PORT}")
        server.bind((HOST, GAME_PORT))
    except Exception as e:
        print(f"Unable to bind to host {HOST} and port {GAME_PORT}")
        print(e)
        exit()

    server.listen(4)
    print("Server connected. Waiting for a player.")

    global game_id_count
    current_game_id = 0

    while True:
        client, address = server.accept()
        print(f"Connected to: {address}")

        try:
            player_name = json.loads(client.recv(512)).get('player_name')
            if player_name != '':
                print(f"{player_name} has joined")
        except Exception as e:
            print(e)
            exit()

        if game_id_count not in games:
            current_game_id = game_id_count
            games[current_game_id] = Game(game_id_count)
            games[current_game_id].set_new_player(player_name, client)
            print("Creating a new game...")
            send_player_serial(client, current_game_id)

        elif len(games[current_game_id].get_players()) == 3:
            current_game = games[current_game_id]
            current_game.set_new_player(player_name, client)

            current_game.initialize_game()
            game_id_count += 1

            send_player_serial(client, current_game_id)

            send_game_to_all_clients(current_game)

            print("GAME INITIALIZED")

        else:
            games[current_game_id].set_new_player(player_name, client)
            send_player_serial(client, current_game_id)

        context = {
            'type': 'chat_data',
            'sender': 'server',
            'message': player_name + " has joined\n"
        }
        send_to_chat(games[current_game_id], context)
        
        # Create a new thread that will execute the function `listen_for_events` with the given arguments `client` and `current_game_id`.
        threading.Thread(target=listen_for_events, args=(client, current_game_id)).start()


main()
