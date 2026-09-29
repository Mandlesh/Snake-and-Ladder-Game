"""
Tkinter GUI for Snake and Ladder Game.
Features animated dice, smooth token movement, real ladder/snake rendering,
multiplayer setup, AI bots, sound effects, and confetti win celebration.
"""

from __future__ import annotations
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple, Optional

from game.engine import (
    Board,
    Player,
    PlayerType,
    SnakeLadderGame,
    MoveResult,
    DEFAULT_SNAKES,
    DEFAULT_LADDERS,
)
from game.sound import SoundManager


# Colors and theme
BG_MAIN = "#F1F5F9"
PANEL_BG = "#FFFFFF"
BORDER_COLOR = "#CBD5E1"
TEXT_MAIN = "#0F172A"
TEXT_MUTED = "#64748B"
PRIMARY_COLOR = "#3B82F6"
PRIMARY_HOVER = "#2563EB"
SUCCESS_COLOR = "#10B981"
DANGER_COLOR = "#EF4444"

TILE_LIGHT = "#FFFFFF"
TILE_ALT = "#F8FAFC"
TILE_START = "#ECFDF5"
TILE_END = "#FEF3C7"

LADDER_COLOR = "#D97706"
LADDER_RAIL_COLOR = "#92400E"
SNAKE_BODY_COLOR = "#DC2626"
SNAKE_SPOTS_COLOR = "#FBBF24"
SNAKE_HEAD_COLOR = "#B91C1C"

PLAYER_PALETTE = [
    {"name": "Red", "hex": "#EF4444", "border": "#991B1B"},
    {"name": "Blue", "hex": "#3B82F6", "border": "#1E40AF"},
    {"name": "Green", "hex": "#10B981", "border": "#065F46"},
    {"name": "Purple", "hex": "#8B5CF6", "border": "#5B21B6"},
]


class ConfettiParticle:
    """Particle for victory celebration."""
    def __init__(self, canvas_width: int, canvas_height: int):
        self.x = random.uniform(50, canvas_width - 50)
        self.y = random.uniform(-50, 0)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(2, 6)
        self.size = random.uniform(5, 10)
        self.color = random.choice([
            "#EF4444", "#3B82F6", "#10B981", "#F59E0B",
            "#8B5CF6", "#EC4899", "#06B6D4"
        ])
        self.tilt = random.uniform(0, 360)
        self.tilt_speed = random.uniform(-10, 10)


class SnakeLadderGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Snake & Ladder - Python Edition")
        self.root.geometry("1060x740")
        self.root.minsize(980, 700)
        self.root.configure(bg=BG_MAIN)

        self.cell_size = 64
        self.canvas_size = self.cell_size * 10  # 640 x 640

        self.sound = SoundManager(enabled=True)
        self.sound_enabled_var = tk.BooleanVar(value=True)

        # Initialize Default Players
        self.players: List[Player] = [
            Player(id=1, name="Player 1", color=PLAYER_PALETTE[0]["hex"], player_type=PlayerType.HUMAN),
            Player(id=2, name="Computer Bot", color=PLAYER_PALETTE[1]["hex"], player_type=PlayerType.BOT),
        ]
        self.game = SnakeLadderGame(players=self.players)

        # Animation states
        self.is_animating = False
        self.confetti_particles: List[ConfettiParticle] = []
        self.confetti_job = None

        self._build_layout()
        self.draw_board()
        self.update_player_tokens()
        self.update_ui_state()

    def _build_layout(self):
        """Builds main frame with board on left and dashboard on right."""
        container = tk.Frame(self.root, bg=BG_MAIN)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Column: Canvas Board
        board_frame = tk.Frame(
            container,
            bg=PANEL_BG,
            highlightbackground=BORDER_COLOR,
            highlightthickness=2,
            bd=0
        )
        board_frame.pack(side=tk.LEFT, padx=(0, 20), pady=0)

        self.canvas = tk.Canvas(
            board_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#FFFFFF",
            highlightthickness=0,
        )
        self.canvas.pack()

        # Right Column: Dashboard
        self.dash_frame = tk.Frame(container, bg=BG_MAIN)
        self.dash_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_header_card()
        self._build_dice_card()
        self._build_players_card()
        self._build_log_card()
        self._build_footer_controls()

    def _build_header_card(self):
        header_card = tk.Frame(self.dash_frame, bg=PANEL_BG, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        header_card.pack(fill=tk.X, pady=(0, 10))

        title = tk.Label(
            header_card,
            text="🐍 Snake & Ladder 🪜",
            font=("Segoe UI", 16, "bold"),
            bg=PANEL_BG,
            fg=TEXT_MAIN,
        )
        title.pack(anchor="w")

        self.turn_status_label = tk.Label(
            header_card,
            text="Alice's Turn",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL_BG,
            fg=PRIMARY_COLOR,
        )
        self.turn_status_label.pack(anchor="w", pady=(4, 0))

    def _build_dice_card(self):
        dice_card = tk.Frame(self.dash_frame, bg=PANEL_BG, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        dice_card.pack(fill=tk.X, pady=(0, 10))

        dice_row = tk.Frame(dice_card, bg=PANEL_BG)
        dice_row.pack(fill=tk.X)

        # Dice Canvas for drawing realistic 3D dice faces
        self.dice_canvas = tk.Canvas(
            dice_row,
            width=70,
            height=70,
            bg=PANEL_BG,
            highlightthickness=0,
        )
        self.dice_canvas.pack(side=tk.LEFT, padx=(0, 16))
        self.draw_dice_face(1)

        info_col = tk.Frame(dice_row, bg=PANEL_BG)
        info_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.roll_btn = tk.Button(
            info_col,
            text="🎲 ROLL DICE",
            font=("Segoe UI", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="#FFFFFF",
            activebackground=PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.on_roll_clicked,
        )
        self.roll_btn.pack(fill=tk.X)

        self.dice_subtext = tk.Label(
            info_col,
            text="Click roll or press Space",
            font=("Segoe UI", 9),
            bg=PANEL_BG,
            fg=TEXT_MUTED,
        )
        self.dice_subtext.pack(anchor="w", pady=(4, 0))

        self.root.bind("<space>", lambda event: self.on_roll_clicked())

    def _build_players_card(self):
        players_card = tk.Frame(self.dash_frame, bg=PANEL_BG, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        players_card.pack(fill=tk.X, pady=(0, 10))

        title = tk.Label(
            players_card,
            text="Players & Positions",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL_BG,
            fg=TEXT_MAIN,
        )
        title.pack(anchor="w", pady=(0, 8))

        self.player_row_frames: Dict[int, Tuple[tk.Frame, tk.Label, tk.Label, tk.Label]] = {}
        self.players_container = tk.Frame(players_card, bg=PANEL_BG)
        self.players_container.pack(fill=tk.X)

        self.refresh_players_list_ui()

    def refresh_players_list_ui(self):
        for widget in self.players_container.winfo_children():
            widget.destroy()

        self.player_row_frames.clear()

        for p in self.game.players:
            p_row = tk.Frame(self.players_container, bg=PANEL_BG, pady=4)
            p_row.pack(fill=tk.X)

            # Color pip indicator
            color_pip = tk.Canvas(p_row, width=16, height=16, bg=PANEL_BG, highlightthickness=0)
            color_pip.pack(side=tk.LEFT, padx=(0, 8))
            color_pip.create_oval(2, 2, 14, 14, fill=p.color, outline="#333333", width=1.5)

            name_lbl = tk.Label(
                p_row,
                text=f"{p.name} ({'Bot' if p.player_type == PlayerType.BOT else 'Human'})",
                font=("Segoe UI", 9, "bold" if p == self.game.current_player else "normal"),
                bg=PANEL_BG,
                fg=TEXT_MAIN,
            )
            name_lbl.pack(side=tk.LEFT)

            pos_badge = tk.Label(
                p_row,
                text=f"Tile {p.position}/100",
                font=("Segoe UI", 9, "bold"),
                bg="#E2E8F0",
                fg=TEXT_MAIN,
                padx=8,
                pady=2,
            )
            pos_badge.pack(side=tk.RIGHT)

            self.player_row_frames[p.id] = (p_row, name_lbl, pos_badge, color_pip)

    def _build_log_card(self):
        log_card = tk.Frame(self.dash_frame, bg=PANEL_BG, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        title = tk.Label(
            log_card,
            text="Game Log",
            font=("Segoe UI", 11, "bold"),
            bg=PANEL_BG,
            fg=TEXT_MAIN,
        )
        title.pack(anchor="w", pady=(0, 6))

        self.log_text = tk.Text(
            log_card,
            font=("Consolas", 9),
            bg="#F8FAFC",
            fg=TEXT_MAIN,
            height=6,
            relief=tk.FLAT,
            state=tk.DISABLED,
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.append_log("Game started! Welcome to Snake & Ladder.")

    def _build_footer_controls(self):
        footer_card = tk.Frame(self.dash_frame, bg=PANEL_BG, padx=16, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        footer_card.pack(fill=tk.X)

        new_game_btn = tk.Button(
            footer_card,
            text="⚙️ Setup / New Game",
            font=("Segoe UI", 9, "bold"),
            bg="#E2E8F0",
            fg=TEXT_MAIN,
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.open_setup_dialog,
        )
        new_game_btn.pack(side=tk.LEFT)

        sound_cb = tk.Checkbutton(
            footer_card,
            text="🔊 Sound",
            variable=self.sound_enabled_var,
            font=("Segoe UI", 9),
            bg=PANEL_BG,
            fg=TEXT_MAIN,
            activebackground=PANEL_BG,
            command=self.on_toggle_sound,
        )
        sound_cb.pack(side=tk.RIGHT)

    def on_toggle_sound(self):
        self.sound.enabled = self.sound_enabled_var.get()

    def append_log(self, text: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "• " + text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # -------------------------------------------------------------
    # Board Canvas Drawing
    # -------------------------------------------------------------
    def get_tile_center(self, tile: int) -> Tuple[float, float]:
        """Calculates center pixel (cx, cy) for a given tile."""
        row, col = self.game.board.tile_to_coords(tile)
        cx = col * self.cell_size + self.cell_size / 2
        cy = row * self.cell_size + self.cell_size / 2
        return cx, cy

    def draw_board(self):
        self.canvas.delete("all")
        board = self.game.board

        # 1. Draw Grid Tiles
        for tile in range(1, board.size + 1):
            row, col = board.tile_to_coords(tile)
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            # Tile color
            if tile == 1:
                fill_color = TILE_START
            elif tile == 100:
                fill_color = TILE_END
            else:
                fill_color = TILE_LIGHT if (row + col) % 2 == 0 else TILE_ALT

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fill_color,
                outline="#E2E8F0",
                width=1,
                tags="board_grid"
            )

            # Tile Number Label
            num_color = TEXT_MUTED if tile not in (1, 100) else PRIMARY_COLOR
            font_spec = ("Segoe UI", 8, "bold" if tile in (1, 100) else "normal")
            self.canvas.create_text(
                x1 + 6, y1 + 6,
                text=str(tile),
                anchor="nw",
                font=font_spec,
                fill=num_color,
                tags="board_grid"
            )

            # Special label icons
            if tile == 1:
                self.canvas.create_text(
                    x1 + self.cell_size / 2, y1 + self.cell_size - 14,
                    text="START",
                    font=("Segoe UI", 8, "bold"),
                    fill=SUCCESS_COLOR,
                    tags="board_grid"
                )
            elif tile == 100:
                self.canvas.create_text(
                    x1 + self.cell_size / 2, y1 + self.cell_size / 2,
                    text="👑 100",
                    font=("Segoe UI", 12, "bold"),
                    fill="#B45309",
                    tags="board_grid"
                )

        # 2. Draw Ladders
        for bottom, top in board.ladders.items():
            self._draw_ladder(bottom, top)

        # 3. Draw Snakes
        for head, tail in board.snakes.items():
            self._draw_snake(head, tail)

    def _draw_ladder(self, bottom_tile: int, top_tile: int):
        """Draws realistic ladder with two vertical rails and horizontal rungs."""
        x1, y1 = self.get_tile_center(bottom_tile)
        x2, y2 = self.get_tile_center(top_tile)

        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return

        # Perpendicular vector for ladder width
        ladder_width = 14
        px = -dy / length * (ladder_width / 2)
        py = dx / length * (ladder_width / 2)

        # Left and Right Rails
        rail1_start = (x1 + px, y1 + py)
        rail1_end = (x2 + px, y2 + py)
        rail2_start = (x1 - px, y1 - py)
        rail2_end = (x2 - px, y2 - py)

        self.canvas.create_line(
            *rail1_start, *rail1_end,
            fill=LADDER_RAIL_COLOR, width=4, capstyle=tk.ROUND, tags="ladder"
        )
        self.canvas.create_line(
            *rail2_start, *rail2_end,
            fill=LADDER_RAIL_COLOR, width=4, capstyle=tk.ROUND, tags="ladder"
        )

        # Rungs along the ladder
        step_dist = 18
        num_rungs = max(3, int(length // step_dist))
        for i in range(1, num_rungs):
            t = i / num_rungs
            rx = x1 + dx * t
            ry = y1 + dy * t
            self.canvas.create_line(
                rx + px, ry + py, rx - px, ry - py,
                fill=LADDER_COLOR, width=3, capstyle=tk.ROUND, tags="ladder"
            )

        # Ladder indicators
        self.canvas.create_oval(
            x1 - 6, y1 - 6, x1 + 6, y1 + 6,
            fill="#FEF3C7", outline=LADDER_RAIL_COLOR, width=1.5, tags="ladder"
        )

    def _draw_snake(self, head_tile: int, tail_tile: int):
        """Draws a serpentine snake with curved wavy body, head, eyes and tongue."""
        hx, hy = self.get_tile_center(head_tile)
        tx, ty = self.get_tile_center(tail_tile)

        dx = tx - hx
        dy = ty - hy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        # Unit vectors
        ux = dx / dist
        uy = dy / dist
        # Normal vectors
        nx = -uy
        ny = ux

        # Generate wavy points along the snake body
        num_segments = 14
        amplitude = 12
        points = []

        for i in range(num_segments + 1):
            t = i / num_segments
            base_x = hx + dx * t
            base_y = hy + dy * t
            # Sine wave oscillation
            offset = math.sin(t * math.pi * 3) * amplitude * (1.0 - t * 0.4)
            px = base_x + nx * offset
            py = base_y + ny * offset
            points.extend([px, py])

        # Smooth spline body
        self.canvas.create_line(
            points,
            smooth=True,
            splinesteps=24,
            fill=SNAKE_BODY_COLOR,
            width=9,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            tags="snake"
        )

        # Striped spots along snake spine
        self.canvas.create_line(
            points,
            smooth=True,
            splinesteps=24,
            fill=SNAKE_SPOTS_COLOR,
            width=3,
            dash=(6, 6),
            tags="snake"
        )

        # Snake Head (Oval)
        head_radius = 11
        self.canvas.create_oval(
            hx - head_radius, hy - head_radius,
            hx + head_radius, hy + head_radius,
            fill=SNAKE_HEAD_COLOR,
            outline="#7F1D1D",
            width=1.5,
            tags="snake"
        )

        # Snake Eyes
        eye_offset = 5
        self.canvas.create_oval(
            hx - eye_offset - 2, hy - eye_offset - 2,
            hx - eye_offset + 2, hy - eye_offset + 2,
            fill="#FFFFFF", outline="#000000", width=0.5, tags="snake"
        )
        self.canvas.create_oval(
            hx + eye_offset - 2, hy - eye_offset - 2,
            hx + eye_offset + 2, hy - eye_offset + 2,
            fill="#FFFFFF", outline="#000000", width=0.5, tags="snake"
        )
        # Eye Pupils
        self.canvas.create_oval(
            hx - eye_offset - 1, hy - eye_offset - 1,
            hx - eye_offset + 1, hy - eye_offset + 1,
            fill="#000000", tags="snake"
        )
        self.canvas.create_oval(
            hx + eye_offset - 1, hy - eye_offset - 1,
            hx + eye_offset + 1, hy - eye_offset + 1,
            fill="#000000", tags="snake"
        )

        # Forked Red Tongue
        tongue_len = 10
        tx_tongue = hx - ux * tongue_len
        ty_tongue = hy - uy * tongue_len
        self.canvas.create_line(
            hx, hy, tx_tongue, ty_tongue,
            fill="#EF4444", width=2, tags="snake"
        )
        self.canvas.create_line(
            tx_tongue, ty_tongue,
            tx_tongue - nx * 3 - ux * 3, ty_tongue - ny * 3 - uy * 3,
            fill="#EF4444", width=1.5, tags="snake"
        )
        self.canvas.create_line(
            tx_tongue, ty_tongue,
            tx_tongue + nx * 3 - ux * 3, ty_tongue + ny * 3 - uy * 3,
            fill="#EF4444", width=1.5, tags="snake"
        )

    # -------------------------------------------------------------
    # Player Token Rendering & Animation
    # -------------------------------------------------------------
    def update_player_tokens(self):
        """Draws all player tokens at their current positions with offsets if overlapping."""
        self.canvas.delete("player_token")

        # Group players by position
        position_groups: Dict[int, List[Player]] = {}
        for p in self.game.players:
            if p.position > 0:
                position_groups.setdefault(p.position, []).append(p)

        # Offsets for up to 4 players on same cell
        offset_map = {
            1: [(0, 0)],
            2: [(-10, 0), (10, 0)],
            3: [(-10, -10), (10, -10), (0, 10)],
            4: [(-10, -10), (10, -10), (-10, 10), (10, 10)],
        }

        radius = 12

        for pos, players in position_groups.items():
            cx, cy = self.get_tile_center(pos)
            offsets = offset_map.get(len(players), [(0, 0)] * len(players))

            for p, (ox, oy) in zip(players, offsets):
                px = cx + ox
                py = cy + oy

                # Shadow
                self.canvas.create_oval(
                    px - radius + 1, py - radius + 2,
                    px + radius + 1, py + radius + 2,
                    fill="#94A3B8", outline="", tags="player_token"
                )
                # Outer circle
                self.canvas.create_oval(
                    px - radius, py - radius,
                    px + radius, py + radius,
                    fill=p.color,
                    outline="#FFFFFF",
                    width=2.5,
                    tags="player_token"
                )
                # Player ID text
                self.canvas.create_text(
                    px, py,
                    text=f"P{p.id}",
                    font=("Segoe UI", 7, "bold"),
                    fill="#FFFFFF",
                    tags="player_token"
                )

    def draw_dice_face(self, value: int):
        """Renders 3D styled dice face with rounded corners and dots."""
        self.dice_canvas.delete("all")
        w = 66
        h = 66
        pad = 3

        # Dice body with subtle border shadow
        self.dice_canvas.create_rectangle(
            pad, pad, w, h,
            fill="#FFFFFF", outline="#CBD5E1", width=2
        )

        pip_coords = {
            1: [(33, 33)],
            2: [(18, 18), (48, 48)],
            3: [(18, 18), (33, 33), (48, 48)],
            4: [(18, 18), (48, 18), (18, 48), (48, 48)],
            5: [(18, 18), (48, 18), (33, 33), (18, 48), (48, 48)],
            6: [(18, 16), (48, 16), (18, 33), (48, 33), (18, 50), (48, 50)],
        }

        pips = pip_coords.get(value, [(33, 33)])
        pip_radius = 5.5
        pip_color = "#E11D48" if value in (1, 6) else "#1E293B"

        for px, py in pips:
            self.dice_canvas.create_oval(
                px - pip_radius, py - pip_radius,
                px + pip_radius, py + pip_radius,
                fill=pip_color, outline="",
            )

    # -------------------------------------------------------------
    # Game Loop & Movement Animation
    # -------------------------------------------------------------
    def on_roll_clicked(self):
        if self.is_animating or self.game.game_over:
            return

        current_player = self.game.current_player
        self.roll_btn.config(state=tk.DISABLED)
        self.is_animating = True

        # Animate dice roll
        self._animate_dice(roll_count=10, final_callback=self._execute_move)

    def _animate_dice(self, roll_count: int, final_callback):
        if roll_count > 0:
            rand_val = random.randint(1, 6)
            self.draw_dice_face(rand_val)
            self.sound.roll_dice()
            self.root.after(45, lambda: self._animate_dice(roll_count - 1, final_callback))
        else:
            final_callback()

    def _execute_move(self):
        result = self.game.play_turn()
        self.draw_dice_face(result.dice_roll)
        self.append_log(result.message)

        if result.turn_skipped or result.overshot or not result.step_positions:
            self.is_animating = False
            self.update_ui_state()
            self.check_bot_turn()
            return

        # Animate step by step
        self._animate_steps(
            player=result.player,
            steps=result.step_positions,
            index=0,
            result=result
        )

    def _animate_steps(self, player: Player, steps: List[int], index: int, result: MoveResult):
        if index < len(steps):
            player.position = steps[index]
            self.sound.step()
            self.update_player_tokens()
            self.update_player_badges()
            self.root.after(140, lambda: self._animate_steps(player, steps, index + 1, result))
        else:
            # Check snake or ladder glide
            if result.is_ladder or result.is_snake:
                self.root.after(300, lambda: self._animate_special_move(player, result))
            else:
                self._finish_turn(result)

    def _animate_special_move(self, player: Player, result: MoveResult):
        player.position = result.final_pos
        self.update_player_tokens()
        self.update_player_badges()

        if result.is_ladder:
            self.sound.ladder()
        elif result.is_snake:
            self.sound.snake()

        self.root.after(400, lambda: self._finish_turn(result))

    def _finish_turn(self, result: MoveResult):
        self.is_animating = False
        self.update_ui_state()

        if result.won:
            self.sound.victory()
            self.start_confetti()
            messagebox.showinfo("Winner!", f"🏆 {result.player.name} has won the match! 🏆")
        else:
            self.check_bot_turn()

    def check_bot_turn(self):
        """If current player is a Bot, schedule automatic roll after 0.8s."""
        if not self.game.game_over and self.game.current_player.player_type == PlayerType.BOT:
            self.dice_subtext.config(text="Bot is thinking...")
            self.root.after(800, self.on_roll_clicked)

    def update_ui_state(self):
        current = self.game.current_player

        if self.game.game_over:
            self.turn_status_label.config(
                text=f"🏆 Winner: {self.game.winner.name}!",
                fg=SUCCESS_COLOR
            )
            self.roll_btn.config(state=tk.DISABLED, text="GAME OVER")
            self.dice_subtext.config(text="Game finished. Click New Game to play again!")
        else:
            bot_tag = " (Bot)" if current.player_type == PlayerType.BOT else ""
            self.turn_status_label.config(
                text=f"Turn: {current.name}{bot_tag}",
                fg=current.color
            )
            can_roll = not self.is_animating and (current.player_type == PlayerType.HUMAN)
            self.roll_btn.config(
                state=tk.NORMAL if can_roll else tk.DISABLED,
                text="🎲 ROLL DICE"
            )
            if current.player_type == PlayerType.HUMAN:
                self.dice_subtext.config(text="Click roll or press Space")
            else:
                self.dice_subtext.config(text="Computer bot will roll automatically...")

        self.update_player_badges()

    def update_player_badges(self):
        for p in self.game.players:
            if p.id in self.player_row_frames:
                _, name_lbl, pos_badge, _ = self.player_row_frames[p.id]
                pos_badge.config(text=f"Tile {p.position}/100")
                is_active = (p == self.game.current_player and not self.game.game_over)
                name_lbl.config(
                    font=("Segoe UI", 9, "bold" if is_active else "normal"),
                    fg=p.color if is_active else TEXT_MAIN
                )

    # -------------------------------------------------------------
    # Victory Celebration Confetti
    # -------------------------------------------------------------
    def start_confetti(self):
        self.confetti_particles = [
            ConfettiParticle(self.canvas_size, self.canvas_size) for _ in range(60)
        ]
        self._animate_confetti()

    def _animate_confetti(self):
        if not self.game.game_over:
            self.canvas.delete("confetti")
            return

        self.canvas.delete("confetti")
        for p in self.confetti_particles:
            p.x += p.vx
            p.y += p.vy
            if p.y > self.canvas_size:
                p.y = -10
                p.x = random.uniform(20, self.canvas_size - 20)

            self.canvas.create_rectangle(
                p.x, p.y, p.x + p.size, p.y + p.size / 2,
                fill=p.color, outline="", tags="confetti"
            )

        self.confetti_job = self.root.after(30, self._animate_confetti)

    def stop_confetti(self):
        if self.confetti_job:
            self.root.after_cancel(self.confetti_job)
            self.confetti_job = None
        self.canvas.delete("confetti")

    # -------------------------------------------------------------
    # Setup Dialog
    # -------------------------------------------------------------
    def open_setup_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Game Setup")
        dialog.geometry("400x380")
        dialog.configure(bg=BG_MAIN)
        dialog.transient(self.root)
        dialog.grab_set()

        content = tk.Frame(dialog, bg=PANEL_BG, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Label(
            content,
            text="Configure Players",
            font=("Segoe UI", 12, "bold"),
            bg=PANEL_BG,
            fg=TEXT_MAIN,
        ).pack(anchor="w", pady=(0, 10))

        # Number of players
        num_frame = tk.Frame(content, bg=PANEL_BG)
        num_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(num_frame, text="Number of Players:", bg=PANEL_BG, fg=TEXT_MAIN).pack(side=tk.LEFT)
        num_var = tk.IntVar(value=len(self.players))
        num_combo = ttk.Combobox(
            num_frame,
            textvariable=num_var,
            values=[2, 3, 4],
            state="readonly",
            width=5
        )
        num_combo.pack(side=tk.RIGHT)

        # Player inputs container
        rows_container = tk.Frame(content, bg=PANEL_BG)
        rows_container.pack(fill=tk.BOTH, expand=True)

        player_entries: List[Tuple[tk.Entry, tk.BooleanVar]] = []

        def rebuild_player_inputs(*args):
            for widget in rows_container.winfo_children():
                widget.destroy()
            player_entries.clear()

            n = num_var.get()
            for i in range(n):
                r = tk.Frame(rows_container, bg=PANEL_BG, pady=3)
                r.pack(fill=tk.X)

                color_sq = tk.Label(r, bg=PLAYER_PALETTE[i]["hex"], width=2)
                color_sq.pack(side=tk.LEFT, padx=(0, 6))

                default_name = f"Player {i+1}" if i == 0 else (f"Bot {i}" if i == 1 else f"Player {i+1}")
                if i < len(self.players):
                    default_name = self.players[i].name

                entry = tk.Entry(r, width=15)
                entry.insert(0, default_name)
                entry.pack(side=tk.LEFT, padx=(0, 10))

                bot_var = tk.BooleanVar(value=(i > 0 and (i == 1 or (i < len(self.players) and self.players[i].player_type == PlayerType.BOT))))
                bot_chk = tk.Checkbutton(
                    r, text="Bot (AI)", variable=bot_var, bg=PANEL_BG, fg=TEXT_MAIN
                )
                bot_chk.pack(side=tk.LEFT)

                player_entries.append((entry, bot_var))

        num_combo.bind("<<ComboboxSelected>>", rebuild_player_inputs)
        rebuild_player_inputs()

        # Start Button
        def apply_and_start():
            new_players: List[Player] = []
            for idx, (entry, bot_var) in enumerate(player_entries):
                name = entry.get().strip() or f"Player {idx+1}"
                ptype = PlayerType.BOT if bot_var.get() else PlayerType.HUMAN
                color = PLAYER_PALETTE[idx]["hex"]
                new_players.append(
                    Player(id=idx + 1, name=name, color=color, player_type=ptype)
                )

            self.stop_confetti()
            self.players = new_players
            self.game = SnakeLadderGame(players=self.players)
            self.refresh_players_list_ui()
            self.update_player_tokens()
            self.update_ui_state()
            self.append_log(f"Started new game with {len(self.players)} players.")
            dialog.destroy()
            self.check_bot_turn()

        btn_row = tk.Frame(content, bg=PANEL_BG)
        btn_row.pack(fill=tk.X, pady=(15, 0))

        start_btn = tk.Button(
            btn_row,
            text="Start New Game",
            font=("Segoe UI", 10, "bold"),
            bg=PRIMARY_COLOR,
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=apply_and_start,
        )
        start_btn.pack(side=tk.RIGHT)


def run_gui():
    root = tk.Tk()
    app = SnakeLadderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
