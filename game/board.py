"""
board.py

This file manages the Candy Match game board.

The Board is responsible for:
- Creating the candy grid
- Storing all Candy objects
- Drawing the board
- Providing access to individual candies

Later, we will add:
- Candy swapping
- Match detection
- Removing candies
- Gravity
- New candy generation
"""


import random
import pygame

# Import our Candy class.
# The Board will create many Candy objects.
from game.candy import Candy

# Import all the settings from settings.py.
import settings


# =========================================================
# BOARD CLASS
# =========================================================

class Board:
    """
    Represents the complete Candy Match board.
    """

    def __init__(self):
        """
        Create a new game board.
        """

        # Create an empty list that will eventually contain
        # all rows of the board.
        #
        # The final structure will look like:
        #
        # board[0][0] → candy at row 0, column 0
        # board[0][1] → candy at row 0, column 1
        # board[1][0] → candy at row 1, column 0
        #
        # and so on.
        self.grid = []

        # Create all the candies and place them
        # into the grid.
        self.create_board()

    # =====================================================
    # CREATE BOARD
    # =====================================================

    def create_board(self):
        """
        Create a 6×6 grid and fill it with random candies.
        """

        # Go through each row.
        for row in range(settings.GRID_SIZE):

            # Create an empty list for the current row.
            current_row = []

            # Go through each column in the row.
            for column in range(settings.GRID_SIZE):

                # Randomly select a candy type.
                #
                # Example:
                # random number 0 → Red
                # random number 1 → Blue
                # random number 2 → Green
                # etc.
                
                # Create a Candy object using:
                # - its random type
                # - its row
                # - its column
                x = settings.BOARD_X + column * settings.CELL_SIZE
                y = settings.BOARD_Y + row * settings.CELL_SIZE

                candy = Candy(
                    row,
                    column,
                     x,
                     y
                )

                # Add the candy to the current row.
                current_row.append(candy)

            # Once the row is complete, add it to the board.
            self.grid.append(current_row)

    # =====================================================
    # DRAW BOARD
    # =====================================================

    def draw(self, screen):
        """
        Draw the board and all of its candies.
        """

        # Draw the individual cells first.
        #
        # This gives us a visible grid behind the candies.
        for row in range(settings.GRID_SIZE):

            for column in range(settings.GRID_SIZE):

                # Calculate the top-left pixel position
                # of this cell.
                x = (
                    settings.BOARD_X
                    + column * settings.CELL_SIZE
                )

                y = (
                    settings.BOARD_Y
                    + row * settings.CELL_SIZE
                )

                # Create a rectangle representing the cell.
                cell_rect = pygame.Rect(
                    x,
                    y,
                    settings.CELL_SIZE,
                    settings.CELL_SIZE
                )

                # Draw the cell.
                pygame.draw.rect(
                    screen,
                    settings.CELL_COLOR,
                    cell_rect
                )

                # Draw a border around the cell.
                pygame.draw.rect(
                    screen,
                    settings.WHITE,
                    cell_rect,
                    2
                )

        # Now draw every candy on top of the cells.
        for row in self.grid:

            for candy in row:

                # Tell the Candy object to draw itself.
                candy.draw(screen)