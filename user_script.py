from engine import *
from utils import *

import sys
import math
import random



class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, pos):
        return abs(self.x - pos.x) + abs(self.y - pos.y)


class Entity(Pos):
    def __init__(self, x, y, type, id):
        super().__init__(x, y)
        self.type = type
        self.id = id

class Game:
    def __init__(self):
        self.my_score = 0
        self.enemy_score = 0
        self.radar_cooldown = 0
        self.trap_cooldown = 0
        self.radars = []
        self.traps = []
        self.my_robots = []

    def distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


    def get_closest_to_hq(self, board:Board, robots_transporting_radar=None):
        closest_robot: Robot = None
        closest_distance = math.inf
        for robot in self.my_robots:
            distance = self.distance((robot.x, robot.y), (board.head_quarter_width-1, robot.y))
            if distance < closest_distance:
                if robots_transporting_radar is not None and robot in robots_transporting_radar:
                    continue
                closest_robot = robot
                closest_distance = distance

        return closest_robot


game = Game()

def get_ores(board):
    ores = []
    for y in range(board.height):
        for x in range(board.width):
            cell: Square = board.grid[y][x]
            if cell and cell.ore_amount != "?" and int(cell.ore_amount) > 0:
                ores.append((x, y))
    return ores


def get_all_robots_targets(robots):
    return [robot.target for robot in robots]


def find_next_ore(current_robot, robots, board):
    if current_robot.current_item and current_robot.current_item.type == "radar":
        print("on cherche minerai en tant que radar?")
    ores = get_ores(board)
    #sort ores according to distance with (current_robot.x, current_robot.y)
    ores.sort(key=lambda x: game.distance((current_robot.x, current_robot.y), x))
    for ore in ores:
        if ore not in get_all_robots_targets(robots):
            return ore
    random_target = None
    while random_target is None or random_target in set_radar_locations:
        random_target = (random.randint(0, board.width - 1), random.randint(0, board.height - 1))
    return random_target



set_radar_locations = [(2, 1), (12, 2), (12, 12), (4, 2), (4, 12), (15, 7), (19, 2), (19, 12), (23, 7), (27, 2), (27, 12), (27, 7)]
placed_radars = []

def user_script(board, robots, turn_count, player):
    """
    This is the main function that you should write. It is called by the engine
    at the start of each turn. It must return a list of strings for each robot.
    Returns a list of actions for each robot and each robot's target.
    """



    game.radars = board.get_radars()
    game.traps = board.get_traps()
    game.my_robots = robots


    actions = []
    targets = []
    for i in range(len(robots)):
        #print(i)
        robot = robots[i]
        if robot.current_item:
            if robot.current_item.type == "ore":
                actions.append("move")
                targets.append((board.head_quarter_width-1, robot.y))
                continue
            if robot.current_item.type == "radar" and robot.target not in set_radar_locations:
                actions.append("move")
                next_radar_location = set_radar_locations.pop(0)
                targets.append(next_radar_location)
                continue

        if player.radar_cooldown < 1 :
            closest_robot = game.get_closest_to_hq(board)
            robots_transporting_radar = []
            while closest_robot.current_item and closest_robot.current_item.type == "radar":
                robots_transporting_radar.append(closest_robot)
                closest_robot = game.get_closest_to_hq(board, robots_transporting_radar)
            if closest_robot == robot:
                if closest_robot.x == 0:
                    targets.append(robot.target)
                    actions.append("request radar")
                    continue
                else:
                    targets.append((closest_robot.x-1, robot.y))
                    actions.append("move")
                    continue
        if robot.target:
            if (robot.x, robot.y) == robot.target:
                actions.append("dig")
                targets.append(None)
                continue
            else:
                actions.append("move")
                targets.append(robot.target)
                continue
        else:
            actions.append("move")
            targets.append(find_next_ore(robot, robots, board))
            continue
    #print(actions, targets)
    return actions, targets
