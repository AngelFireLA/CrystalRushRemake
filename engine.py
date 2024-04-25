from collections import deque
import pygame
import numpy as np

id_counter = 0
# https://github.com/CodinGameCommunity/UnleashTheGeek
class Square:
    pixel_size = 50

    def __init__(self, x, y, ore_amount, ground_type):
        self.x = x
        self.y = y
        self.ore_amount = ore_amount
        self.items = []
        self.ground_type = ground_type
        self.has_hole = False


class Board:
    def __init__(self, width=30, height=15, head_quarter_width=1):
        self.width = width
        self.height = height
        self.head_quarter_width = head_quarter_width
        self.grille = []
        self.ore_map = self.init_ore_map()

        self.init_grid()

    def init_grid(self):
        for row in range(self.height):
            self.grille.append([])
            for col in range(self.width):
                self.grille[row].append(self.generate_square(col, row))

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

    def generate_square(self, x, y):
        if x <= self.head_quarter_width - 1:
            ground_type = "head_quarter"
        else:
            ground_type = "ground"

        ore_amount = self.ore_map[y][x]
        return Square(x, y, ore_amount, ground_type)

    def draw_grid(self, screen):
        for row in self.grille:
            for square in row:

                rect = pygame.Rect(square.x * Square.pixel_size, square.y * Square.pixel_size, Square.pixel_size,
                                   Square.pixel_size)
                if square.ground_type == "head_quarter":
                    pygame.draw.rect(screen, (0, 255, 0), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Draw black border with thickness of 1 pixel

    def get_square_from_mouse_position(self, mouse_pos):
        x, y = mouse_pos
        x //= Square.pixel_size
        y //= Square.pixel_size
        return self.grille[y][x]


class Robot:
    reach = 1
    max_movement_per_turn = 4

    def __init__(self, x, y, color):
        global id_counter
        self.id = id_counter
        id_counter+=1
        self.x = x
        self.y = y
        self.current_item = None
        self.color = color
        self.target = None

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
        #draw a circle of the robot color
        pygame.draw.circle(screen, self.color, (self.x * Square.pixel_size + Square.pixel_size // 2,
                                                  self.y * Square.pixel_size + Square.pixel_size // 2),
                           Square.pixel_size // 2)

    def move(self, pos, board):
        x, y = pos
        path = self.pathfind_to(x, y, board)
        if path:
            if len(path) <= self.max_movement_per_turn:
                self.x, self.y = path[-1]
            else:
                self.x, self.y = path[self.max_movement_per_turn-1]
        return path

class Player:
    default_item_cooldown = 5
    def __init__(self, name, robots, color):
        self.name = name
        self.robots = robots
        self.color = color
        self.score = 0
        self.radar_cooldown = self.default_item_cooldown
        self.trap_cooldown = self.default_item_cooldown

class Item:
    def __init__(self, type, color):
        self.type = type
        self.color = color

class Radar(Item):
    range = 4
    def __init__(self, color):
        super().__init__("radar", color)

class Trap(Item):
    range = 1
    def __init__(self, color):
        super().__init__("trap", color)


class Game:
    def __init__(self, players, width, height):
        self.players = players
        self.board = Board(width, height)
        self.turn = 0