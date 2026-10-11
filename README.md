# Fruity Match

### Match • Splash • Win!

## About the Game

Fruity Match is a fruit-matching puzzle game developed using Python and Pygame. Players match identical fruits on an 8×8 game board to earn points and achieve a high score within a limited number of moves.

The game features colourful fruit graphics, sound effects, special elements, and an interactive interface to make the gameplay engaging.

## Features

* **8×8 Game Board:** Play on a grid filled with different fruits.
* **Fruit Matching:** Match identical fruits to score points.
* **Limited Moves:** Complete matches strategically within 20 moves.
* **Scoring System:** Earn points by making successful matches.
* **Special Elements:** Includes special items and obstacles that add variety to the gameplay.
* **Sound Effects:** Audio feedback for different game actions.
* **Score Tracking:** Save and track the best score.
* **Interactive Interface:** Includes a menu, gameplay screen, and game-over screen.

## Technologies Used

* **Python:** Core programming language.
* **Pygame:** Game development, graphics, events, and audio.
* **Object-Oriented Programming:** Organizes game components into separate modules.
* **Git and GitHub:** Version control and project hosting.

## Project Structure

```text
candycrush/
├── main.py
├── settings.py
├── best_score.txt
├── README.md
│
├── assets/
│   ├── apple.png
│   ├── cherry.png
│   ├── grape.png
│   ├── lemon.png
│   ├── orange.png
│   ├── pineapple.png
│   ├── strawberry.png
│   ├── watermelon.png
│   ├── fruity_background.png
│   ├── font.ttf
│   └── sound effects and other images
│
├── game/
│   ├── board.py
│   ├── candy.py
│   ├── game.py
│   ├── level.py
│   ├── matching.py
│   ├── obstacles.py
│   └── special.py
│
└── screens/
    ├── menu.py
    ├── game_screen.py
    ├── game_over.py
    └── level_complete.py
```

## Installation and Setup

### Prerequisites

* Python 3.10 or a compatible version.
* pip package manager.

### Step 1: Install Pygame

Open a terminal in the project folder and run:

```bash
python -m pip install pygame
```

### Step 2: Run the Game

Execute:

```bash
python main.py
```

The game window will open, allowing you to start playing.

## How to Play

1. Launch the game using `main.py`.
2. Start the game from the menu.
3. Select fruits on the board and swap adjacent fruits to create matches.
4. Match identical fruits to earn points.
5. Use your moves carefully to achieve a higher score.
6. Try to beat your best score before running out of moves.

*Note: The exact matching rules and special-item effects depend on the implemented game logic.*

## Learning Outcomes

Through this project, I gained practical experience in:

* Developing a 2D game using Python and Pygame.
* Designing a grid-based game board.
* Implementing matching logic and score calculation.
* Organizing code into reusable modules.
* Working with images, fonts, and sound effects.
* Managing game states and user interactions.
* Debugging and testing game functionality.
* Using Git and GitHub to manage source code.

## Future Enhancements

* Add more levels with increasing difficulty.
* Introduce new fruit types and special combinations.
* Add animations and visual effects for matches.
* Include a leaderboard and additional scoring challenges.
* Improve the interface and add more gameplay options.

## Conclusion

Fruity Match combines puzzle-solving, game logic, graphics, and audio into an interactive fruit-matching experience. The project demonstrates the practical application of Python and Pygame while providing valuable experience in game development, modular programming, and debugging.

**Match the fruits, maximize your score, and enjoy the game!**

Made by: Megha Guleria
