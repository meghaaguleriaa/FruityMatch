import pygame
import os
import random

from game.candy import Candy
from settings import *


class FruitMatchGame:

    def __init__(self):
        pygame.init()

        try:
            pygame.mixer.init()
        except pygame.error:
            pass

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Fruity Match")
        self.clock = pygame.time.Clock()

        # Pastel theme
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

        self.rows = 8
        self.cols = 8
        self.cell_size = 70
        self.board_width = 0
        self.board_height = 0
        self.board_x = 0
        self.board_y = 0

        self.state = "start"
        self.candies = []
        self.selected_candy = None
        self.score = 0
        self.moves = 20
        self.game_over = False

        # 10-level Candy Crush-style progression
        self.level = 1
        self.level_score = 0
        self.level_complete = False
        self.level_failed = False
        self.fruit_collected = {fruit: 0 for fruit in Candy.TYPES}
        self.striped_created = 0
        self.color_bombs_created = 0
        self.wrapped_created = 0
        self.ice_positions = set()
        self.ice_cleared = 0
        self.level_stars = 0
        self.levels = [
            # Easy introduction: normal 3-match gameplay.
            {"objective": "Score 150 points", "type": "score", "target": 150, "moves": 10, "ice": 0},

            # Introduces the 4-match striped candy without making the level long.
            {"objective": "Create 1 striped candy", "type": "striped", "target": 1, "moves": 14, "ice": 0, "special_opportunity": "striped"},

            # Showcase level: ice + all three major special types are placed on the board.
            {"objective": "Clear 6 ice blocks", "type": "ice", "target": 6, "moves": 20, "ice": 6, "showcase": True},

            # Score and striped candies together.
            {"objective": "Score 500 + create 2 striped candies", "type": "score_striped", "target": 500, "striped_target": 2, "moves": 20, "ice": 0, "special_opportunity": "striped"},

            # First real blocker challenge.
            {"objective": "Clear 12 ice blocks", "type": "ice", "target": 12, "moves": 24, "ice": 12},

            # Color bomb becomes the main objective.
            {"objective": "Create 1 color bomb", "type": "bomb", "target": 1, "moves": 24, "ice": 0, "special_opportunity": "bomb"},

            # Mixed collection challenge.
            {"objective": "Collect 15 grapes + 15 cherries", "type": "collect_two", "fruit1": "grape", "fruit2": "cherry", "target": 15, "moves": 26, "ice": 4},

            # More specials and a larger score target.
            {"objective": "Create 2 color bombs", "type": "bomb", "target": 2, "moves": 28, "ice": 6, "special_opportunity": "bomb"},

            # Combined blocker + score challenge.
            {"objective": "Clear 18 ice + score 1200", "type": "ice_score", "target": 18, "score_target": 1200, "moves": 30, "ice": 18},

            # Final level.
            {"objective": "Final challenge: score 2500", "type": "score", "target": 2500, "moves": 32, "ice": 10},
        ]

        self.best_score_file = "best_score.txt"
        self.best_score = self.load_best_score()

        self.match_animation = False
        self.matched_candies = set()
        self.animation_start = 0
        self.MATCH_DURATION = 300

        self.score_popup = 0
        self.score_popup_start = 0

        self.shuffle_message_until = 0

        # Candy Crush-style hint system
        self.hint_candies = None
        self.last_action_time = pygame.time.get_ticks()
        self.HINT_DELAY = 7000

        cursive_path = pygame.font.match_font([
            "segoe script", "segoe print", "comic sans ms", "brush script mt"
        ])
        self.title_font = pygame.font.Font(cursive_path, 72) if cursive_path else pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 25)
        self.button_font = pygame.font.Font(None, 34)
        self.score_font = pygame.font.Font(None, 28)
        self.header_font = pygame.font.Font(None, 31)
        self.gameover_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 23)

        self.background = None
        self.load_background()

        self.ice_image = self.load_image("ice.png")
        self.bomb_image = self.load_image("bomb.png")
        self.star_image = self.load_image("star.png")
        self.lock_image = self.load_image("lock.png")

        self.pop_sound = self.load_sound("pop.mp3")
        self.splash_sound = self.load_sound("splash.mp3")
        self.swap_sound = self.load_sound("swap.mp3")
        self.gameover_sound = self.load_sound("gameover.mp3")

        self.update_board_dimensions()

        self.play_button = pygame.Rect(0, 0, 300, 70)
        self.update_play_button()

        self.create_board()

    # =====================================================
    # FILES / SOUND
    # =====================================================

    def load_best_score(self):
        try:
            with open(self.best_score_file, "r") as file:
                return int(file.read().strip())
        except (FileNotFoundError, ValueError, OSError):
            return 0

    def save_best_score(self):
        try:
            with open(self.best_score_file, "w") as file:
                file.write(str(self.best_score))
        except OSError:
            pass

    def update_best_score(self):
        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()

    def load_image(self, filename):
        path = os.path.join("assets", filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    def load_sound(self, filename):
        path = os.path.join("assets", filename)
        try:
            return pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            return None

    def play_sound(self, sound):
        if sound:
            try:
                sound.play()
            except pygame.error:
                pass

    def load_background(self):
        path = os.path.join("assets", "fruity_background.png")
        try:
            image = pygame.image.load(path).convert()
            self.background = pygame.transform.smoothscale(
                image, (self.screen_width, self.screen_height)
            )
        except (pygame.error, FileNotFoundError):
            self.background = None

    # =====================================================
    # BOARD SIZE
    # =====================================================

    def update_play_button(self):
        self.play_button = pygame.Rect(
            self.screen_width // 2 - 150,
            self.screen_height // 2 - 15,
            300,
            70
        )

    def update_board_dimensions(self):
        header_height = 170
        margin = 25
        available_width = self.screen_width - margin * 2
        available_height = self.screen_height - header_height - margin * 2

        self.cell_size = max(
            35,
            min(82, available_width // self.cols, available_height // self.rows)
        )

        self.board_width = self.cell_size * self.cols
        self.board_height = self.cell_size * self.rows
        self.board_x = (self.screen_width - self.board_width) // 2
        self.board_y = header_height + max(
            margin, (available_height - self.board_height) // 2
        )

        self.update_candy_positions()
        self.update_play_button()
        self.load_background()

    def update_candy_positions(self):
        for candy in self.candies:
            candy.x = self.board_x + candy.col * self.cell_size
            candy.y = self.board_y + candy.row * self.cell_size
            if hasattr(candy, "resize"):
                candy.resize(self.cell_size)

    # =====================================================
    # BOARD CREATION
    # =====================================================

    # =====================================================
    # LEVEL SYSTEM
    # =====================================================

    def current_level_data(self):
        return self.levels[self.level - 1]

    def reset_level_stats(self):
        self.level_score = 0
        self.fruit_collected = {fruit: 0 for fruit in Candy.TYPES}
        self.striped_created = 0
        self.color_bombs_created = 0
        self.ice_positions = set()
        self.ice_cleared = 0
        self.level_complete = False
        self.level_failed = False
        self.level_stars = 0

    def setup_level(self):
        data = self.current_level_data()
        self.moves = data["moves"]
        self.score = 0
        self.game_over = False
        self.selected_candy = None
        self.match_animation = False
        self.matched_candies = set()
        self.hint_candies = None
        self.shuffle_message_until = 0
        self.reset_level_stats()
        self.create_board()
        self.create_ice_blocks(data.get("ice", 0))

        # Level 3 is a short feature-showcase so the important special
        # mechanics are visible early in the demonstration.
        if data.get("showcase"):
            self.add_showcase_specials()

    def add_showcase_specials(self):
        showcase_positions = [
            ((2, 2), "striped_h"),
            ((2, 3), "striped_v"),
            ((5, 2), "wrapped"),
            ((5, 5), "color_bomb"),
        ]

        for (row, col), special in showcase_positions:
            candy = self.candy_at(row, col)
            if candy is not None:
                candy.special_type = special

    def create_ice_blocks(self, amount):
        self.ice_positions = set()
        if amount <= 0:
            return
        positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        random.shuffle(positions)
        protected = set()
        if self.current_level_data().get("showcase"):
            protected = {(2, 2), (2, 3), (5, 2), (5, 5)}

        for row, col in positions:
            if row == 0 and amount > 5:
                continue
            if (row, col) in protected:
                continue
            self.ice_positions.add((row, col))
            if len(self.ice_positions) >= amount:
                break

    def objective_progress(self):
        data=self.current_level_data(); kind=data["type"]
        if kind == "score": return min(self.level_score/data["target"],1), f"{self.level_score} / {data['target']}"
        if kind == "score_striped":
            score_progress = min(self.level_score/data["target"], 1)
            striped_progress = min(self.striped_created/data["striped_target"], 1)
            return min(score_progress, striped_progress), f"Score {self.level_score}/{data['target']}  Striped {self.striped_created}/{data['striped_target']}"
        if kind == "collect":
            v=self.fruit_collected[data["fruit"]]; return min(v/data["target"],1), f"{v} / {data['target']}"
        if kind == "collect_two":
            a=self.fruit_collected[data["fruit1"]]; b=self.fruit_collected[data["fruit2"]]
            return min(a/data["target"],b/data["target"],1), f"Grapes {a}/{data['target']}  Cherries {b}/{data['target']}"
        if kind == "striped": return min(self.striped_created/data["target"],1), f"{self.striped_created} / {data['target']}"
        if kind == "bomb": return min(self.color_bombs_created/data["target"],1), f"{self.color_bombs_created} / {data['target']}"
        if kind == "ice": return min(self.ice_cleared/data["target"],1), f"{self.ice_cleared} / {data['target']}"
        if kind == "ice_score": return min(self.ice_cleared/data["target"],self.level_score/data["score_target"],1), f"Ice {self.ice_cleared}/{data['target']}  Score {self.level_score}/{data['score_target']}"
        return 0,""

    def objective_met(self):
        data=self.current_level_data(); kind=data["type"]
        if kind == "score": return self.level_score >= data["target"]
        if kind == "score_striped": return self.level_score >= data["target"] and self.striped_created >= data["striped_target"]
        if kind == "collect": return self.fruit_collected[data["fruit"]] >= data["target"]
        if kind == "collect_two": return self.fruit_collected[data["fruit1"]] >= data["target"] and self.fruit_collected[data["fruit2"]] >= data["target"]
        if kind == "striped": return self.striped_created >= data["target"]
        if kind == "bomb": return self.color_bombs_created >= data["target"]
        if kind == "ice": return self.ice_cleared >= data["target"]
        if kind == "ice_score": return self.ice_cleared >= data["target"] and self.level_score >= data["score_target"]
        return False

    def calculate_stars(self):
        if not self.objective_met(): return 0
        data=self.current_level_data()
        if data["type"] in ("score", "score_striped"):
            ratio=self.level_score/data["target"]
            return 3 if ratio >= 2 else 2 if ratio >= 1.5 else 1
        return 3 if self.moves >= data["moves"]*0.45 else 2 if self.moves >= data["moves"]*0.2 else 1

    def check_level_state(self):
        if self.level_complete or self.level_failed:
            return

        # Completing the objective always takes priority over running out
        # of moves on the same move. This guarantees the completion screen
        # and NEXT LEVEL button are shown in a clean state.
        if self.objective_met():
            self.level_complete = True
            self.level_failed = False
            self.game_over = False
            self.level_stars = self.calculate_stars()
            return

        if self.moves <= 0:
            self.level_failed = True
            self.game_over = True

    def next_level(self):
        # Move to the next level and reset all level-specific state.
        if self.level >= len(self.levels):
            self.state = "start"
            self.level = 1
            self.level_complete = False
            self.level_failed = False
            self.game_over = False
            return

        self.level += 1
        self.setup_level()
        self.state = "game"
        self.level_complete = False
        self.level_failed = False
        self.game_over = False
        self.last_action_time = pygame.time.get_ticks()

    def new_candy(self, row, col):
        candy = Candy(
            row,
            col,
            self.board_x + col * self.cell_size,
            self.board_y + row * self.cell_size
        )
        candy.special_type = None
        return candy

    def create_board(self):
        # Create a board quickly. The previous version searched through
        # hundreds of full board states and could freeze when moving to a
        # level that required a special-candy opportunity.
        for _ in range(80):
            self.candies = []

            for row in range(self.rows):
                for col in range(self.cols):
                    self.candies.append(self.new_candy(row, col))

            if not self.find_matches() and self.count_possible_moves() >= 6:
                break

        # Give levels that demonstrate special candies a guaranteed, quick
        # opportunity instead of performing an expensive search.
        wanted = self.current_level_data().get("special_opportunity")
        if wanted:
            self.make_special_opportunity(wanted)

        self.update_candy_positions()
        self.hint_candies = None
        self.last_action_time = pygame.time.get_ticks()

    def make_special_opportunity(self, wanted_special):
        # Build a safe pattern where one simple swap creates the required
        # special. For a striped candy: A A B A -> swap B/A.
        # For a color bomb: A A B A A -> swap B/A.
        # Try several rows/fruit types and keep the first board with no
        # automatic match. This is much faster than testing every swap.
        if wanted_special == "striped":
            patterns = [(0, 1, 3)]
        elif wanted_special == "bomb":
            patterns = [(0, 1, 3, 4)]
        else:
            return

        for _ in range(40):
            row = random.randint(1, self.rows - 2)
            start = random.randint(0, self.cols - (5 if wanted_special == "bomb" else 4))
            fruit = random.choice(Candy.TYPES)
            other = random.choice([x for x in Candy.TYPES if x != fruit])

            positions = [start + offset for offset in patterns[0]]
            gap_col = start + 2

            old_types = {}
            for col in positions + [gap_col]:
                candy = self.candy_at(row, col)
                if candy:
                    old_types[(row, col)] = candy.type
                    candy.type = fruit if col in positions else other
                    image_path = os.path.join("assets", candy.type + ".png")
                    candy.original_image = pygame.image.load(image_path).convert_alpha()
                    candy.resize(self.cell_size)

            # Also check that the changed cells did not accidentally create
            # an existing match elsewhere on the board.
            if not self.find_matches():
                return

            # Restore and try another location/type.
            for (r, c), old_type in old_types.items():
                candy = self.candy_at(r, c)
                candy.type = old_type
                image_path = os.path.join("assets", candy.type + ".png")
                candy.original_image = pygame.image.load(image_path).convert_alpha()
                candy.resize(self.cell_size)

    def candy_at(self, row, col):
        for candy in self.candies:
            if candy.row == row and candy.col == col:
                return candy
        return None

    # =====================================================
    # MATCH DETECTION
    # =====================================================

    def find_match_groups(self):
        """Return complete connected match groups.

        A row of 8 identical fruits is one group of 8, not two groups of 4.
        Crossing horizontal/vertical runs are merged into one group.
        """
        raw = []

        # Horizontal complete runs
        for row in range(self.rows):
            line = sorted(
                [c for c in self.candies if c.row == row],
                key=lambda c: c.col
            )
            i = 0
            while i < len(line):
                j = i + 1
                while (
                    j < len(line)
                    and line[j].type == line[i].type
                    and line[j].col == line[j - 1].col + 1
                ):
                    j += 1
                if j - i >= 3:
                    raw.append({
                        "candies": set(line[i:j]),
                        "horizontal": True,
                        "vertical": False
                    })
                i = j

        # Vertical complete runs
        for col in range(self.cols):
            line = sorted(
                [c for c in self.candies if c.col == col],
                key=lambda c: c.row
            )
            i = 0
            while i < len(line):
                j = i + 1
                while (
                    j < len(line)
                    and line[j].type == line[i].type
                    and line[j].row == line[j - 1].row + 1
                ):
                    j += 1
                if j - i >= 3:
                    raw.append({
                        "candies": set(line[i:j]),
                        "horizontal": False,
                        "vertical": True
                    })
                i = j

        # Merge groups that cross/touch through a common candy.
        groups = []
        for item in raw:
            merged = False
            for group in groups:
                if group["candies"] & item["candies"]:
                    group["candies"] |= item["candies"]
                    group["horizontal"] |= item["horizontal"]
                    group["vertical"] |= item["vertical"]
                    merged = True
                    break
            if not merged:
                groups.append({
                    "candies": set(item["candies"]),
                    "horizontal": item["horizontal"],
                    "vertical": item["vertical"]
                })

        changed = True
        while changed:
            changed = False
            result = []
            for group in groups:
                merged = False
                for other in result:
                    if group["candies"] & other["candies"]:
                        other["candies"] |= group["candies"]
                        other["horizontal"] |= group["horizontal"]
                        other["vertical"] |= group["vertical"]
                        merged = True
                        changed = True
                        break
                if not merged:
                    result.append(group)
            groups = result

        return groups

    def find_matches(self):
        matches = set()
        for group in self.find_match_groups():
            matches |= group["candies"]
        return matches

    # =====================================================
    # CANDY CRUSH SPECIALS
    # =====================================================

    def get_special_for_group(self, group, preferred=None):
        candies = group["candies"]
        length = len(candies)
        position = preferred if preferred in candies else next(iter(candies))

        # T, L or + shape -> Wrapped Candy
        if group["horizontal"] and group["vertical"]:
            return "wrapped", position

        # Five or more in a straight line -> Color Bomb
        if length >= 5:
            return "color_bomb", position

        # Four in a straight line -> Striped Candy
        if length == 4:
            if group["horizontal"]:
                return "striped_h", position
            return "striped_v", position

        # Three -> normal match
        return None, None

    def activate_special(self, candy, clear_set, color_target=None):
        special = getattr(candy, "special_type", None)

        if special == "striped_h":
            clear_set.update(c for c in self.candies if c.row == candy.row)

        elif special == "striped_v":
            clear_set.update(c for c in self.candies if c.col == candy.col)

        elif special == "wrapped":
            clear_set.update(
                c for c in self.candies
                if abs(c.row - candy.row) <= 1
                and abs(c.col - candy.col) <= 1
            )

        elif special == "color_bomb" and color_target:
            clear_set.update(c for c in self.candies if c.type == color_target)

    def expand_special_effects(self, clear_set):
        """Activate special candies that are part of a match/effect."""
        processed = set()
        changed = True

        while changed:
            changed = False
            for candy in list(clear_set):
                if candy in processed:
                    continue

                processed.add(candy)
                special = getattr(candy, "special_type", None)
                before = len(clear_set)

                if special == "striped_h":
                    self.activate_special(candy, clear_set)
                elif special == "striped_v":
                    self.activate_special(candy, clear_set)
                elif special == "wrapped":
                    self.activate_special(candy, clear_set)

                if len(clear_set) > before:
                    changed = True

    def special_swap_effect(self, first, second):
        a = getattr(first, "special_type", None)
        b = getattr(second, "special_type", None)

        if not a and not b:
            return None

        # Color Bomb + Color Bomb -> clear entire board
        if a == "color_bomb" and b == "color_bomb":
            return set(self.candies)

        # Color Bomb + anything -> remove all fruits of the other fruit's type.
        if a == "color_bomb" or b == "color_bomb":
            bomb = first if a == "color_bomb" else second
            other = second if bomb is first else first
            target_type = other.type
            clear_set = {bomb, other}
            clear_set.update(c for c in self.candies if c.type == target_type)

            # If the other candy is special, activate that style on every
            # candy of the selected fruit type.
            other_special = getattr(other, "special_type", None)
            for candy in list(clear_set):
                if candy.type != target_type:
                    continue
                if other_special == "striped_h":
                    clear_set.update(c for c in self.candies if c.row == candy.row)
                elif other_special == "striped_v":
                    clear_set.update(c for c in self.candies if c.col == candy.col)
                elif other_special == "wrapped":
                    clear_set.update(
                        c for c in self.candies
                        if abs(c.row - candy.row) <= 1
                        and abs(c.col - candy.col) <= 1
                    )
            return clear_set

        # Striped + Striped -> row + column cross
        # Check the type first so a special candy swapped with a normal
        # candy never tries to call .startswith() on None.
        a_is_striped = isinstance(a, str) and a.startswith("striped")
        b_is_striped = isinstance(b, str) and b.startswith("striped")

        if a_is_striped and b_is_striped:
            clear_set = {first, second}
            clear_set.update(c for c in self.candies if c.row == first.row)
            clear_set.update(c for c in self.candies if c.col == first.col)
            return clear_set

        # Wrapped + Wrapped -> large explosion
        if a == "wrapped" and b == "wrapped":
            clear_set = {first, second}
            clear_set.update(
                c for c in self.candies
                if abs(c.row - first.row) <= 2
                and abs(c.col - first.col) <= 2
            )
            return clear_set

        # Wrapped + Striped -> large cross
        if (a == "wrapped" and b_is_striped) or (
            b == "wrapped" and a_is_striped
        ):
            clear_set = {first, second}
            clear_set.update(
                c for c in self.candies
                if abs(c.row - first.row) <= 1
                or abs(c.col - first.col) <= 1
            )
            return clear_set

        # Special + normal -> activate the special.
        special = first if a else second
        normal = second if special is first else first
        clear_set = {special, normal}

        if getattr(special, "special_type", None) == "striped_h":
            clear_set.update(c for c in self.candies if c.row == special.row)
        elif getattr(special, "special_type", None) == "striped_v":
            clear_set.update(c for c in self.candies if c.col == special.col)
        elif getattr(special, "special_type", None) == "wrapped":
            clear_set.update(
                c for c in self.candies
                if abs(c.row - special.row) <= 1
                and abs(c.col - special.col) <= 1
            )

        return clear_set

    # =====================================================
    # SWAP / MOVE LOGIC
    # =====================================================

    def swap_candies(self, candy1, candy2):
        candy1.row, candy2.row = candy2.row, candy1.row
        candy1.col, candy2.col = candy2.col, candy1.col
        self.update_candy_positions()

    def handle_game_click(self, mouse_x, mouse_y):
        self.last_action_time = pygame.time.get_ticks()
        self.hint_candies = None

        # Level completion must be checked BEFORE game_over. In some cases
        # the final move can also make moves reach zero, and the completion
        # screen should still receive the NEXT LEVEL click.
        if self.level_complete:
            button = self.get_level_complete_button()
            if button.collidepoint(mouse_x, mouse_y):
                self.next_level()
            return

        if self.game_over:
            if hasattr(self, "restart_button") and self.restart_button.collidepoint(mouse_x, mouse_y):
                self.restart_game()
            return

        if self.match_animation or self.moves <= 0:
            return

        clicked = None
        for candy in self.candies:
            rect = pygame.Rect(
                int(candy.x), int(candy.y),
                self.cell_size, self.cell_size
            )
            if rect.collidepoint(mouse_x, mouse_y):
                clicked = candy
                break

        if clicked is None:
            return

        if self.selected_candy is None:
            self.selected_candy = clicked
            return

        first = self.selected_candy
        second = clicked

        if first is second:
            self.selected_candy = None
            return

        if abs(first.row - second.row) + abs(first.col - second.col) != 1:
            self.selected_candy = clicked
            return

        self.selected_candy = None
        self.play_sound(self.swap_sound)
        self.swap_candies(first, second)

        # Special swaps do not need a normal 3-match.
        special_clear = self.special_swap_effect(first, second)
        if special_clear is not None:
            self.moves -= 1
            self.expand_special_effects(special_clear)
            self.start_match(special_clear, 15)
            return

        matches = self.find_matches()
        groups = self.find_match_groups()

        if not matches:
            # Real Candy Crush behavior: invalid swap is reversed and costs no move.
            self.swap_candies(first, second)
            return

        self.moves -= 1

        # Create the special from the COMPLETE group produced by this move.
        chosen_special = None
        chosen_position = None

        for group in groups:
            if first in group["candies"] or second in group["candies"]:
                preferred = first if first in group["candies"] else second
                chosen_special, chosen_position = self.get_special_for_group(
                    group, preferred
                )
                if chosen_special:
                    break

        if chosen_special:
            chosen_position.special_type = chosen_special
            if chosen_special.startswith("striped"):
                self.striped_created += 1
            elif chosen_special == "color_bomb":
                self.color_bombs_created += 1
            matches.discard(chosen_position)

        self.expand_special_effects(matches)

        bonus = 50 if chosen_special else 0
        self.start_match(matches, 10, bonus)

    def start_match(self, matches, points_per_candy=10, bonus=0):
        if not matches:
            return

        for candy in matches:
            self.fruit_collected[candy.type] = self.fruit_collected.get(candy.type, 0) + 1
            if (candy.row, candy.col) in self.ice_positions:
                self.ice_positions.remove((candy.row, candy.col))
                self.ice_cleared += 1

        gained = len(matches) * points_per_candy + bonus
        self.level_score += gained
        self.score = self.level_score
        self.update_best_score()

        self.score_popup = gained
        self.score_popup_start = pygame.time.get_ticks()
        self.matched_candies = set(matches)
        self.match_animation = True
        self.animation_start = pygame.time.get_ticks()
        self.play_sound(self.pop_sound)

    # =====================================================
    # GRAVITY / REFILL
    # =====================================================

    def apply_gravity(self):
        for col in range(self.cols):
            column = sorted(
                [c for c in self.candies if c.col == col],
                key=lambda c: c.row,
                reverse=True
            )

            for index, candy in enumerate(column):
                candy.row = self.rows - 1 - index

    def fill_empty_spaces(self):
        occupied = {(c.row, c.col) for c in self.candies}

        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in occupied:
                    self.candies.append(self.new_candy(row, col))

    # =====================================================
    # FINISH MATCH / CASCADES
    # =====================================================

    def finish_match(self):
        for candy in list(self.matched_candies):
            if candy in self.candies:
                self.candies.remove(candy)

        self.play_sound(self.splash_sound)
        self.apply_gravity()
        self.fill_empty_spaces()
        self.update_candy_positions()

        self.matched_candies = set()
        self.match_animation = False

        # Automatic cascades do not use moves.
        matches = self.find_matches()
        if matches:
            groups = self.find_match_groups()
            special = None
            position = None

            for group in groups:
                special, position = self.get_special_for_group(group)
                if special:
                    break

            if special and position:
                position.special_type = special
                if special.startswith("striped"):
                    self.striped_created += 1
                elif special == "color_bomb":
                    self.color_bombs_created += 1
                matches.discard(position)

            self.expand_special_effects(matches)
            self.start_match(matches, 10, 50 if special else 0)
            return

        # Candy Crush shuffles only when NO legal move remains.
        if self.moves > 0 and not self.has_possible_move():
            self.shuffle_board()

        self.check_level_state()

        if self.level_failed:
            self.update_best_score()
            self.play_sound(self.gameover_sound)

    def update_animation(self):
        if not self.match_animation:
            return

        elapsed = pygame.time.get_ticks() - self.animation_start
        if elapsed >= self.MATCH_DURATION:
            self.finish_match()

    # =====================================================
    # POSSIBLE MOVES / SHUFFLE
    # =====================================================

    def build_type_grid(self):
        grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        for candy in self.candies:
            grid[candy.row][candy.col] = candy.type

        return grid

    def grid_has_match(self, grid):
        # Horizontal
        for row in range(self.rows):
            for col in range(self.cols - 2):
                value = grid[row][col]
                if value is not None and value == grid[row][col + 1] == grid[row][col + 2]:
                    return True

        # Vertical
        for row in range(self.rows - 2):
            for col in range(self.cols):
                value = grid[row][col]
                if value is not None and value == grid[row + 1][col] == grid[row + 2][col]:
                    return True

        return False

    def count_possible_moves(self):
        # Fast board-level check. This avoids swapping Candy objects and
        # repeatedly scanning the whole object list.
        grid = self.build_type_grid()
        count = 0

        for row in range(self.rows):
            for col in range(self.cols):
                # Right
                if col + 1 < self.cols:
                    grid[row][col], grid[row][col + 1] = (
                        grid[row][col + 1],
                        grid[row][col]
                    )

                    if self.grid_has_match(grid):
                        count += 1

                    grid[row][col], grid[row][col + 1] = (
                        grid[row][col + 1],
                        grid[row][col]
                    )

                # Down
                if row + 1 < self.rows:
                    grid[row][col], grid[row + 1][col] = (
                        grid[row + 1][col],
                        grid[row][col]
                    )

                    if self.grid_has_match(grid):
                        count += 1

                    grid[row][col], grid[row + 1][col] = (
                        grid[row + 1][col],
                        grid[row][col]
                    )

        return count

    def find_hint(self):
        # Find one legal normal swap for the player.
        grid = self.build_type_grid()

        for row in range(self.rows):
            for col in range(self.cols):
                first = self.candy_at(row, col)

                if first is None:
                    continue

                for dr, dc in ((0, 1), (1, 0)):
                    nr = row + dr
                    nc = col + dc

                    if nr >= self.rows or nc >= self.cols:
                        continue

                    second = self.candy_at(nr, nc)

                    if second is None:
                        continue

                    grid[row][col], grid[nr][nc] = (
                        grid[nr][nc],
                        grid[row][col]
                    )

                    possible = self.grid_has_match(grid)

                    grid[row][col], grid[nr][nc] = (
                        grid[nr][nc],
                        grid[row][col]
                    )

                    if possible:
                        return first, second

        return None

    def update_hint(self):
        if self.match_animation or self.game_over or self.moves <= 0:
            self.hint_candies = None
            return

        now = pygame.time.get_ticks()

        if now - self.last_action_time >= self.HINT_DELAY:
            if self.hint_candies is None:
                self.hint_candies = self.find_hint()

        else:
            self.hint_candies = None

    def has_possible_move(self):
        return self.count_possible_moves() > 0

    def shuffle_board(self):
        # Keep the fruit collection but rearrange it until the board is
        # playable and has no immediate matches.
        saved_types = [c.type for c in self.candies]

        for _ in range(300):
            random.shuffle(saved_types)

            for candy, fruit_type in zip(self.candies, saved_types):
                candy.type = fruit_type
                candy.special_type = None

            if not self.find_matches() and self.has_possible_move():
                self.update_candy_positions()
                self.shuffle_message_until = pygame.time.get_ticks() + 1200
                self.hint_candies = None
                self.last_action_time = pygame.time.get_ticks()
                return

        # Safe fallback.
        self.create_board()
        self.shuffle_message_until = pygame.time.get_ticks() + 1200

    # =====================================================
    # DRAW START SCREEN
    # =====================================================

    def draw_start_screen(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.LIGHT_PINK)

        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((255, 240, 245, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("Fruity Match", True, self.DARK_PINK)
        self.screen.blit(
            title,
            (
                self.screen_width // 2 - title.get_width() // 2,
                self.screen_height // 2 - 155
            )
        )

        subtitle = self.subtitle_font.render(
            "MATCH  •  SPLASH  •  WIN", True, self.BROWN
        )
        self.screen.blit(
            subtitle,
            (
                self.screen_width // 2 - subtitle.get_width() // 2,
                self.screen_height // 2 - 75
            )
        )

        pygame.draw.rect(
            self.screen, self.PINK, self.play_button, border_radius=35
        )
        pygame.draw.rect(
            self.screen, self.WHITE, self.play_button, 4, border_radius=35
        )

        play_text = self.button_font.render("PLAY", True, self.WHITE)
        triangle_size = 17
        triangle_x = self.play_button.centerx - play_text.get_width() // 2 - 35
        triangle_y = self.play_button.centery
        pygame.draw.polygon(
            self.screen,
            self.WHITE,
            [
                (triangle_x, triangle_y - triangle_size),
                (triangle_x, triangle_y + triangle_size),
                (triangle_x + triangle_size, triangle_y)
            ]
        )
        self.screen.blit(
            play_text,
            (
                self.play_button.centerx - play_text.get_width() // 2 + 15,
                self.play_button.centery - play_text.get_height() // 2
            )
        )

        # Small 10-level map preview. Locked levels use the uploaded lock icon.
        map_title = self.small_font.render("LEVEL MAP", True, self.BROWN)
        self.screen.blit(
            map_title,
            (self.screen_width // 2 - map_title.get_width() // 2,
             self.play_button.bottom + 75)
        )

        for index in range(len(self.levels)):
            x = self.screen_width // 2 - 135 + (index % 5) * 68
            y = self.play_button.bottom + 110 + (index // 5) * 55
            if index + 1 <= self.level:
                pygame.draw.circle(self.screen, self.PINK, (x, y), 19)
                number = self.small_font.render(str(index + 1), True, self.WHITE)
                self.screen.blit(number, (x - number.get_width() // 2, y - number.get_height() // 2))
            elif self.lock_image:
                lock = pygame.transform.smoothscale(self.lock_image, (34, 34))
                self.screen.blit(lock, (x - 17, y - 17))
            else:
                pygame.draw.circle(self.screen, self.SHADOW, (x, y), 16)

        best = self.score_font.render(
            f"BEST SCORE: {self.best_score}", True, self.BROWN
        )
        self.screen.blit(
            best,
            (
                self.screen_width // 2 - best.get_width() // 2,
                self.play_button.bottom + 225
            )
        )

        pygame.display.flip()

    # =====================================================
    # HEADER
    # =====================================================

    def draw_header(self):
        header_height = 105

        pygame.draw.rect(
            self.screen, self.SHADOW,
            (0, 5, self.screen_width, header_height)
        )
        pygame.draw.rect(
            self.screen, self.PINK,
            (0, 0, self.screen_width, header_height)
        )

        margin = 15
        gap = 10
        usable = self.screen_width - margin * 2 - gap * 2
        box_width = min(330, usable // 3)

        boxes = [
            ("SCORE", str(self.score), self.PEACH),
            ("MOVES", str(self.moves), self.MINT),
            ("BEST", str(self.best_score), self.LAVENDER)
        ]

        for index, (label, value, color) in enumerate(boxes):
            x = margin + index * (box_width + gap)
            rect = pygame.Rect(x, 16, box_width, 73)

            pygame.draw.rect(
                self.screen, self.SHADOW,
                (rect.x, rect.y + 4, rect.width, rect.height),
                border_radius=20
            )
            pygame.draw.rect(
                self.screen, color, rect, border_radius=20
            )
            pygame.draw.rect(
                self.screen, self.WHITE, rect, 2, border_radius=20
            )

            label_surface = self.small_font.render(label, True, self.BROWN)
            value_surface = self.header_font.render(value, True, self.DARK_PINK)

            self.screen.blit(
                label_surface,
                (rect.centerx - label_surface.get_width() // 2, rect.y + 8)
            )
            self.screen.blit(
                value_surface,
                (rect.centerx - value_surface.get_width() // 2, rect.y + 31)
            )

    # =====================================================
    # BOARD DRAWING
    # =====================================================

    def draw_level_info(self):
        data=self.current_level_data()
        progress,text_value=self.objective_progress()
        label=self.small_font.render(f"LEVEL {self.level}  •  {data['objective']}",True,self.BROWN)
        self.screen.blit(label,(self.screen_width//2-label.get_width()//2,108))
        bar_width=min(620,self.screen_width-80); bar_x=(self.screen_width-bar_width)//2
        pygame.draw.rect(self.screen,self.WHITE,(bar_x,132,bar_width,12),border_radius=6)
        pygame.draw.rect(self.screen,self.PINK,(bar_x,132,int(bar_width*progress),12),border_radius=6)
        value=self.small_font.render(text_value,True,self.BROWN)
        self.screen.blit(value,(self.screen_width//2-value.get_width()//2,147))

        if data.get("showcase"):
            tip=self.small_font.render("SPECIALS: STRIPED  •  WRAPPED  •  COLOR BOMB  •  COMBOS",True,self.DARK_PINK)
            self.screen.blit(tip,(self.screen_width//2-tip.get_width()//2,166))

    def draw_special(self, candy):
        special = getattr(candy, "special_type", None)
        if not special:
            return

        cx = int(candy.x + self.cell_size / 2)
        cy = int(candy.y + self.cell_size / 2)
        radius = max(7, int(self.cell_size * 0.30))

        if special == "striped_h":
            pygame.draw.line(
                self.screen, self.WHITE,
                (int(candy.x + 8), cy),
                (int(candy.x + self.cell_size - 8), cy),
                max(4, self.cell_size // 12)
            )
            pygame.draw.line(
                self.screen, self.DARK_PINK,
                (int(candy.x + 8), cy + 8),
                (int(candy.x + self.cell_size - 8), cy + 8),
                2
            )

        elif special == "striped_v":
            pygame.draw.line(
                self.screen, self.WHITE,
                (cx, int(candy.y + 8)),
                (cx, int(candy.y + self.cell_size - 8)),
                max(4, self.cell_size // 12)
            )
            pygame.draw.line(
                self.screen, self.DARK_PINK,
                (cx + 8, int(candy.y + 8)),
                (cx + 8, int(candy.y + self.cell_size - 8)),
                2
            )

        elif special == "wrapped":
            pygame.draw.circle(self.screen, self.WHITE, (cx, cy), radius, 3)
            pygame.draw.circle(self.screen, self.YELLOW, (cx, cy), max(4, radius // 2), 3)

        elif special == "color_bomb":
            if self.bomb_image:
                size=max(25,int(self.cell_size*0.78))
                image=pygame.transform.smoothscale(self.bomb_image,(size,size))
                self.screen.blit(image,(cx-size//2,cy-size//2))
            else:
                pygame.draw.circle(self.screen,self.BROWN,(cx,cy),radius)

    def draw_board(self):
        shadow_rect = pygame.Rect(
            self.board_x - 16, self.board_y - 16,
            self.board_width + 32, self.board_height + 32
        )
        pygame.draw.rect(
            self.screen, self.SHADOW, shadow_rect, border_radius=32
        )

        outer_rect = pygame.Rect(
            self.board_x - 13, self.board_y - 13,
            self.board_width + 26, self.board_height + 26
        )
        pygame.draw.rect(
            self.screen, self.PINK, outer_rect, border_radius=30
        )

        inner_rect = pygame.Rect(
            self.board_x - 6, self.board_y - 6,
            self.board_width + 12, self.board_height + 12
        )
        pygame.draw.rect(
            self.screen, self.CREAM, inner_rect, border_radius=25
        )
        pygame.draw.rect(
            self.screen, self.WHITE, inner_rect, 3, border_radius=25
        )

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
                x = self.board_x + col * self.cell_size
                y = self.board_y + row * self.cell_size
                cell_rect = pygame.Rect(
                    int(x + 3), int(y + 3),
                    self.cell_size - 6, self.cell_size - 6
                )
                color = pastel_cells[(row + col) % len(pastel_cells)]

                shadow = pygame.Rect(
                    int(x + 5), int(y + 6),
                    self.cell_size - 8, self.cell_size - 8
                )
                pygame.draw.rect(
                    self.screen, self.SHADOW, shadow, border_radius=16
                )
                pygame.draw.rect(
                    self.screen, color, cell_rect, border_radius=16
                )
                pygame.draw.rect(
                    self.screen, self.WHITE, cell_rect, 2, border_radius=16
                )

        for candy in self.candies:
            candy.draw(self.screen)
            self.draw_special(candy)

        if self.ice_image:
            # Ice is a translucent overlay, not an opaque cover.
            # The fruit underneath must remain clearly visible so the
            # player can see and match it while breaking the ice.
            ice_size = max(20, int(self.cell_size * 0.82))
            ice_scaled = pygame.transform.smoothscale(
                self.ice_image, (ice_size, ice_size)
            ).copy()
            ice_scaled.set_alpha(105)

            for row, col in self.ice_positions:
                x = int(
                    self.board_x
                    + col * self.cell_size
                    + (self.cell_size - ice_size) / 2
                )
                y = int(
                    self.board_y
                    + row * self.cell_size
                    + (self.cell_size - ice_size) / 2
                )
                self.screen.blit(ice_scaled, (x, y))

                # Small white outline makes the iced cell easy to identify
                # without hiding the fruit.
                outline = pygame.Rect(
                    int(self.board_x + col * self.cell_size + 5),
                    int(self.board_y + row * self.cell_size + 5),
                    self.cell_size - 10,
                    self.cell_size - 10
                )
                pygame.draw.rect(
                    self.screen, self.WHITE, outline, 2, border_radius=14
                )

        # Match flash
        if self.match_animation:
            elapsed = pygame.time.get_ticks() - self.animation_start
            progress = min(elapsed / self.MATCH_DURATION, 1)

            for candy in self.matched_candies:
                if candy not in self.candies:
                    continue

                rect = pygame.Rect(
                    int(candy.x + 4), int(candy.y + 4),
                    self.cell_size - 8, self.cell_size - 8
                )
                pygame.draw.rect(
                    self.screen, self.WHITE, rect, 4, border_radius=16
                )
                pygame.draw.circle(
                    self.screen,
                    self.WHITE,
                    (int(candy.x + self.cell_size / 2), int(candy.y + self.cell_size / 2)),
                    int(8 + progress * 25),
                    3
                )

            # Striped candies use a real Candy Crush-style beam, not a
            # circular/ripple animation. Horizontal striped candy clears the
            # entire row; vertical striped candy clears the entire column.
            beam_width = max(3, int(5 + 8 * progress))
            beam_alpha = max(40, 255 - int(progress * 180))
            beam_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

            for candy in self.matched_candies:
                special = getattr(candy, "special_type", None)
                if special == "striped_h" and candy in self.candies:
                    y = int(candy.y + self.cell_size / 2)
                    pygame.draw.rect(
                        beam_surface, (255, 255, 255, beam_alpha),
                        (self.board_x - 10, y - beam_width // 2,
                         self.board_width + 20, beam_width),
                        border_radius=beam_width
                    )
                    pygame.draw.line(
                        beam_surface, (255, 182, 203, min(255, beam_alpha + 20)),
                        (self.board_x - 10, y),
                        (self.board_x + self.board_width + 10, y),
                        max(2, beam_width // 2)
                    )

                elif special == "striped_v" and candy in self.candies:
                    x = int(candy.x + self.cell_size / 2)
                    pygame.draw.rect(
                        beam_surface, (255, 255, 255, beam_alpha),
                        (x - beam_width // 2, self.board_y - 10,
                         beam_width, self.board_height + 20),
                        border_radius=beam_width
                    )
                    pygame.draw.line(
                        beam_surface, (255, 182, 203, min(255, beam_alpha + 20)),
                        (x, self.board_y - 10),
                        (x, self.board_y + self.board_height + 10),
                        max(2, beam_width // 2)
                    )

            self.screen.blit(beam_surface, (0, 0))

        if self.selected_candy:
            rect = pygame.Rect(
                int(self.selected_candy.x + 2),
                int(self.selected_candy.y + 2),
                self.cell_size - 4,
                self.cell_size - 4
            )
            pygame.draw.rect(
                self.screen, self.DARK_PINK, rect, 4, border_radius=18
            )

    # =====================================================
    # SCORE / GAME OVER
    # =====================================================

    def draw_hint(self):
        if not self.hint_candies:
            return

        now = pygame.time.get_ticks()
        pulse = 3 + int(3 * abs((now % 600) - 300) / 300)

        for candy in self.hint_candies:
            rect = pygame.Rect(
                int(candy.x) + 3,
                int(candy.y) + 3,
                self.cell_size - 6,
                self.cell_size - 6
            )

            pygame.draw.rect(
                self.screen,
                self.WHITE,
                rect,
                4 + pulse,
                border_radius=12
            )

    def draw_score_popup(self):
        if self.score_popup <= 0:
            return

        elapsed = pygame.time.get_ticks() - self.score_popup_start
        if elapsed > 1000:
            return

        alpha = max(0, 255 - int(elapsed / 1000 * 255))
        text = self.score_font.render(
            f"+{self.score_popup}", True, self.DARK_PINK
        )
        text.set_alpha(alpha)

        y = self.board_y - 30 - int(elapsed / 20)
        self.screen.blit(
            text,
            (self.screen_width // 2 - text.get_width() // 2, y)
        )

    def draw_shuffle_message(self):
        if pygame.time.get_ticks() >= self.shuffle_message_until:
            return

        box = pygame.Rect(
            self.screen_width // 2 - 150,
            self.screen_height // 2 - 35,
            300,
            70
        )
        pygame.draw.rect(
            self.screen, self.PINK, box, border_radius=25
        )
        pygame.draw.rect(
            self.screen, self.WHITE, box, 3, border_radius=25
        )
        text = self.button_font.render("SHUFFLE!", True, self.WHITE)
        self.screen.blit(
            text,
            (box.centerx - text.get_width() // 2,
             box.centery - text.get_height() // 2)
        )

    def get_level_complete_button(self):
        """Return the same NEXT LEVEL button rectangle used for drawing and clicking."""
        panel=pygame.Rect(
            self.screen_width//2-250,
            self.screen_height//2-220,
            500,
            440
        )
        return pygame.Rect(panel.centerx-135, panel.y+285, 270, 65)

    def draw_game_over(self):
        if not (self.game_over or self.level_complete): return
        overlay=pygame.Surface((self.screen_width,self.screen_height),pygame.SRCALPHA)
        overlay.fill((255,240,245,180)); self.screen.blit(overlay,(0,0))
        panel=pygame.Rect(self.screen_width//2-250,self.screen_height//2-220,500,440)
        pygame.draw.rect(self.screen,self.CREAM,panel,border_radius=35)
        pygame.draw.rect(self.screen,self.PINK,panel,5,border_radius=35)
        if self.level_complete:
            title=self.gameover_font.render("LEVEL COMPLETE!",True,self.DARK_PINK)
            self.screen.blit(title,(panel.centerx-title.get_width()//2,panel.y+35))
            info=self.score_font.render(f"LEVEL {self.level}  •  SCORE {self.level_score}",True,self.BROWN)
            self.screen.blit(info,(panel.centerx-info.get_width()//2,panel.y+105))
            for i in range(3):
                x=panel.centerx-87+i*87; y=panel.y+180
                if i < self.level_stars and self.star_image:
                    star=pygame.transform.smoothscale(self.star_image,(58,58)); self.screen.blit(star,(x-29,y-29))
                else: pygame.draw.circle(self.screen,self.SHADOW,(x,y),22,4)
            button=self.get_level_complete_button()
            pygame.draw.rect(self.screen,self.PINK,button,border_radius=28); pygame.draw.rect(self.screen,self.WHITE,button,3,border_radius=28)
            text=self.button_font.render("FINISH" if self.level>=len(self.levels) else "NEXT LEVEL",True,self.WHITE)
            self.screen.blit(text,(button.centerx-text.get_width()//2,button.centery-text.get_height()//2)); self.level_complete_button=button
        else:
            title=self.gameover_font.render("LEVEL FAILED",True,self.DARK_PINK)
            self.screen.blit(title,(panel.centerx-title.get_width()//2,panel.y+55))
            score=self.score_font.render(f"SCORE: {self.level_score}",True,self.BROWN)
            self.screen.blit(score,(panel.centerx-score.get_width()//2,panel.y+135))
            obj=self.small_font.render(self.current_level_data()["objective"],True,self.BROWN)
            self.screen.blit(obj,(panel.centerx-obj.get_width()//2,panel.y+180))
            button=pygame.Rect(panel.centerx-125,panel.y+250,250,65)
            pygame.draw.rect(self.screen,self.PINK,button,border_radius=28)
            text=self.button_font.render("TRY AGAIN",True,self.WHITE)
            self.screen.blit(text,(button.centerx-text.get_width()//2,button.centery-text.get_height()//2)); self.restart_button=button

    # =====================================================
    # GAME CONTROL
    # =====================================================

    def restart_game(self):
        self.setup_level()
        self.state="game"

    def draw_game(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.LIGHT_PINK)

        self.draw_header()
        self.draw_level_info()
        self.draw_board()
        self.draw_hint()
        self.draw_score_popup()
        self.draw_shuffle_message()
        self.draw_game_over()
        pygame.display.flip()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.screen = pygame.display.set_mode(
                        (self.screen_width, self.screen_height),
                        pygame.RESIZABLE
                    )
                    self.update_board_dimensions()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos

                    if self.state == "start":
                        if self.play_button.collidepoint(mouse_x, mouse_y):
                            self.play_sound(self.swap_sound)
                            self.state = "game"
                            self.level = 1
                            self.setup_level()

                    elif self.state == "game":
                        self.handle_game_click(mouse_x, mouse_y)

            if self.state == "game":
                self.update_animation()
                self.update_hint()

            if self.state == "start":
                self.draw_start_screen()
            else:
                self.draw_game()

            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = FruitMatchGame()
    game.run()
