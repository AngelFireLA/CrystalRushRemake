import pygame



def pos_to_square(mouse_pos, square_size):
    return (mouse_pos[0] // square_size, mouse_pos[1] // square_size)

def show_text(text, pos, screen, color=(0, 0, 0), size=30):
    """
    Place pygame text
    :param text: text to show
    :param pos: position of text
    :param color: color of text
    :param screen: screen to show text
    """
    font = pygame.font.SysFont('Arial', size)
    text = font.render(str(text), True, color)
    screen.blit(text, pos)

def find_closest_robot_to_pos(robots, pos):
    #robots is a list of robot who has .x and .y and pos is a tuple (x, y)
    robot = None
    min_distance = 99999
    for r in robots:
        distance = (r.x - pos[0])**2 + (r.y - pos[1])**2
        if distance < min_distance:
            min_distance = distance
            robot = r

    return robot

def show_grid(grid):
    for row in grid:
        for square in row:
            print(square.ore_amount, end=" ")
        print()


color_dict = {
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "lime": (0, 255, 0),
    "maroon": (128, 0, 0),
    "olive": (128, 128, 0),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
    "silver": (192, 192, 192),
    "gold": (255, 215, 0)
}

tile_color = {}

tile_color["blue"] = {"radar":color_dict["cyan"], "trap":color_dict["navy"]}