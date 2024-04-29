import numpy as np
import pygame
from engine import *
from utils import *
import user_script

pygame.init()
clock = pygame.time.Clock()

board_width, board_height = 30, 15
sidebar_width = 100
width, height = Game.pixel_size * board_width + sidebar_width, Game.pixel_size * board_height

screen = pygame.display.set_mode((width, height))
player1 = Player("Player 1", [Robot(0, 0, "blue"), Robot(0, 1, "blue"), Robot(0, 2, "blue"), Robot(0, 3, "blue")], "blue")
player2 = Player("Player 2", [Robot(0, 14, "red"), Robot(0, 13, "red"), Robot(0, 12, "red"), Robot(0, 11, "red")], "red")

game = Game([player1, player2],width=board_width, height=board_height)

background = pygame.image.load("assets/images/background.png")
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            target_pos = pos_to_square(pygame.mouse.get_pos(), Game.pixel_size)
            find_closest_robot_to_pos(player1.robots, target_pos).target = target_pos

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            target_pos = pos_to_square(pygame.mouse.get_pos(), Game.pixel_size)
            robot = game.get_robot_on_square(target_pos)
            if robot is not None:
                print(robot)


        #when press space bar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game.turn += 1
            for player in game.players:
                player.reduce_cooldowns()
            user_actions, robot_targets = user_script.user_script(board=game.construct_player_board(player1), robots=[robot.copy() for robot in player1.robots], turn_count=game.turn, player=player1.copy_empty())
            for i in range(len(robot_targets)):
                player1.robots[i].target = robot_targets[i]
            for i in range(len(user_actions)):
                if user_actions[i] is not None:
                    game.process_action(user_actions[i], player1.robots[i], player1)
            # print(player1.score)
            # for r in player1.robots:
            #     print(r.id, r.current_item)
    # show grid with each square and inside the number of ores inside it
    screen.blit(background, (0, 0))

    show_text(game.turn, (width-sidebar_width, 0), screen, size=50)

    game.board.draw_grid(screen)
    for row in game.board.grid:
        for square in row:
            if square.ore_amount > 0:
                font = pygame.font.Font(None, 30)
                text = font.render(str(square.ore_amount), True, (255, 255, 255))
                screen.blit(text, (square.x * Game.pixel_size + 10, square.y * Game.pixel_size + 10))
    for robot in player1.robots:
        robot.draw(screen)
    for robot in player2.robots:
        robot.draw(screen)
    pygame.display.flip()
    clock.tick(60)
