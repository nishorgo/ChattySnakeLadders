from board import Board
from player import Player
from moving_entity import Snake, Ladder


class Game:
    def __init__(self, game_id):
        self.id = game_id
        self.colors = ['blue', 'green', 'red', 'yellow']
        self.is_ready = False
        self.board = None
        self.players = []
        self.current_turn = 0
        self.last_rank = 0
        self.consecutive_one = 0
        self.consecutive_one_dice_result = 0
        self.request_count = 0

    def get_players(self):
        return self.players

    def get_next_player_serial(self):
        return len(self.players)

    def set_new_player(self, player_name, client):
        """
        Create a new player object and add it to the list of players in the game.
        @param player_name - the name of the new player
        @param client - the client object associated with the new player
        @return None
        """
        new_player_serial = self.get_next_player_serial()
        self.players.append(Player(new_player_serial, self.colors[new_player_serial], client, player_name))

    def initialize_game(self):
        self.board = Board()

        # instantiating all the snakes
        self.board.set_moving_entity(27, Snake(5))
        self.board.set_moving_entity(40, Snake(3))
        self.board.set_moving_entity(43, Snake(18))
        self.board.set_moving_entity(54, Snake(31))
        self.board.set_moving_entity(66, Snake(45))
        self.board.set_moving_entity(76, Snake(58))
        self.board.set_moving_entity(89, Snake(53))
        self.board.set_moving_entity(99, Snake(41))

        # instantiating all the ladders
        self.board.set_moving_entity(4, Ladder(25))
        self.board.set_moving_entity(13, Ladder(46))
        self.board.set_moving_entity(33, Ladder(49))
        self.board.set_moving_entity(42, Ladder(63))
        self.board.set_moving_entity(50, Ladder(69))
        self.board.set_moving_entity(62, Ladder(81))
        self.board.set_moving_entity(74, Ladder(92))

        self.is_ready = True
        print('Game has started.')

    def can_play(self):
        """
        Check if the player can play based on their last rank and the total number of players.
        @return True if the player can play, False otherwise
        """
        if self.last_rank != len(self.players):
            return True
        return False

    def move_player(self, current_player, next_position):
        """
        Move the current player to the next position on the board. If the player reaches the last position on the board, update their rank accordingly.
        @param self - the current instance of the class
        @param current_player - the player object that is currently moving
        @param next_position - the position on the board where the player will move to
        @return None
        """
        current_player.set_position(next_position)
        print(f"position set to {next_position}")
        if self.board.at_last_position(next_position):
            current_player.set_rank(self.last_rank + 1)
            self.last_rank += 1

    def can_move(self, current_player, to_move_position):
        """
        Check if a player can move to a certain position on the board.
        @param current_player - the player who wants to move
        @param to_move_position - the position the player wants to move to
        @return True if the player can move to the position, False otherwise
        """
        if to_move_position <= self.board.get_size() and current_player.get_rank() == -1 and current_player.is_ready:
            return True
        return False

    def change_turn(self, dice_result):
        """
        Change the turn in the game based on the result of the dice roll.
        @param self - the instance of the game
        @param dice_result - the result of the dice roll
        @return None
        """
        self.consecutive_one = 0 if dice_result != 1 else self.consecutive_one + 1
        if dice_result != 1 or self.consecutive_one == 3:
            if self.consecutive_one == 3:
                print("Changing turn due to 3 consecutive ones")
            self.current_turn = (self.current_turn + 1) % len(self.players)

            while self.players[self.current_turn].get_rank() != -1:
                self.current_turn = (self.current_turn + 1) % len(self.players)

        else:
            print(f"One more turn for player {self.current_turn + 1} after rolling 1")

    def handle_start_game_request(self, player_serial):
        """
        Handle a start game request from a player. If there are more than one players in the game, check if the current player has already made a request. 
        If not, mark the current player as requested and increment the request count. Print the current player's name and request status, 
        as well as the current request count.
         """
        if len(self.get_players()) > 1:
            current_player = self.get_players()[player_serial]
            if current_player.is_requested == False:
                current_player.is_requested = True
                self.request_count += 1

                print(f"player {current_player.name}: {current_player.is_requested}")
                print(f"request count: {self.request_count}")

            if self.request_count == len(self.get_players()):
                if self.is_ready:
                    self.current_turn = 0
                    self.last_rank = 0
                    self.consecutive_one = 0
                    self.consecutive_one_dice_result = 0
                    self.request_count = 0

                    for player in self.get_players():
                        player.is_ready = False
                        player.position = 0
                        player.rank = -1
                        player.is_requested = False

                    print('Game has reset.')

                else:
                    self.initialize_game()
                    for player in self.get_players():
                        player.is_requested = False
                    self.request_count = 0
