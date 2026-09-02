import pygame
import os

from game.candy import Candy
from settings import *


class FruitMatchGame:

    def __init__(self):

        pygame.init()

        try:
            pygame.mixer.init()
        except:
            pass

        # ==========================================
        # WINDOW
        # ==========================================

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE
        )

        pygame.display.set_caption("Fruity Match")

        self.clock = pygame.time.Clock()

        # ==========================================
        # PASTEL COLORS
        # ==========================================

        self.PINK = (255, 182, 203)
        self.LIGHT_PINK = (255, 221, 232)

        self.CREAM = (255, 247, 226)
        self.WHITE = (255, 255, 255)

        self.PEACH = (255, 205, 180)
        self.YELLOW = (255, 232, 170)

        self.LAVENDER = (225, 210, 245)
        self.MINT = (205, 238, 218)
        self.BABY_BLUE = (205, 230, 245)

        self.DARK_PINK = (174, 82, 112)
        self.BROWN = (117, 75, 62)

        self.GRID_BORDER = (244, 202, 216)
        self.SHADOW = (218, 170, 185)

        # ==========================================
        # GAME SETTINGS
        # ==========================================

        self.rows = 8
        self.cols = 8

        self.cell_size = 70

        self.board_width = 0
        self.board_height = 0

        self.board_x = 0
        self.board_y = 0

        # ==========================================
        # GAME STATE
        # ==========================================

        self.state = "start"

        self.candies = []

        self.selected_candy = None

        self.score = 0
        self.moves = 20

        self.game_over = False

        # ==========================================
        # BEST SCORE
        # ==========================================

        self.best_score_file = "best_score.txt"

        self.best_score = self.load_best_score()

        # ==========================================
        # MATCH ANIMATION
        # ==========================================

        self.match_animation = False

        self.matched_candies = set()

        self.animation_start = 0

        self.MATCH_DURATION = 250

        # ==========================================
        # SCORE POPUP
        # ==========================================

        self.score_popup = 0
        self.score_popup_start = 0

        # ==========================================
        # FONTS
        # ==========================================

        # Try to use a stylish cursive font
        cursive_path = pygame.font.match_font(
            [
                "segoe script",
                "segoe print",
                "comic sans ms",
                "brush script mt",
                "lucida handwriting"
            ]
        )

        if cursive_path:

            self.title_font = pygame.font.Font(
                cursive_path,
                82
            )

        else:

            self.title_font = pygame.font.Font(
                None,
                82
            )

        self.subtitle_font = pygame.font.Font(
            None,
            28
        )

        self.button_font = pygame.font.Font(
            None,
            34
        )

        self.score_font = pygame.font.Font(
            None,
            30
        )

        self.game_over_font = pygame.font.Font(
            None,
            60
        )

        # ==========================================
        # BACKGROUND
        # ==========================================

        self.background_original = None
        self.background = None

        background_path = os.path.join(
            "assets",
            "fruity_background.png"
        )

        if os.path.exists(background_path):

            try:

                self.background_original = pygame.image.load(
                    background_path
                ).convert()

                self.update_background()

            except:
                pass

        # ==========================================
        # SOUNDS
        # ==========================================

        self.swap_sound = self.load_sound(
            "swap.mp3"
        )

        self.pop_sound = self.load_sound(
            "pop.mp3"
        )

        self.splash_sound = self.load_sound(
            "splash.mp3"
        )

        self.gameover_sound = self.load_sound(
            "gameover.mp3"
        )

        # ==========================================
        # PLAY BUTTON
        # ==========================================

        self.play_button = pygame.Rect(
            0,
            0,
            280,
            75
        )

        # ==========================================
        # BOARD
        # ==========================================

        self.update_board_dimensions()

        self.create_board()

    # =================================================
    # BEST SCORE
    # =================================================

    def load_best_score(self):

        try:

            if os.path.exists(
                self.best_score_file
            ):

                with open(
                    self.best_score_file,
                    "r"
                ) as file:

                    return int(
                        file.read().strip()
                    )

        except:

            pass

        return 0

    def save_best_score(self):

        try:

            with open(
                self.best_score_file,
                "w"
            ) as file:

                file.write(
                    str(self.best_score)
                )

        except:

            pass

    def update_best_score(self):

        if self.score > self.best_score:

            self.best_score = self.score

            self.save_best_score()

    # =================================================
    # SOUND
    # =================================================

    def load_sound(self, filename):

        path = os.path.join(
            "assets",
            filename
        )

        if os.path.exists(path):

            try:

                return pygame.mixer.Sound(path)

            except:

                return None

        return None

    def play_sound(self, sound):

        if sound is not None:

            try:

                sound.play()

            except:

                pass

    # =================================================
    # BACKGROUND
    # =================================================

    def update_background(self):

        if self.background_original:

            self.background = pygame.transform.smoothscale(

                self.background_original,

                (
                    self.screen_width,
                    self.screen_height
                )

            )

    # =================================================
    # BOARD DIMENSIONS
    # =================================================

    def update_board_dimensions(self):

        available_width = (
            self.screen_width - 120
        )

        available_height = (
            self.screen_height - 180
        )

        max_cell_width = (
            available_width // self.cols
        )

        max_cell_height = (
            available_height // self.rows
        )

        self.cell_size = min(
            max_cell_width,
            max_cell_height
        )

        self.cell_size = max(
            45,
            self.cell_size
        )

        self.board_width = (
            self.cols * self.cell_size
        )

        self.board_height = (
            self.rows * self.cell_size
        )

        self.board_x = (
            self.screen_width
            - self.board_width
        ) // 2

        self.board_y = (

            125
            + (
                self.screen_height
                - 125
                - self.board_height
            ) // 2

        )

        self.update_candy_positions()

        self.update_background()

    # =================================================
    # CREATE BOARD
    # =================================================

    def create_board(self):

        # Generate a fresh board until it has no starting matches.
        # The attempt limit prevents the game from getting stuck
        # if random generation takes unusually long.
        attempts = 0
        max_attempts = 1000

        while attempts < max_attempts:

            attempts += 1

            self.candies = []

            for row in range(self.rows):

                for col in range(self.cols):

                    x = (
                        self.board_x
                        + col * self.cell_size
                    )

                    y = (
                        self.board_y
                        + row * self.cell_size
                    )

                    candy = Candy(
                        row,
                        col,
                        x,
                        y
                    )

                    self.candies.append(candy)

            # Do not allow the game to start with a match.
            if not self.find_matches():
                break

        # If needed, keep the last generated board rather than
        # leaving the game with an empty board.
    # UPDATE CANDY POSITIONS
    # =================================================

    def update_candy_positions(self):

        for candy in self.candies:

            candy.x = (
                self.board_x
                + candy.col * self.cell_size
            )

            candy.y = (
                self.board_y
                + candy.row * self.cell_size
            )

            if hasattr(
                candy,
                "resize"
            ):

                candy.resize(
                    self.cell_size
                )

    # =================================================
    # FIND MATCHES
    # =================================================

    def find_matches(self):

        matches = set()

        # ------------------------------------------
        # HORIZONTAL
        # ------------------------------------------

        for row in range(self.rows):

            row_candies = [

                candy
                for candy in self.candies

                if candy.row == row

            ]

            row_candies.sort(
                key=lambda candy: candy.col
            )

            for i in range(
                len(row_candies) - 2
            ):

                if (

                    row_candies[i].type
                    == row_candies[i + 1].type
                    == row_candies[i + 2].type

                ):

                    matches.add(
                        row_candies[i]
                    )

                    matches.add(
                        row_candies[i + 1]
                    )

                    matches.add(
                        row_candies[i + 2]
                    )

        # ------------------------------------------
        # VERTICAL
        # ------------------------------------------

        for col in range(self.cols):

            col_candies = [

                candy
                for candy in self.candies

                if candy.col == col

            ]

            col_candies.sort(
                key=lambda candy: candy.row
            )

            for i in range(
                len(col_candies) - 2
            ):

                if (

                    col_candies[i].type
                    == col_candies[i + 1].type
                    == col_candies[i + 2].type

                ):

                    matches.add(
                        col_candies[i]
                    )

                    matches.add(
                        col_candies[i + 1]
                    )

                    matches.add(
                        col_candies[i + 2]
                    )

        return matches

    # =================================================
    # GRAVITY
    # =================================================

    def apply_gravity(self):

        for col in range(self.cols):

            column_candies = [

                candy
                for candy in self.candies

                if candy.col == col

            ]

            column_candies.sort(

                key=lambda candy: candy.row,

                reverse=True

            )

            for new_row, candy in enumerate(
                column_candies
            ):

                target_row = (
                    self.rows
                    - 1
                    - new_row
                )

                candy.row = target_row

                candy.x = (
                    self.board_x
                    + col * self.cell_size
                )

                candy.y = (
                    self.board_y
                    + target_row
                    * self.cell_size
                )

    # =================================================
    # FILL EMPTY SPACES
    # =================================================

    def fill_empty_spaces(self):

        for row in range(self.rows):

            for col in range(self.cols):

                occupied = any(

                    candy.row == row
                    and candy.col == col

                    for candy in self.candies

                )

                if not occupied:

                    x = (
                        self.board_x
                        + col * self.cell_size
                    )

                    y = (
                        self.board_y
                        + row * self.cell_size
                    )

                    new_candy = Candy(
                        row,
                        col,
                        x,
                        y
                    )

                    if hasattr(
                        new_candy,
                        "resize"
                    ):

                        new_candy.resize(
                            self.cell_size
                        )

                    self.candies.append(
                        new_candy
                    )

    # =================================================
    # SWAP
    # =================================================

    def swap_candies(
        self,
        candy1,
        candy2
    ):

        temp_x = candy1.x
        temp_y = candy1.y

        candy1.x = candy2.x
        candy1.y = candy2.y

        candy2.x = temp_x
        candy2.y = temp_y

        temp_row = candy1.row
        temp_col = candy1.col

        candy1.row = candy2.row
        candy1.col = candy2.col

        candy2.row = temp_row
        candy2.col = temp_col

    # =================================================
    # HANDLE CLICK
    # =================================================

    def handle_game_click(self, mouse_x, mouse_y):

    # If game is over, only allow restart
        if self.game_over:
            restart_button = pygame.Rect(
                self.screen_width // 2 - 125,
                self.screen_height // 2 + 70,
                250,
                65
            )

            if restart_button.collidepoint(mouse_x, mouse_y):
                self.restart_game()

            return

        # Don't allow clicking while fruits are being removed/animated
        if self.match_animation:
            return

        # No moves left
        if self.moves <= 0:
            return

        # -------------------------------------------------
        # FIND WHICH FRUIT WAS CLICKED
        # -------------------------------------------------

        clicked_candy = None

        for candy in self.candies:
            rect = pygame.Rect(
                int(candy.x),
                int(candy.y),
                self.cell_size,
                self.cell_size
            )

            if rect.collidepoint(mouse_x, mouse_y):
                clicked_candy = candy
                break

        # Clicked outside the board
        if clicked_candy is None:
            return

        # -------------------------------------------------
        # FIRST FRUIT SELECTION
        # -------------------------------------------------

        if self.selected_candy is None:
            self.selected_candy = clicked_candy
            return

        # -------------------------------------------------
        # SECOND FRUIT SELECTION
        # -------------------------------------------------

        first = self.selected_candy
        second = clicked_candy

        row_difference = abs(first.row - second.row)
        col_difference = abs(first.col - second.col)

        # -------------------------------------------------
        # ONLY ADJACENT FRUITS CAN BE SWAPPED
        # -------------------------------------------------

        if row_difference + col_difference != 1:

            # If the player clicks another non-adjacent fruit,
            # make that fruit the new selection.
            self.selected_candy = clicked_candy
            return

        # -------------------------------------------------
        # SWAP THE TWO FRUITS
        # -------------------------------------------------

        self.play_sound(self.swap_sound)

        self.swap_candies(first, second)

        # -------------------------------------------------
        # EVERY VALID SWAP USES ONE MOVE
        # -------------------------------------------------

        self.moves -= 1

        # -------------------------------------------------
        # CHECK FOR MATCHES
        # -------------------------------------------------

        matches = self.find_matches()

        if matches:

            # Give points for the matched fruits
            gained_score = len(matches) * 10

            self.score += gained_score

            self.update_best_score()

            # Score popup
            self.score_popup = gained_score
            self.score_popup_start = pygame.time.get_ticks()

            # Store matched fruits
            self.matched_candies = matches

            # Start match animation
            self.match_animation = True
            self.animation_start = pygame.time.get_ticks()

            # Play match sound
            self.play_sound(self.pop_sound)

        else:

            # IMPORTANT:
            # DO NOT SWAP THE FRUITS BACK.
            #
            # The swap remains on the board even though
            # it did not create a match.
            #
            # Score remains unchanged.

            pass

        # Clear current selection
        self.selected_candy = None

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

        if self.moves <= 0:

            self.game_over = True

            self.update_best_score()

            self.play_sound(self.gameover_sound)

    # =================================================
    # FINISH MATCH
    # =================================================

    def finish_match(self):

        # Remove the currently matched fruits
        for candy in self.matched_candies:

            if candy in self.candies:

                self.candies.remove(candy)

        # Play splash sound
        self.play_sound(
            self.splash_sound
        )

        # Move remaining fruits downward
        self.apply_gravity()

        # Create new fruits
        self.fill_empty_spaces()

        # Update their positions
        self.update_candy_positions()

        # Clear previous match
        self.matched_candies = set()

        # Stop the current animation before checking the new board.
        self.match_animation = False

        # =================================================
        # CHECK FOR AUTOMATIC / CASCADE MATCH
        # =================================================

        new_matches = self.find_matches()

        if new_matches:

            # A cascade gives score but does NOT use another move.
            gained_score = (
                len(new_matches) * 10
            )

            self.score += gained_score

            self.update_best_score()

            # Show score popup for the cascade.
            self.score_popup = gained_score

            self.score_popup_start = (
                pygame.time.get_ticks()
            )

            # Store the cascade match.
            self.matched_candies = new_matches

            # Start the next match animation.
            self.match_animation = True

            self.animation_start = (
                pygame.time.get_ticks()
            )

            self.play_sound(
                self.pop_sound
            )

    # =================================================
    # UPDATE ANIMATION
    # =================================================

    def update_animation(self):

        if not self.match_animation:

            return

        elapsed = (

            pygame.time.get_ticks()
            - self.animation_start

        )

        if elapsed >= self.MATCH_DURATION:

            self.finish_match()

    # =================================================
    # START SCREEN
    # =================================================

    def draw_start_screen(self):

        # ==========================================
        # BACKGROUND
        # ==========================================

        if self.background:

            self.screen.blit(
                self.background,
                (0, 0)
            )

        else:

            self.screen.fill(
                self.LIGHT_PINK
            )

        # ==========================================
        # SOFT OVERLAY
        # ==========================================

        overlay = pygame.Surface(

            (
                self.screen_width,
                self.screen_height
            ),

            pygame.SRCALPHA

        )

        overlay.fill(
            (
                255,
                235,
                242,
                90
            )
        )

        self.screen.blit(
            overlay,
            (0, 0)
        )

        # ==========================================
        # TITLE
        # ==========================================

        title_font_size = max(

            50,

            min(
                90,
                self.screen_width // 9
            )

        )

        title_font = pygame.font.Font(

            pygame.font.match_font(

                [
                    "segoe script",
                    "segoe print",
                    "comic sans ms",
                    "brush script mt",
                    "lucida handwriting"
                ]

            )
            if pygame.font.match_font(

                [
                    "segoe script",
                    "segoe print",
                    "comic sans ms",
                    "brush script mt",
                    "lucida handwriting"
                ]

            )
            else None,

            title_font_size

        )

        title = title_font.render(

            "Fruity Match",

            True,

            self.DARK_PINK

        )

        title_shadow = title_font.render(

            "Fruity Match",

            True,

            self.WHITE

        )

        title_x = (

            self.screen_width
            - title.get_width()

        ) // 2

        title_y = (

            self.screen_height // 2
            - 190

        )

        # White soft shadow
        self.screen.blit(

            title_shadow,

            (
                title_x + 4,
                title_y + 6
            )

        )

        self.screen.blit(

            title,

            (
                title_x,
                title_y
            )

        )

        # ==========================================
        # SUBTITLE
        # ==========================================

        subtitle = self.subtitle_font.render(

            "MATCH  •  SPLASH  •  WIN",

            True,

            self.BROWN

        )

        self.screen.blit(

            subtitle,

            (

                self.screen_width // 2
                - subtitle.get_width() // 2,

                title_y
                + title.get_height()
                + 15

            )

        )

        # ==========================================
        # PLAY BUTTON
        # ==========================================

        button_width = min(

            300,

            self.screen_width - 70

        )

        button_height = 78

        button_x = (

            self.screen_width
            - button_width

        ) // 2

        button_y = (

            self.screen_height // 2
            + 25

        )

        self.play_button = pygame.Rect(

            button_x,
            button_y,

            button_width,
            button_height

        )

        mouse_pos = pygame.mouse.get_pos()

        hovering = (

            self.play_button.collidepoint(
                mouse_pos
            )

        )

        # Button shadow
        shadow_rect = self.play_button.copy()

        shadow_rect.y += 7

        pygame.draw.rect(

            self.screen,

            self.SHADOW,

            shadow_rect,

            border_radius=35

        )

        # Button color
        if hovering:

            button_color = self.PEACH

        else:

            button_color = self.PINK

        # Main button
        pygame.draw.rect(

            self.screen,

            button_color,

            self.play_button,

            border_radius=35

        )

        # White border
        pygame.draw.rect(

            self.screen,

            self.WHITE,

            self.play_button,

            4,

            border_radius=35

        )
            # ==========================================
    # PLAY ICON + TEXT
    # ==========================================

        play_text = self.button_font.render(
            "PLAY",
            True,
            self.WHITE
        )

        # Play triangle
        triangle_size = 18

        triangle_x = (
            self.play_button.centerx
            - play_text.get_width() // 2
            - 35
        )

        triangle_y = self.play_button.centery

        pygame.draw.polygon(
            self.screen,
            self.WHITE,
            [
                (
                    triangle_x,
                    triangle_y - triangle_size
                ),
                (
                    triangle_x,
                    triangle_y + triangle_size
                ),
                (
                    triangle_x + triangle_size,
                    triangle_y
                )
            ]
        )

        # PLAY text
        self.screen.blit(
            play_text,
            (
                self.play_button.centerx
                - play_text.get_width() // 2
                + 15,

                self.play_button.centery
                - play_text.get_height() // 2
            )
        )

            

        # ==========================================
        # BEST SCORE
        # ==========================================

        best_text = self.score_font.render(

            f"🏆  BEST SCORE: {self.best_score}",

            True,

            self.BROWN

        )

        self.screen.blit(

            best_text,

            (

                self.screen_width // 2
                - best_text.get_width() // 2,

                button_y
                + button_height
                + 25

            )

        )

        # ==========================================
        # DECORATIVE CIRCLES
        # ==========================================

        decorative_positions = [

            (
                int(self.screen_width * 0.12),
                int(self.screen_height * 0.27),
                self.PEACH
            ),

            (
                int(self.screen_width * 0.88),
                int(self.screen_height * 0.28),
                self.YELLOW
            ),

            (
                int(self.screen_width * 0.15),
                int(self.screen_height * 0.75),
                self.MINT
            ),

            (
                int(self.screen_width * 0.86),
                int(self.screen_height * 0.74),
                self.LAVENDER
            )

        ]

        for x, y, color in decorative_positions:

            pygame.draw.circle(

                self.screen,

                color,

                (x, y),

                38

            )

            pygame.draw.circle(

                self.screen,

                self.WHITE,

                (x, y),

                38,

                3

            )

        pygame.display.flip()

    # =================================================
    # HEADER
    # =================================================

    def draw_header(self):

        header_height = 105

        # Shadow
        pygame.draw.rect(

            self.screen,

            self.SHADOW,

            (
                0,
                5,
                self.screen_width,
                header_height
            )

        )

        # Header
        pygame.draw.rect(

            self.screen,

            self.PINK,

            (
                0,
                0,
                self.screen_width,
                header_height
            )

        )

        margin = 15

        gap = 10

        usable_width = (

            self.screen_width
            - margin * 2
            - gap * 2

        )

        box_width = min(

            330,

            usable_width // 3

        )

        total_width = (

            box_width * 3
            + gap * 2

        )

        start_x = (

            self.screen_width
            - total_width

        ) // 2

        box_y = 18

        box_height = 68

        boxes = [

            pygame.Rect(

                start_x,
                box_y,

                box_width,
                box_height

            ),

            pygame.Rect(

                start_x
                + box_width
                + gap,

                box_y,

                box_width,
                box_height

            ),

            pygame.Rect(

                start_x
                + (box_width + gap) * 2,

                box_y,

                box_width,
                box_height

            )

        ]

        # Different pastel header boxes
        box_colors = [

            self.CREAM,
            self.LIGHT_PINK,
            self.CREAM

        ]

        for box, color in zip(
            boxes,
            box_colors
        ):

            pygame.draw.rect(

                self.screen,

                color,

                box,

                border_radius=28

            )

            pygame.draw.rect(

                self.screen,

                self.WHITE,

                box,

                3,

                border_radius=28

            )

        font_size = max(

            18,

            min(
                38,
                int(box_width * 0.15)
            )

        )

        header_font = pygame.font.Font(

            None,

            font_size

        )

        texts = [

            "FRUITY MATCH",

            f"SCORE: {self.score}",

            f"MOVES: {self.moves}"

        ]

        colors = [

            self.DARK_PINK,
            self.BROWN,
            self.BROWN

        ]

        for box, text, color in zip(

            boxes,
            texts,
            colors

        ):

            rendered = header_font.render(

                text,

                True,

                color

            )

            # Automatically shrink if needed
            while (

                rendered.get_width()
                > box.width - 20

                and font_size > 15

            ):

                font_size -= 1

                header_font = pygame.font.Font(

                    None,

                    font_size

                )

                rendered = header_font.render(

                    text,

                    True,

                    color

                )

            self.screen.blit(

                rendered,

                (

                    box.centerx
                    - rendered.get_width() // 2,

                    box.centery
                    - rendered.get_height() // 2

                )

            )

    # =================================================
    # PASTEL GRID
    # =================================================

    def draw_board(self):

        # ==========================================
        # OUTER BOARD SHADOW
        # ==========================================

        shadow_rect = pygame.Rect(

            self.board_x - 16,
            self.board_y - 16,

            self.board_width + 32,
            self.board_height + 32

        )

        pygame.draw.rect(

            self.screen,

            self.SHADOW,

            shadow_rect,

            border_radius=32

        )

        # ==========================================
        # PASTEL BOARD
        # ==========================================

        outer_rect = pygame.Rect(

            self.board_x - 13,
            self.board_y - 13,

            self.board_width + 26,
            self.board_height + 26

        )

        pygame.draw.rect(

            self.screen,

            self.PINK,

            outer_rect,

            border_radius=30

        )

        # ==========================================
        # INNER CREAM AREA
        # ==========================================

        inner_rect = pygame.Rect(

            self.board_x - 6,
            self.board_y - 6,

            self.board_width + 12,
            self.board_height + 12

        )

        pygame.draw.rect(

            self.screen,

            self.CREAM,

            inner_rect,

            border_radius=25

        )

        pygame.draw.rect(

            self.screen,

            self.WHITE,

            inner_rect,

            3,

            border_radius=25

        )

        # ==========================================
        # PASTEL GRID CELLS
        # ==========================================

        pastel_cells = [

            self.LIGHT_PINK,
            self.CREAM,
            self.LAVENDER,
            self.MINT,
            self.BABY_BLUE,
            self.PEACH

        ]

        for row in range(self.rows):

            for col in range(self.cols):

                x = (

                    self.board_x
                    + col * self.cell_size

                )

                y = (

                    self.board_y
                    + row * self.cell_size

                )

                cell_rect = pygame.Rect(

                    int(x + 3),
                    int(y + 3),

                    self.cell_size - 6,
                    self.cell_size - 6

                )

                # Alternating soft pastel colors
                color_index = (

                    row + col
                ) % len(
                    pastel_cells
                )

                cell_color = pastel_cells[
                    color_index
                ]

                # Cell shadow
                shadow = pygame.Rect(

                    int(x + 5),
                    int(y + 6),

                    self.cell_size - 8,
                    self.cell_size - 8

                )

                pygame.draw.rect(

                    self.screen,

                    self.SHADOW,

                    shadow,

                    border_radius=16

                )

                # Cell
                pygame.draw.rect(

                    self.screen,

                    cell_color,

                    cell_rect,

                    border_radius=16

                )

                # Cell border
                pygame.draw.rect(

                    self.screen,

                    self.WHITE,

                    cell_rect,

                    2,

                    border_radius=16

                )

        # ==========================================
        # FRUITS
        # ==========================================

        for candy in self.candies:

            candy.draw(
                self.screen
            )

        # ==========================================
        # MATCH ANIMATION
        # ==========================================

        if self.match_animation:

            elapsed = (

                pygame.time.get_ticks()
                - self.animation_start

            )

            progress = min(

                elapsed
                / self.MATCH_DURATION,

                1

            )

            for candy in self.matched_candies:

                if candy not in self.candies:

                    continue

                flash_rect = pygame.Rect(

                    int(candy.x + 4),
                    int(candy.y + 4),

                    self.cell_size - 8,
                    self.cell_size - 8

                )

                pygame.draw.rect(

                    self.screen,

                    self.WHITE,

                    flash_rect,

                    4,

                    border_radius=16

                )

                radius = int(

                    8
                    + progress * 30

                )

                pygame.draw.circle(

                    self.screen,

                    self.WHITE,

                    (

                        int(

                            candy.x
                            + self.cell_size / 2

                        ),

                        int(

                            candy.y
                            + self.cell_size / 2

                        )

                    ),

                    radius,

                    3

                )

        # ==========================================
        # SELECTED FRUIT
        # ==========================================

        if self.selected_candy:

            selected_rect = pygame.Rect(

                int(
                    self.selected_candy.x + 2
                ),

                int(
                    self.selected_candy.y + 2
                ),

                self.cell_size - 4,
                self.cell_size - 4

            )

            pygame.draw.rect(

                self.screen,

                self.WHITE,

                selected_rect,

                5,

                border_radius=17

            )

            pygame.draw.rect(

                self.screen,

                self.DARK_PINK,

                selected_rect,

                2,

                border_radius=17

            )

    # =================================================
    # SCORE POPUP
    # =================================================

    def draw_score_popup(self):

        if self.score_popup <= 0:

            return

        elapsed = (

            pygame.time.get_ticks()
            - self.score_popup_start

        )

        if elapsed >= 800:

            self.score_popup = 0

            return

        progress = elapsed / 800

        popup = self.score_font.render(

            f"+{self.score_popup}!",

            True,

            self.DARK_PINK

        )

        popup.set_alpha(

            int(
                255 * (1 - progress)
            )

        )

        x = (

            self.screen_width // 2
            - popup.get_width() // 2

        )

        y = int(

            self.board_y
            - 45
            - progress * 30

        )

        self.screen.blit(

            popup,

            (x, y)

        )

    # =================================================
    # GAME OVER
    # =================================================

    def draw_game_over(self):

        if not self.game_over:

            return

        overlay = pygame.Surface(

            (
                self.screen_width,
                self.screen_height
            ),

            pygame.SRCALPHA

        )

        overlay.fill(

            (
                255,
                210,
                225,
                190
            )

        )

        self.screen.blit(

            overlay,

            (0, 0)

        )

        panel_width = min(

            500,

            self.screen_width - 40

        )

        panel_height = 350

        panel = pygame.Rect(

            self.screen_width // 2
            - panel_width // 2,

            self.screen_height // 2
            - panel_height // 2,

            panel_width,

            panel_height

        )

        pygame.draw.rect(

            self.screen,

            self.CREAM,

            panel,

            border_radius=35

        )

        pygame.draw.rect(

            self.screen,

            self.PINK,

            panel,

            6,

            border_radius=35

        )

        text = self.game_over_font.render(

            "GAME OVER!",

            True,

            self.DARK_PINK

        )

        self.screen.blit(

            text,

            (

                panel.centerx
                - text.get_width() // 2,

                panel.y + 35

            )

        )

        final_score = self.score_font.render(

            f"FINAL SCORE: {self.score}",

            True,

            self.BROWN

        )

        self.screen.blit(

            final_score,

            (

                panel.centerx
                - final_score.get_width() // 2,

                panel.y + 125

            )

        )

        best_score = self.score_font.render(

            f"BEST SCORE: {self.best_score}",

            True,

            self.BROWN

        )

        self.screen.blit(

            best_score,

            (

                panel.centerx
                - best_score.get_width() // 2,

                panel.y + 165

            )

        )

        restart_button = pygame.Rect(

            panel.centerx - 125,

            panel.y + 225,

            250,

            65

        )

        pygame.draw.rect(

            self.screen,

            self.PINK,

            restart_button,

            border_radius=28

        )

        restart_text = self.button_font.render(

            "PLAY AGAIN",

            True,

            self.WHITE

        )

        self.screen.blit(

            restart_text,

            (

                restart_button.centerx
                - restart_text.get_width() // 2,

                restart_button.centery
                - restart_text.get_height() // 2

            )

        )

    # =================================================
    # RESTART
    # =================================================

    def restart_game(self):

        self.score = 0

        self.moves = 20

        self.game_over = False

        self.match_animation = False

        self.matched_candies = set()

        self.selected_candy = None

        self.score_popup = 0

        self.create_board()

        self.state = "game"

    # =================================================
    # DRAW GAME
    # =================================================

    def draw_game(self):

        if self.background:

            self.screen.blit(

                self.background,

                (0, 0)

            )

        else:

            self.screen.fill(

                self.LIGHT_PINK

            )

        self.draw_header()

        self.draw_board()

        self.draw_score_popup()

        self.draw_game_over()

        pygame.display.flip()

    # =================================================
    # MAIN LOOP
    # =================================================

    def run(self):

        running = True

        while running:

            for event in pygame.event.get():

                # ==================================
                # QUIT
                # ==================================

                if event.type == pygame.QUIT:

                    running = False

                # ==================================
                # RESIZE
                # ==================================

                elif event.type == pygame.VIDEORESIZE:

                    self.screen_width = event.w

                    self.screen_height = event.h

                    self.screen = pygame.display.set_mode(

                        (
                            self.screen_width,
                            self.screen_height
                        ),

                        pygame.RESIZABLE

                    )

                    self.update_board_dimensions()

                # ==================================
                # MOUSE CLICK
                # ==================================

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    mouse_x, mouse_y = (
                        pygame.mouse.get_pos()
                    )

                    # ------------------------------
                    # START SCREEN
                    # ------------------------------

                    if self.state == "start":

                        if self.play_button.collidepoint(

                            mouse_x,
                            mouse_y

                        ):

                            self.play_sound(
                                self.swap_sound
                            )

                            self.state = "game"

                            self.score = 0

                            self.moves = 20

                            self.game_over = False

                            self.create_board()

                    # ------------------------------
                    # GAME
                    # ------------------------------

                    elif self.state == "game":

                        self.handle_game_click(

                            mouse_x,
                            mouse_y

                        )

            # ======================================
            # UPDATE
            # ======================================

            if self.state == "game":

                self.update_animation()

            # ======================================
            # DRAW
            # ======================================

            if self.state == "start":

                self.draw_start_screen()

            else:

                self.draw_game()

            self.clock.tick(FPS)

        pygame.quit()


# =====================================================
# START GAME
# =====================================================

if __name__ == "__main__":

    game = FruitMatchGame()

    game.run()