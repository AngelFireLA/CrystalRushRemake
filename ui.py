import numpy as np
import pygame
from engine import *
from utils import *

pygame.init()

width, height = 30, 15

screen = pygame.display.set_mode((Square.pixel_size * width, Square.pixel_size * height))
player1 = Player("Player 1", [Robot(0, 0, "blue"), Robot(0, 1, "blue"), Robot(0, 2, "blue"), Robot(0, 3, "blue")], "blue")
player2 = Player("Player 2", [Robot(0, 14, "red"), Robot(0, 13, "red"), Robot(0, 12, "red"), Robot(0, 11, "red")], "red")

game = Game([],width=width, height=height)

background = pygame.image.load("background.png")
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            target_pos = pos_to_square(pygame.mouse.get_pos(), Square.pixel_size)
            robot.target = target_pos

    # show grid with each square and inside the number of ores inside it
    screen.blit(background, (0, 0))
    game.board.draw_grid(screen)
    for row in game.board.grille:
        for square in row:
            if square.ore_amount > 0:
                font = pygame.font.Font(None, 30)
                text = font.render(str(square.ore_amount), True, (255, 255, 255))
                screen.blit(text, (square.x * Square.pixel_size + 10, square.y * Square.pixel_size + 10))
    for robot in player1.robots:
        if robot.target:
            robot.move(robot.target, game.board)
        robot.draw(screen)
    for robot in player2.robots:
        if robot.target:
            robot.move(robot.target, game.board)
        robot.draw(screen)
    pygame.display.flip()
