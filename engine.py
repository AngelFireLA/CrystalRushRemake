import copy
from collections import deque
import pygame
import numpy as np
from utils import *

id_counter = 0


# https://github.com/CodinGameCommunity/UnleashTheGeek
class Square:

    def __init__(self, x, y, ore_amount, ground_type, item=None, has_hole=False):
        self.x = x
        self.y = y
        self.ore_amount = ore_amount
        self.item = item
        self.ground_type = ground_type
        self.has_hole = has_hole

    def copy(self):
        new_square = Square(self.x, self.y, self.ore_amount, self.ground_type, self.item, self.has_hole)
        return new_square

    def __str__(self):
        return f"{self.ore_amount}"

    def __repr__(self):
        return f"{self.ore_amount}"


class Board:
    def __init__(self, width=30, height=15, head_quarter_width=1):
        self.width = width
        self.height = height
        self.head_quarter_width = head_quarter_width
        self.grid = []

        self.init_grid(self.init_ore_map())

    def copy(self):
        # Create a new Board instance
        new_board = Board(self.width, self.height, self.head_quarter_width)

        new_board.grid = copy.deepcopy(self.grid)
        return new_board

    def init_grid(self, ore_map):
        for row in range(self.height):
            self.grid.append([])
            for col in range(self.width):
                self.grid[row].append(self.generate_square(col, row, ore_map))

    def init_ore_map(self, target_ores=200):
        grid = np.zeros((self.height, self.width), dtype=int)
        center_x, center_y = self.width // 2, self.height // 2
        total_ores = 0

        # Compute distance weights, favoring the center
        for x in range(self.head_quarter_width, self.width):
            for y in range(self.height):
                distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
                weight = 1 - (distance / max_distance)  # Normalize to [0,1], where 1 is center

                # Set up initial probabilities
                probs = [0.5 - weight * 0.15, 0.3 + weight * 0.05, 0.15, 0.05 + weight * 0.05]
                # Normalize probabilities to sum to 1
                probs /= np.sum(probs)

                # Determine ore value, with adjusted probabilities
                ore_value = np.random.choice([0, 1, 2, 3], p=probs)
                grid[y, x] = ore_value
                total_ores += ore_value
        # Post-generation adjustments to meet the target ore count more precisely
        while total_ores < target_ores:
            x, y = np.random.randint(self.head_quarter_width, self.width), np.random.randint(self.height)
            if grid[y, x] < 3:
                grid[y, x] += 1
                total_ores += 1
        while total_ores > target_ores:
            x, y = np.random.randint(self.head_quarter_width, self.width), np.random.randint(self.height)
            if grid[y, x] > 0:
                grid[y, x] -= 1
                total_ores -= 1

        return grid

    def generate_square(self, x, y, ore_map):
        if x <= self.head_quarter_width - 1:
            ground_type = "head_quarter"
        else:
            ground_type = "ground"

        ore_amount = ore_map[y][x]
        return Square(x=x, y=y, ore_amount=ore_amount, ground_type=ground_type)

    def draw_grid(self, screen):
        for row in self.grid:
            for square in row:
                scale_factor = 0.75
                rect = pygame.Rect(square.x * Game.pixel_size, square.y * Game.pixel_size, Game.pixel_size*scale_factor, Game.pixel_size*scale_factor)
                outline_rect = pygame.Rect(square.x * Game.pixel_size, square.y * Game.pixel_size, Game.pixel_size, Game.pixel_size)
                if square.ground_type == "head_quarter":
                    pygame.draw.rect(screen, (0, 255, 0), rect)
                elif square.item and square.item.type == "radar":
                    pygame.draw.rect(screen, tile_color[square.item.color]["radar"], rect)
                elif square.item and square.item.type == "trap":
                    pygame.draw.rect(screen, tile_color[square.item.color]["trap"], rect)
                elif square.has_hole:
                    pygame.draw.rect(screen, (255, 255, 255), rect)
                pygame.draw.rect(screen, (0, 0, 0), outline_rect, 1)  # Draw black border with thickness of 1 pixel

    def get_square_from_mouse_position(self, mouse_pos):
        x, y = mouse_pos
        x //= Game.pixel_size
        y //= Game.pixel_size
        return self.grid[y][x]

    def get_radars(self):
        radars = []
        for row in self.grid:
            for square in row:
                if square.item and square.item.type == "radar":
                    radars.append((square.item, (square.x, square.y)))
        return radars

    def get_traps(self):
        traps = []
        for row in self.grid:
            for square in row:
                if square.item and square.item.type == "trap":
                    traps.append((square.item, (square.x, square.y)))
        return traps


class Robot:
    reach = 1
    max_movement_per_turn = 4

    def __init__(self, x, y, color, id=None, current_item=None, target=None, exploded=False):
        global id_counter
        if not id:
            self.id = id_counter
            id_counter += 1
        else:
            self.id = id
        self.x = x
        self.y = y
        if current_item:
            self.current_item = current_item
        else:
            self.current_item = None
        self.color = color
        if target:
            self.target = target
        else:
            self.target = None
        self.exploded = exploded

    def __str__(self):
        return f"Id :{self.id}, pos : ({self.x},{self.y}), item : ({self.current_item}), target : {self.target}"

    def __repr__(self):
        return f"Id :{self.id}, pos : ({self.x}, {self.y}), item : ({self.current_item}), target : {self.target}"

    def copy(self):
        return Robot(self.x, self.y, self.color, self.id, self.current_item, self.target, self.exploded)

    def pathfind_to(self, x, y, board):
        queue = deque([(self.x, self.y, [])])
        visited = {(self.x, self.y)}

        while queue:
            current_x, current_y, path = queue.popleft()

            if current_x == x and current_y == y:
                return path

            # Generate neighboring cells
            neighbors = [(current_x + dx, current_y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]

            for nx, ny in neighbors:
                if 0 <= nx < board.width and 0 <= ny < board.height:
                    if (nx, ny) not in visited:
                        queue.append((nx, ny, path + [(nx, ny)]))
                        visited.add((nx, ny))

        return None

    def draw(self, screen):
        # draw a circle of the robot color
        pygame.draw.circle(screen, self.color, (self.x * Game.pixel_size + Game.pixel_size // 2,
                                                self.y * Game.pixel_size + Game.pixel_size // 2),
                           Game.pixel_size // 2)
        from utils import show_text
        show_text(f"{self.id}",( self.x * Game.pixel_size + Game.pixel_size // 4,
                  self.y * Game.pixel_size + Game.pixel_size // 4), screen)

    def move(self, pos, board, player):
        x, y = pos
        path = self.pathfind_to(x, y, board)
        if path:
            if len(path) <= self.max_movement_per_turn:
                self.x, self.y = path[-1]
            else:
                self.x, self.y = path[self.max_movement_per_turn - 1]
        if board.grid[self.y][self.x].ground_type == "head_quarter" and self.current_item and self.current_item.type == "ore":
            player.score += self.current_item.value
            self.current_item = None
        return path


class Player:
    default_item_cooldown = 5

    def __init__(self, name, robots, color, score=0, radar_cooldown=0, trap_cooldown=0):
        self.name = name
        self.robots = robots
        self.color = color
        self.score = score
        self.radar_cooldown = radar_cooldown
        self.trap_cooldown = trap_cooldown

    def reduce_cooldowns(self):
        self.radar_cooldown -= 1
        self.trap_cooldown -= 1

    def copy_empty(self):
        return Player(self.name, [], self.color, self.score, self.radar_cooldown, self.trap_cooldown)


class Item:
    def __init__(self, type, color):
        self.type = type
        self.color = color

    def __str__(self):
        return f"type : {self.type}, color : {self.color}"

    def __repr__(self):
        return f"type : {self.type}, color : {self.color}"


class Radar(Item):

    def __init__(self, color, radius=4):
        super().__init__("radar", color)
        self.radius = radius
        self.radius_map = self.construct_radius_map()

    def construct_radius_map(self):
        """Creates a list of all the offsets from the center a radar can see in a + shape"""
        neighbor_offsets = []
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                if abs(x) + abs(y) <= self.radius:
                    neighbor_offsets.append((x, y))
        return neighbor_offsets


class Trap(Item):

    def __init__(self, color, radius=1):
        super().__init__("trap", color)
        self.radius = radius
        self.radius_map = self.construct_radius_map()

    def construct_radius_map(self):
        """Creates a list of all the offsets from the center a radar can see in a + shape"""
        neighbor_offsets = []
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                if abs(x) + abs(y) <= self.radius:
                    neighbor_offsets.append((x, y))
        return neighbor_offsets


    def detonate(self, game, robot):
        """
        Explodes the trap and damages all robots in the radius of the trap in the same shape as the radar but different radius
        :param game: the game object
        :param robot: the robot object
        :return:
        """
        for x, y in self.radius_map:
            for robot_on_square in game.get_robots_on_square((robot.x + x, robot.y + y)):
                robot_on_square.exploded = True



class Ore(Item):
    def __init__(self, color):
        super().__init__("ore", color)
        self.value = 1


class Game:
    pixel_size = 50

    def __init__(self, players, width, height):
        self.players = players
        self.board = Board(width, height)
        self.turn = 0

    def process_action(self, action: str, robot: Robot, player: Player):
        if not robot.exploded:
            if action.startswith("move"):
                if robot.target:
                    robot.move(robot.target, self.board, player)

            elif action == "request radar":
                if player.radar_cooldown < 1 and robot.x < self.board.head_quarter_width:
                    robot.current_item = Radar(player.color)
                    player.radar_cooldown = player.default_item_cooldown

            elif action == "request trap":
                if player.trap_cooldown < 1 and robot.x < self.board.head_quarter_width:
                    robot.current_item = Trap(player.color)
                    player.trap_cooldown = player.default_item_cooldown

            elif action == "dig":
                square: Square = self.board.grid[robot.y][robot.x]
                if square.ground_type != "head_quarter":
                    square.has_hole = True
                    if square.item and square.item.type == "trap":
                        square.item.detonate(self, self.board, robot)
                        square.item = None
                        return
                    if robot.current_item and robot.current_item.type == "ore":
                        square.ore_amount += 1
                        robot.current_item = None
                    else:
                        square.item = robot.current_item
                        robot.current_item = None
                        if square.ore_amount > 0:
                            robot.current_item = Ore(player.color)
                            square.ore_amount -= 1
                            print(f"robot {robot.id} has got ore")





        return

    def get_robot_on_square(self, pos):
        for player in self.players:
            for robot in player.robots:
                if robot.x == pos[0] and robot.y == pos[1]:
                    return robot
        return None

    def construct_player_board(self, player):
        """
        returns a board but with all ore values being ?
        :return:
        """
        board = self.board.copy()
        for row in range(board.height):
            for col in range(board.width):
                if self.is_square_visible_by_player(board.grid[row][col], player):
                    continue
                else:
                    board.grid[row][col].ore_amount = -1
        return board

    def is_square_visible_by_player(self, square, player):
        """
        Returns true if square is in radius of one of the placed radars of the player
        :param square:
        :param player:
        :return:
        """
        # get every radar on the board of the color of the player
        radars = [(r, _) for r, _ in self.board.get_radars() if r.color == player.color]
        affected_squares = []
        # for each radar, check if the square is in its radius
        for radar, radar_pos in radars:
            radius_map = radar.radius_map
            for r in radius_map:
                affected_squares.append((radar_pos[0] + r[0], radar_pos[1] + r[1]))
        if (square.x, square.y) in affected_squares:
            return True
        return False

    def get_robots_on_square(self, pos):
        robots_on_square = []
        for player in self.players:
            for robot in player.robots:
                if robot.x == pos[0] and robot.y == pos[1]:
                    robots_on_square.append(robot)
        return robots_on_square
