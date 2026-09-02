import pygame
import random
import os


class Candy:

    TYPES = [
        "apple",
        "cherry",
        "grape",
        "lemon",
        "orange",
        "pineapple",
        "strawberry",
        "watermelon"
    ]

    def __init__(self, row, col, x, y):

        self.row = row
        self.col = col

        self.x = x
        self.y = y

        self.type = random.choice(self.TYPES)

        image_path = os.path.join(
            "assets",
            self.type + ".png"
        )

        self.original_image = pygame.image.load(
            image_path
        ).convert_alpha()

        self.image = self.original_image.copy()

        self.current_cell_size = 70

        self.resize(self.current_cell_size)

    # ==============================================
    # RESIZE IMAGE
    # ==============================================

    def resize(self, cell_size):

        self.current_cell_size = cell_size

        # Fruit takes about 68% of the cell
        size = int(cell_size * 0.68)

        size = max(25, size)

        self.image = pygame.transform.smoothscale(
            self.original_image,
            (size, size)
        )

    # ==============================================
    # DRAW
    # ==============================================

    def draw(self, screen):

        image_width = self.image.get_width()
        image_height = self.image.get_height()

        # Center fruit inside its cell
        draw_x = (
            self.x
            + (self.current_cell_size - image_width) / 2
        )

        draw_y = (
            self.y
            + (self.current_cell_size - image_height) / 2
        )

        screen.blit(
            self.image,
            (
                int(draw_x),
                int(draw_y)
            )
        )