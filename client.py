import socket
import threading
import json
import random

import tkinter as tk
from tkinter import font, messagebox, scrolledtext
from PIL import Image, ImageTk

HOST = '127.0.0.1'
PORT = 5555

players = []
game_ready = False
current_turn = 0
player_serial = 0
player_name = ""

token_coordinate = [
    [635, 485], [5, 545], [65, 545], [125, 545], [185, 545], [245, 545], [305, 545], [365, 545], [425, 545],
    [485, 545],
    [545, 545],
    [545, 485], [485, 485], [425, 485], [365, 485], [305, 485], [245, 485], [185, 485], [125, 485], [65, 485],
    [5, 485],
    [5, 425], [65, 425], [125, 425], [185, 425], [245, 425], [305, 425], [365, 425], [425, 425], [485, 425],
    [545, 425],
    [545, 365], [485, 365], [425, 365], [365, 365], [305, 365], [245, 365], [185, 365], [125, 365], [65, 365],
    [5, 365],
    [5, 305], [65, 305], [125, 305], [185, 305], [245, 305], [305, 305], [365, 305], [425, 305], [485, 305],
    [545, 305],
    [545, 245], [485, 245], [425, 245], [365, 245], [305, 245], [245, 245], [185, 245], [125, 245], [65, 245],
    [5, 245],
    [5, 185], [65, 185], [125, 185], [185, 185], [245, 185], [305, 185], [365, 185], [425, 185], [485, 185],
    [545, 185],
    [545, 125], [485, 125], [425, 125], [365, 125], [305, 125], [245, 125], [185, 125], [125, 125], [65, 125],
    [5, 125],
    [5, 65], [65, 65], [125, 65], [185, 65], [245, 65], [305, 65], [365, 65], [425, 65], [485, 65], [545, 65],
    [545, 5], [485, 5], [425, 5], [365, 5], [305, 5], [245, 5], [185, 5], [125, 5], [65, 5], [5, 5]
]

def get_token_coordinate(grid_number):
    return token_coordinate[grid_number]

class FormWindow:
    """
    A class representing a form window for user input.
    """
    def __init__(self, client):
        self.client = client
        self.window = tk.Tk()
        self.window.title("Form Window")
        self.window.resizable(False, False)

        self.name_label = tk.Label(self.window, text="Your Name:")
        self.name_label.pack(pady=5)
        self.name_entry = tk.Entry(self.window, font=('Courier', 10), width=30)
        self.name_entry.pack(pady=5)

        self.submit_button = tk.Button(self.window, text="SUBMIT", height=1, width=8, bg='lime', activebackground='green', font=('cursive', 12, 'bold'), command=self.submit_form)
        self.submit_button.pack(pady=10)

    def submit_form(self):
        """
        Submit the form by sending the player's name to the server and opening a new game window.
        @return None
        """
        global player_serial, player_name
        player_name = self.name_entry.get()

        if player_name != '':
            self.window.destroy()

            context = {
                'player_name': player_name
            }
            self.client.sendall(json.dumps(context).encode())

            game_window = GameWindow(self.client, player_name)
            game_window.run()

    def run(self):
        self.window.mainloop()

class GameWindow:
    def __init__(self, client, player_name):
        """
        Initialize the Game GUI.
        @param client - the client object
        @param player_name - the name of the player
        @return None
        """
        self.client = client

        self.players = []
        self.game_ready = False
        self.current_turn = 0
        self.player_serial = 0
        self.player_name = player_name

        self.root = tk.Tk()
        self.root.geometry("1110x600")
        self.root.title("Snake and Ladder Game")
        self.root.resizable(False, False)

        self.game_canvas = tk.Canvas(self.root, width=750, height=600)
        self.game_canvas.place(x=0, y=0)

        # Create game canvas
        self.game_canvas = tk.Canvas(self.root, width=750, height=600)
        self.game_canvas.place(x=0, y=0)

        # Create chat canvas
        self.chat_canvas = tk.Canvas(self.root, width=360, height=600, bg='black')
        self.chat_canvas.pack(side=tk.RIGHT)

        # Create chatbox
        self.chatbox = scrolledtext.ScrolledText(self.chat_canvas, font=('Courier', 10), bg='black', fg='lime', width=44, height=27)
        self.chatbox.config(state=tk.DISABLED)
        self.chatbox.place(x=5, y=5)

        # Create chat entry
        self.entry = tk.Text(self.chat_canvas, width=43, height=2, font=('Courier', 10))
        self.entry.place(x=6, y=500)

        # Create buttons
        self.rank_button = tk.Button(self.game_canvas, text="RANKS", height=2, width=10, bg='lime', activebackground='green', font=('cursive', 12, 'bold'), command=self.show_ranks)
        self.rank_button.place(x=610, y=485)

        self.send_button = tk.Button(self.chat_canvas, text="SEND", height=2, width=10, bg='lime', activebackground='green', font=('cursive', 10, 'bold'), command=self.send_message)
        self.send_button.place(x=140, y=545)

        self.roll_button = tk.Button(self.game_canvas, text="ROLL", height=2, width=10, bg='red', activebackground='green', font=('cursive', 12, 'bold'), command=self.roll_dice)
        self.roll_button.place(x=610, y=545)

        self.start_button = tk.Button(self.game_canvas, text='START', height=2, width=10, bg='lime', activebackground='green', font=('cursive', 12, 'bold'), command=self.start_game)
        self.start_button.place(x=610, y=425)     
        
        self.turn_alert = tk.Label(self.game_canvas, text="YOUR TURN", fg='red', font=('cursive', 14, 'bold'))

        # Create game images
        self.load_game_images()

    def load_game_images(self):
        """
        Load the images required for the game.
        @return None
        """
        # Load board image
        self.board_image = ImageTk.PhotoImage(Image.open('assets/board.jpg'))
        self.game_canvas.create_image(0, 0, anchor=tk.NW, image=self.board_image)

        # Load token images
        self.token_images = {
            'blue': ImageTk.PhotoImage(Image.open('assets/blue.png')),
            'green': ImageTk.PhotoImage(Image.open('assets/green.png')),
            'red': ImageTk.PhotoImage(Image.open('assets/red.png')),
            'yellow': ImageTk.PhotoImage(Image.open('assets/yellow.png'))
        }

        # Initialize token positions
        self.token_positions = {}

        self.dice1 = ImageTk.PhotoImage(Image.open('assets/dice1.jpg'))
        self.dice2 = ImageTk.PhotoImage(Image.open('assets/dice2.jpg'))
        self.dice3 = ImageTk.PhotoImage(Image.open('assets/dice3.jpg'))
        self.dice4 = ImageTk.PhotoImage(Image.open('assets/dice4.jpg'))
        self.dice5 = ImageTk.PhotoImage(Image.open('assets/dice5.jpg'))
        self.dice6 = ImageTk.PhotoImage(Image.open('assets/dice6.jpg'))

        self.dice_image = {
            1: self.dice1, 2: self.dice2, 3: self.dice3, 4: self.dice4, 5: self.dice5, 6: self.dice6
        }

    def run(self):
        """
        Start a new thread to listen for events and then start the main event loop of the GUI.
        @return None
        """
        threading.Thread(target=self.listen_for_events).start()
        self.root.mainloop()

    def start_game(self):
        """
        Start the game by sending a request to the server with the player's name and serial number.
        @return None
        """
        data = {
            'type': 'game_data',
            'player_name': self.player_name,
            'player_serial': self.player_serial
        }
        
        if self.game_ready:
            data['request'] = 'reset'
        else:
            data['request'] = 'start'

        self.client.sendall((json.dumps(data) + '\x00').encode())        

    def show_ranks(self):
        """
        Display the ranks of players in a popup window.
        @return None
        """
        sorted_players = sorted(players, key=lambda player: player.get('rank'))
        text = ""
        for player in sorted_players:
            rank = player.get('rank')
            if rank != -1:
                name = player.get('name')
                text += f"{rank}. {name}\n"

        if text == "": text = "Currently no player could finish the game.\nKeep playing."

        popup = tk.Toplevel(self.root)
        popup.title("Ranks")
        label = tk.Label(popup, text=text, anchor="center", justify="center", font=('Courier', 12))
        label.pack(padx=20, pady=20)
        close_button = tk.Button(popup, text="Close", bg='lime', activebackground='green', font=('cursive', 10, 'bold'), command=popup.destroy)
        close_button.pack(pady=10)

    def move_tokens(self):
        """
        Move the tokens of each player on the game canvas based on their current position.
        @return None
        """
        global players
        for player in players:
            position = player.get('position')
            token_color = player.get('token_color')
            coordinate = get_token_coordinate(position)

            if token_color in self.token_images:
                token_image = self.token_images[token_color]
                if token_color not in self.token_positions:
                    self.token_positions[token_color] = self.game_canvas.create_image(coordinate[0], coordinate[1], anchor=tk.NW, image=token_image)
                else:
                    self.game_canvas.coords(self.token_positions[token_color], coordinate[0], coordinate[1])

    def draw_dice(self, dice_result):
        """
        Draw the image of a dice on the game canvas based on the given dice result.
        @param self - the instance of the class
        @param dice_result - the result of the dice roll
        @return None
        """
        if dice_result in self.dice_image:
            dice_img = self.dice_image[dice_result]
            self.game_canvas.create_image(610, 125, anchor=tk.NW, image=dice_img)

    def send_game_to_server(self, dice_result):
        """
        Send game data to the server.
        @param self - the instance of the class
        @param dice_result - the result of the dice roll
        @return None
        """
        data = {
            'type': 'game_data',
            'player_serial': self.player_serial,
            'dice_result': dice_result,
        }

        try:
            self.client.sendall((json.dumps(data) + '\x00').encode())
        except Exception as e:
            print(e)

    def send_message(self):
        """
        Send a message to the server.
        @return None
        """
        message = self.entry.get('1.0', tk.END)
        if message != '\n':
            self.entry.delete('1.0', tk.END)

            context = {
                'type': 'chat_data',
                'sender': player_name,
                'message': message
            }

            try:
                json_data = json.dumps(context) + '\x00'
                self.client.sendall(json_data.encode())
            except Exception as e:
                print(e)

    def roll_dice(self):
        """
        Roll a dice for the current player if it is their turn and the game is ready.
        @return None
        """
        if self.player_serial == current_turn and self.game_ready:
            dice_result = random.randint(1, 6)
            self.send_game_to_server(dice_result)

    def update_game_data(self, data):
        """
        Update the game data based on the received data.
        @param self - the instance of the class
        @param data - the data to update the game with
        @return None
        """
        global game_ready, current_turn, players

        current_turn = data.get('current_turn')
        self.game_ready = data.get('is_ready')
        dice_result = data.get('dice_result')

        if self.game_ready: self.start_button.config(text="RESET")

        if dice_result: self.draw_dice(dice_result)
        
        if self.player_serial == current_turn and self.game_ready:
            self.turn_alert.place(x=610, y=365)
        else:
            self.turn_alert.place_forget()

        players = [
            {
                'name': player.get('name'),
                'serial': player.get('serial'),
                'token_color': player.get('token_color'),
                'position': player.get('position'),
                'rank': player.get('rank')
            } for player in data.get('players')
        ]

        self.move_tokens()

    def display_chat_data(self, data):
        """
        Display the chat data in the chatbox GUI.
        @param self - the instance of the class
        @param data - the chat data to be displayed
        @return None
        """
        if data.get('sender') == 'server':
            text = 'SERVER: ' + data.get('message').upper()
        else:
            text = data.get('sender') + ': ' + data.get('message')
            
        self.chatbox.config(state=tk.NORMAL)
        self.chatbox.insert(tk.END, text)
        self.chatbox.config(state=tk.DISABLED)

    def handle_incoming_data(self, data):
        """
        Handle incoming data and perform different actions based on the data type.
        @param self - the instance of the class
        @param data - the incoming data
        @return None
        """
        if data.get('type') == 'chat_data':
            self.display_chat_data(data)
        elif data.get('type') == 'game_data':
            self.update_game_data(data)
        else:
            self.player_serial = data['player_serial']

    def listen_for_events(self):
        """
        Listen for events from the client by continuously receiving data in chunks. 
        The received data is appended to a JSON data variable. Once a null byte (b'\x00') is found in the JSON data, 
        it indicates the end of a complete JSON object. The JSON object is extracted, and the remaining data is stored for the next iteration. 
        The extracted JSON object is then passed to the `handle_incoming_data` method for further processing.
        @return None
        """
        json_data = b''
        while True:
            try:
                chunk = self.client.recv(512)
                json_data += chunk

                while b'\x00' in json_data:
                    end_indx = json_data.index(b'\x00')
                    data = json_data[:end_indx]
                    json_data = json_data[end_indx + 1:]

                    self.handle_incoming_data(json.loads(data))
            except Exception as e:
                print(e)
                exit()


class App:
    """
    The `App` class represents an application that connects to a server using a TCP socket and runs a form window.
    """
    def __init__(self):
        """
        Initialize a client socket and connect it to a server using the specified host and port. 
        If the connection is successful, create an instance of the `FormWindow` class passing the client socket as an argument. 
        Then, run the `run()` method of the `FormWindow` instance.
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            client.connect((HOST, PORT))
            print("Connected to server.")
        except Exception as e:
            print(e)
            exit()

        form_window = FormWindow(client)
        form_window.run()

if __name__ == "__main__":
    app = App()
