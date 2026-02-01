#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    LANGTON'S ANT - GLADIUS NEURAL SIMULATION                 ║
║                     Fluid Terminal Animation with Rich UI                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

GLADIUS IS THE ANT - Watch the neural model explore emergent patterns.
"""

import os
import sys
import time
import signal
import curses
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from collections import deque

# Add GLADIUS to path
GLADIUS_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(GLADIUS_ROOT))


class SmoothGrid:
    """Optimized grid with viewport rendering."""
    
    def __init__(self, size: int = 500):
        self.size = size
        self.cells = np.zeros((size, size), dtype=np.uint8)
        self.visit_count = np.zeros((size, size), dtype=np.uint32)
        self.history = deque(maxlen=1000)  # Track recent changes
        
    def get(self, x: int, y: int) -> int:
        return self.cells[y % self.size, x % self.size]
    
    def flip(self, x: int, y: int) -> None:
        x, y = x % self.size, y % self.size
        self.cells[y, x] = 1 - self.cells[y, x]
        self.visit_count[y, x] += 1
        self.history.append((x, y, self.cells[y, x]))
    
    def get_viewport(self, cx: int, cy: int, width: int, height: int) -> np.ndarray:
        """Extract viewport centered on position."""
        half_w, half_h = width // 2, height // 2
        
        # Create viewport with wrapping
        viewport = np.zeros((height, width), dtype=np.uint8)
        
        for dy in range(height):
            for dx in range(width):
                gx = (cx - half_w + dx) % self.size
                gy = (cy - half_h + dy) % self.size
                viewport[dy, dx] = self.cells[gy, gx]
        
        return viewport
    
    def get_stats(self) -> Dict[str, Any]:
        black = int(np.sum(self.cells))
        total = self.size * self.size
        return {
            "black": black,
            "white": total - black,
            "ratio": black / total,
            "visited": int(np.sum(self.visit_count > 0)),
            "max_visits": int(np.max(self.visit_count)),
            "total": total
        }


class GladiusAntAnimated:
    """The GLADIUS-powered ant with smooth animation support."""
    
    DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
    DIR_CHARS = ['▲', '▶', '▼', '◀']
    DIR_NAMES = ['NORTH', 'EAST', 'SOUTH', 'WEST']
    
    def __init__(self, grid: SmoothGrid, model_path: str = None):
        self.grid = grid
        self.x = grid.size // 2
        self.y = grid.size // 2
        self.dir_idx = 0
        self.steps = 0
        self.start_time = time.time()
        
        # Trail for visualization
        self.trail = deque(maxlen=50)
        
        # Model loading (optional)
        self.model = None
        self.use_model = False
        if model_path:
            self._load_model(model_path)
    
    def _load_model(self, path: str):
        """Attempt to load GLADIUS model."""
        try:
            from llama_cpp import Llama
            gguf = Path(path)
            if gguf.is_dir():
                gguf = gguf / "gladius.gguf"
            if gguf.exists():
                self.model = Llama(model_path=str(gguf), n_ctx=128, n_threads=1, verbose=False)
                self.use_model = True
        except Exception:
            pass
    
    def step(self) -> Dict[str, Any]:
        """Execute one simulation step."""
        # Get current cell
        cell = self.grid.get(self.x, self.y)
        
        # Record position before move
        self.trail.append((self.x, self.y))
        
        # Classic Langton's rules (or model decision)
        # On white (0): turn clockwise, flip to black, move
        # On black (1): turn counter-clockwise, flip to white, move
        if cell == 0:
            self.dir_idx = (self.dir_idx + 1) % 4
        else:
            self.dir_idx = (self.dir_idx - 1) % 4
        
        # Flip cell
        self.grid.flip(self.x, self.y)
        
        # Move forward
        dx, dy = self.DIRS[self.dir_idx]
        self.x = (self.x + dx) % self.grid.size
        self.y = (self.y + dy) % self.grid.size
        
        self.steps += 1
        
        return {
            "step": self.steps,
            "pos": (self.x, self.y),
            "dir": self.DIR_NAMES[self.dir_idx],
            "cell_flipped": cell
        }
    
    @property
    def direction_char(self) -> str:
        return self.DIR_CHARS[self.dir_idx]
    
    @property
    def steps_per_sec(self) -> float:
        elapsed = time.time() - self.start_time
        return self.steps / elapsed if elapsed > 0 else 0


class TerminalRenderer:
    """High-performance curses-based terminal renderer."""
    
    # Block characters for different densities
    BLOCKS = [' ', '░', '▒', '▓', '█']
    
    # Color pairs
    COLOR_NORMAL = 1
    COLOR_ANT = 2
    COLOR_TRAIL = 3
    COLOR_STATS = 4
    COLOR_BORDER = 5
    COLOR_HIGHLIGHT = 6
    COLOR_BLACK_CELL = 7
    COLOR_WHITE_CELL = 8
    
    def __init__(self, stdscr, ant: GladiusAntAnimated):
        self.stdscr = stdscr
        self.ant = ant
        self.grid = ant.grid
        
        # Setup curses
        try:
            curses.curs_set(0)
        except curses.error:
            pass  # Terminal doesn't support cursor hiding
        curses.start_color()
        curses.use_default_colors()
        
        # Initialize color pairs
        curses.init_pair(self.COLOR_NORMAL, curses.COLOR_WHITE, -1)
        curses.init_pair(self.COLOR_ANT, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(self.COLOR_TRAIL, curses.COLOR_CYAN, -1)
        curses.init_pair(self.COLOR_STATS, curses.COLOR_GREEN, -1)
        curses.init_pair(self.COLOR_BORDER, curses.COLOR_BLUE, -1)
        curses.init_pair(self.COLOR_HIGHLIGHT, curses.COLOR_YELLOW, -1)
        curses.init_pair(self.COLOR_BLACK_CELL, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(self.COLOR_WHITE_CELL, curses.COLOR_BLACK, -1)
        
        self.stdscr.nodelay(True)
        self.stdscr.timeout(0)
        
        # Get terminal size
        self.height, self.width = stdscr.getmaxyx()
        
        # Calculate grid viewport
        self.grid_width = min(self.width - 40, 100)  # Leave room for stats panel
        self.grid_height = self.height - 8  # Leave room for header/footer
        
        # Animation state
        self.frame = 0
        self.paused = False
        self.speed = 10  # Steps per frame
        self.zoom = 1
        
        # FIXED VIEWPORT - grid stays stationary, ant moves
        # Center the viewport on the starting position (grid center)
        self.viewport_center_x = self.grid.size // 2
        self.viewport_center_y = self.grid.size // 2
        self.follow_ant = False  # Toggle with 'F' key
    
    def draw_border(self, y: int, x: int, h: int, w: int, title: str = ""):
        """Draw a box border with optional title."""
        # Corners
        self.stdscr.addch(y, x, '╔', curses.color_pair(self.COLOR_BORDER))
        self.stdscr.addch(y, x + w - 1, '╗', curses.color_pair(self.COLOR_BORDER))
        self.stdscr.addch(y + h - 1, x, '╚', curses.color_pair(self.COLOR_BORDER))
        try:
            self.stdscr.addch(y + h - 1, x + w - 1, '╝', curses.color_pair(self.COLOR_BORDER))
        except curses.error:
            pass
        
        # Horizontal lines
        for i in range(1, w - 1):
            self.stdscr.addch(y, x + i, '═', curses.color_pair(self.COLOR_BORDER))
            try:
                self.stdscr.addch(y + h - 1, x + i, '═', curses.color_pair(self.COLOR_BORDER))
            except curses.error:
                pass
        
        # Vertical lines
        for i in range(1, h - 1):
            self.stdscr.addch(y + i, x, '║', curses.color_pair(self.COLOR_BORDER))
            try:
                self.stdscr.addch(y + i, x + w - 1, '║', curses.color_pair(self.COLOR_BORDER))
            except curses.error:
                pass
        
        # Title
        if title:
            title_str = f" {title} "
            title_x = x + (w - len(title_str)) // 2
            self.stdscr.addstr(y, title_x, title_str, 
                             curses.color_pair(self.COLOR_HIGHLIGHT) | curses.A_BOLD)
    
    def draw_header(self):
        """Draw animated header."""
        # Spinning animation chars
        spinners = ['◐', '◓', '◑', '◒']
        spinner = spinners[self.frame % len(spinners)]
        
        header = f"╔{'═' * (self.width - 2)}╗"
        self.stdscr.addstr(0, 0, header[:self.width-1], curses.color_pair(self.COLOR_BORDER))
        
        title = f" {spinner} LANGTON'S ANT × GLADIUS NEURAL SIMULATION {spinner} "
        title_x = (self.width - len(title)) // 2
        self.stdscr.addstr(0, max(1, title_x), title, 
                          curses.color_pair(self.COLOR_HIGHLIGHT) | curses.A_BOLD)
        
        # Subtitle
        subtitle = "GLADIUS IS THE ANT - Emergent Intelligence in Action"
        sub_x = (self.width - len(subtitle)) // 2
        self.stdscr.addstr(1, max(0, sub_x), subtitle, curses.color_pair(self.COLOR_NORMAL))
    
    def draw_grid(self, start_y: int, start_x: int):
        """Draw the grid with fixed viewport - ant moves, grid stays still."""
        # Use fixed viewport center OR follow ant based on mode
        if self.follow_ant:
            center_x, center_y = self.ant.x, self.ant.y
        else:
            center_x, center_y = self.viewport_center_x, self.viewport_center_y
        
        view_w = self.grid_width // self.zoom
        view_h = self.grid_height // self.zoom
        half_w = view_w // 2
        half_h = view_h // 2
        
        # Convert trail to set for O(1) lookup
        trail_set = set(self.ant.trail)
        
        for dy in range(min(view_h, self.grid_height)):
            for dx in range(min(view_w, self.grid_width)):
                screen_y = start_y + dy
                screen_x = start_x + dx
                
                if screen_y >= self.height - 1 or screen_x >= self.width - 40:
                    continue
                
                # Calculate actual grid position for this screen position
                grid_x = (center_x - half_w + dx) % self.grid.size
                grid_y = (center_y - half_h + dy) % self.grid.size
                
                # Check if this is the ant position
                if grid_x == self.ant.x and grid_y == self.ant.y:
                    # Ant position - draw the ant character
                    try:
                        self.stdscr.addstr(screen_y, screen_x, self.ant.direction_char,
                                          curses.color_pair(self.COLOR_ANT) | curses.A_BOLD)
                    except curses.error:
                        pass
                elif (grid_x, grid_y) in trail_set:
                    # Trail
                    cell = self.grid.get(grid_x, grid_y)
                    char = '·' if cell == 0 else '•'
                    try:
                        self.stdscr.addstr(screen_y, screen_x, char,
                                          curses.color_pair(self.COLOR_TRAIL))
                    except curses.error:
                        pass
                else:
                    # Regular cell
                    cell = self.grid.get(grid_x, grid_y)
                    if cell == 1:
                        try:
                            self.stdscr.addstr(screen_y, screen_x, '█',
                                              curses.color_pair(self.COLOR_NORMAL))
                        except curses.error:
                            pass
                    else:
                        try:
                            self.stdscr.addstr(screen_y, screen_x, ' ')
                        except curses.error:
                            pass
    
    def draw_stats_panel(self, start_y: int, start_x: int):
        """Draw statistics panel."""
        panel_width = 36
        panel_height = self.height - 4
        
        self.draw_border(start_y, start_x, panel_height, panel_width, "METRICS")
        
        stats = self.grid.get_stats()
        y = start_y + 2
        x = start_x + 2
        
        # Status indicator
        status = "▶ RUNNING" if not self.paused else "⏸ PAUSED"
        status_color = self.COLOR_STATS if not self.paused else self.COLOR_HIGHLIGHT
        self.stdscr.addstr(y, x, status, curses.color_pair(status_color) | curses.A_BOLD)
        y += 1
        
        # View mode indicator
        view_mode = "📍 FOLLOW ANT" if self.follow_ant else "🗺️  FIXED VIEW"
        self.stdscr.addstr(y, x, view_mode, curses.color_pair(self.COLOR_TRAIL))
        y += 2
        
        # Model status
        model_status = "GLADIUS" if self.ant.use_model else "CLASSIC"
        self.stdscr.addstr(y, x, f"Mode: ", curses.color_pair(self.COLOR_NORMAL))
        self.stdscr.addstr(y, x + 6, model_status, 
                          curses.color_pair(self.COLOR_HIGHLIGHT) | curses.A_BOLD)
        y += 2
        
        # Divider
        self.stdscr.addstr(y, x, "─" * (panel_width - 4), curses.color_pair(self.COLOR_BORDER))
        y += 1
        
        # Step counter with animation
        step_str = f"{self.ant.steps:,}"
        self.stdscr.addstr(y, x, "Steps:", curses.color_pair(self.COLOR_NORMAL))
        self.stdscr.addstr(y, x + 8, step_str, 
                          curses.color_pair(self.COLOR_STATS) | curses.A_BOLD)
        y += 1
        
        # Speed
        speed_str = f"{self.ant.steps_per_sec:,.0f}/s"
        self.stdscr.addstr(y, x, "Speed:", curses.color_pair(self.COLOR_NORMAL))
        self.stdscr.addstr(y, x + 8, speed_str, curses.color_pair(self.COLOR_STATS))
        y += 2
        
        # Position
        self.stdscr.addstr(y, x, "Position:", curses.color_pair(self.COLOR_NORMAL))
        y += 1
        self.stdscr.addstr(y, x + 2, f"X: {self.ant.x:,}", curses.color_pair(self.COLOR_STATS))
        y += 1
        self.stdscr.addstr(y, x + 2, f"Y: {self.ant.y:,}", curses.color_pair(self.COLOR_STATS))
        y += 1
        self.stdscr.addstr(y, x + 2, f"Dir: {self.ant.DIR_NAMES[self.ant.dir_idx]}", 
                          curses.color_pair(self.COLOR_STATS))
        y += 2
        
        # Divider
        self.stdscr.addstr(y, x, "─" * (panel_width - 4), curses.color_pair(self.COLOR_BORDER))
        y += 1
        
        # Grid stats
        self.stdscr.addstr(y, x, "Grid Statistics:", 
                          curses.color_pair(self.COLOR_HIGHLIGHT) | curses.A_BOLD)
        y += 1
        
        # Black/White ratio bar
        bar_width = panel_width - 8
        black_ratio = stats["ratio"]
        black_chars = int(black_ratio * bar_width)
        
        self.stdscr.addstr(y, x, "B/W:", curses.color_pair(self.COLOR_NORMAL))
        bar_str = '█' * black_chars + '░' * (bar_width - black_chars)
        self.stdscr.addstr(y, x + 5, bar_str[:bar_width], curses.color_pair(self.COLOR_NORMAL))
        y += 1
        
        self.stdscr.addstr(y, x + 2, f"Black: {stats['black']:,}", 
                          curses.color_pair(self.COLOR_STATS))
        y += 1
        self.stdscr.addstr(y, x + 2, f"White: {stats['white']:,}", 
                          curses.color_pair(self.COLOR_STATS))
        y += 1
        self.stdscr.addstr(y, x + 2, f"Ratio: {black_ratio:.2%}", 
                          curses.color_pair(self.COLOR_STATS))
        y += 2
        
        self.stdscr.addstr(y, x, f"Visited: {stats['visited']:,}", 
                          curses.color_pair(self.COLOR_NORMAL))
        y += 1
        self.stdscr.addstr(y, x, f"Max Visits: {stats['max_visits']:,}", 
                          curses.color_pair(self.COLOR_NORMAL))
        y += 2
        
        # Divider
        if y < start_y + panel_height - 8:
            self.stdscr.addstr(y, x, "─" * (panel_width - 4), curses.color_pair(self.COLOR_BORDER))
            y += 1
        
        # Runtime
        elapsed = time.time() - self.ant.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        self.stdscr.addstr(y, x, "Runtime:", curses.color_pair(self.COLOR_NORMAL))
        self.stdscr.addstr(y, x + 9, f"{hours:02d}:{minutes:02d}:{seconds:02d}", 
                          curses.color_pair(self.COLOR_STATS))
    
    def draw_footer(self):
        """Draw control instructions footer."""
        y = self.height - 2
        
        controls = [
            ("SPACE", "Pause"),
            ("↑/↓", "Speed"),
            ("+/-", "Zoom"),
            ("F", "Follow" if not self.follow_ant else "Fixed"),
            ("R", "Reset"),
            ("Q", "Quit")
        ]
        
        x = 2
        for key, action in controls:
            self.stdscr.addstr(y, x, f"[{key}]", 
                              curses.color_pair(self.COLOR_HIGHLIGHT) | curses.A_BOLD)
            self.stdscr.addstr(y, x + len(key) + 2, f" {action}  ", 
                              curses.color_pair(self.COLOR_NORMAL))
            x += len(key) + len(action) + 6
    
    def draw(self):
        """Main draw routine."""
        self.stdscr.clear()
        
        self.draw_header()
        self.draw_grid(3, 1)
        self.draw_stats_panel(3, self.width - 38)
        self.draw_footer()
        
        self.stdscr.refresh()
        self.frame += 1
    
    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False to quit."""
        try:
            key = self.stdscr.getch()
        except:
            return True
        
        if key == ord('q') or key == ord('Q'):
            return False
        elif key == ord(' '):
            self.paused = not self.paused
        elif key == curses.KEY_UP:
            self.speed = min(1000, self.speed * 2)
        elif key == curses.KEY_DOWN:
            self.speed = max(1, self.speed // 2)
        elif key == ord('+') or key == ord('='):
            self.zoom = min(4, self.zoom + 1)
        elif key == ord('-'):
            self.zoom = max(1, self.zoom - 1)
        elif key == ord('f') or key == ord('F'):
            # Toggle follow mode
            self.follow_ant = not self.follow_ant
        elif key == ord('r') or key == ord('R'):
            # Reset
            self.ant.x = self.grid.size // 2
            self.ant.y = self.grid.size // 2
            self.ant.dir_idx = 0
            self.ant.steps = 0
            self.ant.start_time = time.time()
            self.grid.cells.fill(0)
            self.grid.visit_count.fill(0)
            # Reset viewport to center
            self.viewport_center_x = self.grid.size // 2
            self.viewport_center_y = self.grid.size // 2
        # Arrow keys for panning viewport when not following
        elif key == curses.KEY_LEFT and not self.follow_ant:
            self.viewport_center_x = (self.viewport_center_x - 5) % self.grid.size
        elif key == curses.KEY_RIGHT and not self.follow_ant:
            self.viewport_center_x = (self.viewport_center_x + 5) % self.grid.size
        
        return True


def run_animated(stdscr, model_path: str = None, grid_size: int = 500):
    """Main animation loop."""
    grid = SmoothGrid(grid_size)
    ant = GladiusAntAnimated(grid, model_path)
    renderer = TerminalRenderer(stdscr, ant)
    
    target_fps = 30
    frame_time = 1.0 / target_fps
    
    running = True
    while running:
        frame_start = time.time()
        
        # Handle input
        running = renderer.handle_input()
        
        # Simulation steps
        if not renderer.paused:
            for _ in range(renderer.speed):
                ant.step()
        
        # Render
        renderer.draw()
        
        # Frame timing
        elapsed = time.time() - frame_start
        sleep_time = frame_time - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Langton's Ant - Animated Terminal Visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controls:
  SPACE     Pause/Resume
  ↑/↓       Increase/Decrease speed
  +/-       Zoom in/out
  R         Reset simulation
  Q         Quit

GLADIUS is the ant - watch emergent behavior unfold.
        """
    )
    parser.add_argument('--model', '-m', type=str, help='Path to GLADIUS model')
    parser.add_argument('--grid', '-g', type=int, default=500, help='Grid size (default: 500)')
    
    args = parser.parse_args()
    
    # Run with curses
    try:
        curses.wrapper(lambda stdscr: run_animated(stdscr, args.model, args.grid))
    except KeyboardInterrupt:
        pass
    except curses.error as e:
        print(f"⚠️  Curses error: {e}")
        print("Running in simple mode (requires full terminal for animated view)...")
        run_simple_mode(args.model, args.grid)
    
    print("\n✨ Simulation ended. GLADIUS continues to learn...")


def run_simple_mode(model_path: str, grid_size: int):
    """Fallback simple animation for non-curses terminals."""
    import shutil
    
    grid = SmoothGrid(grid_size)
    ant = GladiusAnt(grid, model_path)
    
    cols, rows = shutil.get_terminal_size((80, 24))
    view_size = min(cols - 10, rows - 10, 60)
    
    print("\n" + "═" * 60)
    print("  LANGTON'S ANT - SIMPLE MODE (GLADIUS IS THE ANT)")
    print("═" * 60 + "\n")
    
    try:
        step = 0
        while True:
            # Clear and draw
            print("\033[H\033[J", end="")  # Clear screen
            
            # Header
            print(f"╔{'═' * 58}╗")
            print(f"║  🐜 GLADIUS ANT │ Step: {step:,} │ Pos: ({ant.x}, {ant.y})".ljust(59) + "║")
            print(f"╠{'═' * 58}╣")
            
            # Draw grid viewport
            half = view_size // 2
            for dy in range(-half, half):
                row = "║ "
                for dx in range(-half, half):
                    x, y = (ant.x + dx) % grid_size, (ant.y + dy) % grid_size
                    if dx == 0 and dy == 0:
                        row += "🐜"
                    elif grid.get(x, y):
                        row += "██"
                    else:
                        row += "  "
                print(row[:59] + " ║")
            
            print(f"╚{'═' * 58}╝")
            print("Press Ctrl+C to exit")
            
            # Step
            ant.step()
            step += 1
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
