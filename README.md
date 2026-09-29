# 🐍 Snake and Ladder Game (Python) 🪜

A modern, feature-rich Snake and Ladder game implemented in Python with both a graphical desktop UI (**Tkinter**) and a colorized terminal interface (**CLI**).

---

## 🌟 Features

- **Dual Modes**:
  - **Desktop GUI (`gui.py`)**: Full graphical board with smooth animations, wavy snake bodies with eyes and tongue, realistic ladders, 3D animated dice, confetti win celebration, and live move logs.
  - **Terminal CLI (`cli.py`)**: Colorized 10x10 ASCII board with dice art and match summary statistics.
- **Flexible Multiplayer**:
  - 2 to 4 players.
  - Mix and match **Human** players and **AI Computer Bots**.
- **Authentic Game Rules**:
  - Standard boustrophedon (zigzag) 100-tile board.
  - **Snakes**: 16→6, 47→26, 49→11, 56→53, 62→19, 64→60, 87→24, 93→73, 95→75, 98→78.
  - **Ladders**: 4→14, 9→31, 20→38, 28→84, 40→59, 51→67, 63→81, 71→91.
  - **Extra Turn on 6**: Rolling a 6 earns an extra roll.
  - **Fair Play Rule**: 3 consecutive sixes cancels the turn.
  - **Exact Win Rule**: Player must land exactly on tile 100 to win; overshooting leaves the player in place.
- **Hardware Sound Effects**:
  - Integrated `winsound` audio cues for dice rolls, step movements, ladder climbs, snake bites, and victory fanfares.
  - Mute/unmute toggle in the GUI.
- **Modular Architecture & Unit Tested**:
  - Decoupled `game.engine` pure logic layer.
  - Automated test suite with 100% passing `pytest` tests.

---

## 🚀 How to Run

### 1. Launch Desktop GUI (Recommended)

```bash
python main.py
```
*(Or simply double-click `main.py` in Windows Explorer)*

Controls:
- Click **"🎲 ROLL DICE"** or press <kbd>Space</kbd> to roll.
- Click **"⚙️ Setup / New Game"** to change player names, add/remove players, or toggle AI bots.
- Toggle **"🔊 Sound"** to mute/unmute audio effects.

### 2. Launch Terminal CLI Mode

```bash
python main.py --cli
```
*(Or directly `python cli.py`)*

---

## 📁 Project Structure

```
demo/
├── game/
│   ├── __init__.py      # Package exports
│   ├── engine.py        # Core rules, Board, Player, Dice, Game logic
│   └── sound.py         # Hardware audio player (winsound)
├── gui.py               # Tkinter GUI application
├── cli.py               # Terminal CLI application
├── main.py              # Main launcher script
├── tests/
│   └── test_engine.py   # Pytest unit tests for all mechanics
├── conftest.py          # Pytest path configuration
└── README.md            # Documentation
```

---

## 🧪 Running Unit Tests

Run the test suite with `pytest`:

```bash
pytest
```
