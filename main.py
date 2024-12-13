import os.path
import time
import math

import pygame
import random as rnd

import menu as m
from settings import *

if __name__ == '__main__':
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    menu = m.Menu(screen)
    menu.main_menu()

    pygame.quit()