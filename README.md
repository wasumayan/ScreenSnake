# 🐍 ScreenSnake

A transparent, full-screen Snake game for macOS, written in Python with PyQt5.
Features a tiger-striped player snake, Princeton logo food, and rival AI snakes using Ivy League logos/colors.

## Features

- **Tiger-striped player snake** with animated eyes
- **Princeton logo** as food
- **Rival AI snakes** (Harvard, Yale, MIT, Stanford, Columbia) with greedy logic and college colors/logos
- **AI snakes spawn** every 60 seconds or when one dies
- **Score and high score tracking**
- **Game speed increases** every 5 points (down to a minimum)
- **AI handicap**: If the player is within 2 grids, AI snakes have a 50% chance to freeze (removed after 15 points)
- **Pause on focus loss**, **exit on mouse click**
- **No ML/RL dependencies** (pure greedy AI for performance and compatibility)

## How to Run

1. **Clone the repo:**
   ```sh
   git clone https://github.com/wasumayan/ScreenSnake.git
   cd ScreenSnake
   ```

2. **Set up a Python 3.11+ virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install PyQt5
   ```

4. **Run the game:**
   ```sh
   python screen_snake.py
   ```

## macOS App Distribution

- If you want a standalone `.app` for macOS, use PyInstaller:
  ```sh
  pip install pyinstaller
  pyinstaller --windowed --add-data "*.png:." --add-data "high_scores.json:." --icon screensnake.icns screen_snake.py
  ```
- The `.app` will be in the `dist/` folder.
- **Note:** macOS will warn about unidentified developers. Right-click the app and choose "Open" to bypass.

## Controls

- **Arrow keys**: Move
- **P**: Pause
- **Space**: Restart after game over
- **Esc or Mouse Click**: Quit

## Troubleshooting

- If you see missing images or errors, make sure all `.png` and `.icns` files are present in the same directory as `screen_snake.py`.
- For macOS Gatekeeper issues, see the instructions above.

## Credits

- Princeton, Harvard, Yale, MIT, Stanford, Columbia logos are property of their respective institutions.
- Game by [@wasumayan](https://github.com/wasumayan/ScreenSnake)

---

**Enjoy the game!** 