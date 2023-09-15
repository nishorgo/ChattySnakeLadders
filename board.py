class Board:
    def __init__(self):
        self.size = 100
        self.moving_entity = {}

    def get_size(self):
        return self.size

    def set_moving_entity(self, position, moving_entity):
        self.moving_entity[position] = moving_entity

    def get_next_position(self, player_position, dice_result):
        """
        Given the current position of a player and the result of rolling a dice, calculate the next position of the player on a game board.
        @param player_position - the current position of the player
        @param dice_result - the result of rolling a dice
        @return The next position of the player on the game board
        """
        next_position = player_position + dice_result
        if next_position > self.size:
            return player_position
        if next_position in self.moving_entity:
            return self.moving_entity[next_position].get_end_position()
        return next_position

    def is_moving_entity(self, player_position):
        if player_position in self.moving_entity:
            return True
        return False

    def at_last_position(self, position):
        if position == self.size:
            return True
        return False
