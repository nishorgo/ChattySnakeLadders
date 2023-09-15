class MovingEntity:
    def __init__(self, end_position=None):
        self.end_position = end_position
        self.name = None

    def set_name(self, name):
        self.name = name

    def set_end_position(self, end_position):
        self.end_position = end_position

    def get_end_position(self):
        if self.end_position is None:
            raise Exception("No end position defined.")
        return self.end_position


class Snake(MovingEntity):
    def __init__(self, end_position=None):
        super(Snake, self).__init__(end_position)
        self.name = "snake"


class Ladder(MovingEntity):
    def __init__(self, end_position=None):
        super(Ladder, self).__init__(end_position)
        self.name = "ladder"
