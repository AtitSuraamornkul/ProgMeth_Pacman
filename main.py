import pygame
import random
import os
from constants import *
from board import Board
from entities import HumanPlayer, AIPlayer, Ghost
from ui import Button
from game import Game

if __name__ == "__main__":
    Game().run()