import pygame
import random


class Player:
    def __init__(self, serial, token_color, network, name=None):
        self.is_ready = False
        self.position = 0
        self.token_color = token_color
        self.name = name
        self.serial = serial
        self.rank = -1
        self.network = network
        self.is_requested = False

    def get_network(self):
        return self.network

    def get_token_color(self):
        return self.token_color

    def get_name(self):
        return self.name

    def get_serial(self):
        return self.serial

    def get_position(self):
        return self.position

    def set_position(self, end_position):
        self.position = end_position

    def set_ready(self):
        self.is_ready = True

    def get_rank(self):
        return self.rank

    def set_rank(self, rank):
        self.rank = rank
