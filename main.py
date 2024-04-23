import numpy as np
import pygame

pygame.init()
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
        for x in range(self.width):
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
            x, y = np.random.randint(self.width), np.random.randint(self.height)
            if grid[y, x] < 3:
                grid[y, x] += 1
                total_ores += 1
        while total_ores > target_ores:
            x, y = np.random.randint(self.width), np.random.randint(self.height)
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

class Robot:
    reach = 1
    def __init__(self, x, y, color):
        global id_counter
        self.id = id_counter
        id_counter+=1
        self.x = x
        self.y = y
        self.current_item = None
        self.color = color

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
    def __init__(self, players):
        self.players = players
        self.board = Board()
        self.turn = 0

board = Board()
screen = pygame.display.set_mode((Square.pixel_size * board.width, Square.pixel_size * board.height))

background = pygame.image.load("background.png")
# resize image to screen
background = pygame.transform.scale(background, (Square.pixel_size * board.width, Square.pixel_size * board.height))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # show grid with each square and inside the number of ores inside it
    screen.blit(background, (0, 0))
    for row in board.grille:
        for square in row:
            if square.ore_amount > 0:
                font = pygame.font.Font(None, 30)
                text = font.render(str(square.ore_amount), True, (255, 255, 255))
                screen.blit(text, (square.x * Square.pixel_size + 10, square.y * Square.pixel_size + 10))

    pygame.display.flip()
