import arcade
from dataclasses import dataclass
from typing import Optional, List, Tuple

# ======================
# ---- CONFIGURATION ----
# ======================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Domino Puzzle (NYT Pips Style)"

TILE_SIZE = 60
BOARD_ROWS = 20
BOARD_COLS = 20
BOARD_START_X = 100
BOARD_START_Y = 100

DOCK_X = 1100
DOCK_Y = 500
DOCK_SPACING = 20

# Asset folder (adjust if needed)
ASSET_PATH = "assets/play/"

# ======================
# ---- DATA CLASSES ----
# ======================

@dataclass
class DominoTile:
    top: int
    bottom: int
    x: float
    y: float
    rotation: int = 0  # 0 = vertical, 1 = horizontal
    placed: bool = False
    being_dragged: bool = False
    dock_index: int = 0


# ======================
# ---- GAME VIEW ----
# ======================

class GameView(arcade.View):
    def __init__(self, active_cells: List[Tuple[int, int]], domino_data: List[Tuple[int, int]]):
        super().__init__()
        self.active_cells = active_cells
        self.domino_data = domino_data

        self.dominoes: List[DominoTile] = []
        self.dragged_domino: Optional[DominoTile] = None
        self.board_state = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

        self.base_tile = None
        self.pip_textures = {}

        self.drag_offset_x = 0
        self.drag_offset_y = 0

    # ------------------------
    #  Setup & asset loading
    # ------------------------

    def setup(self):
        # Load base tile
        try:
            self.base_tile = arcade.load_texture(ASSET_PATH + "base_tile.png")
        except:
            print("Warning: base_tile.png not found")

        # Load pip images
        for i in range(1, 7):
            try:
                self.pip_textures[i] = arcade.load_texture(ASSET_PATH + f"{i}.png")
            except:
                print(f"Warning: {i}.png not found")

        # Create dominoes (start in dock)
        for idx, (top, bottom) in enumerate(self.domino_data):
            dock_y = DOCK_Y - idx * (TILE_SIZE * 2 + DOCK_SPACING)
            domino = DominoTile(top, bottom, DOCK_X, dock_y, dock_index=idx)
            self.dominoes.append(domino)

    # ------------------------
    #  Drawing
    # ------------------------

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color((245, 245, 245))

        # Draw unified light board background
        arcade.draw_rectangle_filled(
            BOARD_START_X + BOARD_COLS * TILE_SIZE / 2,
            BOARD_START_Y + BOARD_ROWS * TILE_SIZE / 2,
            BOARD_COLS * TILE_SIZE,
            BOARD_ROWS * TILE_SIZE,
            (240, 240, 240)
        )

        # Draw active cells
        for row, col in self.active_cells:
            cx = BOARD_START_X + col * TILE_SIZE + TILE_SIZE / 2
            cy = BOARD_START_Y + row * TILE_SIZE + TILE_SIZE / 2
            if self.base_tile:
                arcade.draw_texture_rectangle(cx, cy, TILE_SIZE, TILE_SIZE, self.base_tile)
            else:
                arcade.draw_rectangle_filled(cx, cy, TILE_SIZE, TILE_SIZE, (255, 255, 255))
                arcade.draw_rectangle_outline(cx, cy, TILE_SIZE, TILE_SIZE, (220, 220, 220), 1)

        # Draw dominos
        for domino in self.dominoes:
            self.draw_domino(domino)

    def draw_domino(self, domino):
        cx, cy = domino.x, domino.y
        rot = domino.rotation  # 0..3

        is_vertical = rot in (0, 2)
        # Background size
        w, h = (TILE_SIZE, TILE_SIZE * 2) if is_vertical else (TILE_SIZE * 2, TILE_SIZE)

        # Compute half centers (which side gets the "top" value)
        if rot == 0:            # vertical, top on top
            half_top  = (cx, cy + TILE_SIZE / 2)
            half_bot  = (cx, cy - TILE_SIZE / 2)
        elif rot == 1:          # horizontal, top on left
            half_top  = (cx - TILE_SIZE / 2, cy)
            half_bot  = (cx + TILE_SIZE / 2, cy)
        elif rot == 2:          # vertical, top on bottom (inverted)
            half_top  = (cx, cy - TILE_SIZE / 2)
            half_bot  = (cx, cy + TILE_SIZE / 2)
        else:                   # rot == 3, horizontal, top on right (inverted)
            half_top  = (cx + TILE_SIZE / 2, cy)
            half_bot  = (cx - TILE_SIZE / 2, cy)

        # Card + shadow
        arcade.draw_rectangle_filled(cx + 3, cy - 3, w, h, (220, 220, 220))
        arcade.draw_rectangle_filled(cx, cy, w, h, (255, 253, 249))
        arcade.draw_rectangle_outline(cx, cy, w, h, (210, 210, 210), 1)

        # Divider
        if is_vertical:
            arcade.draw_line(cx - w/2 + 8, cy, cx + w/2 - 8, cy, (230, 230, 230), 2)
        else:
            arcade.draw_line(cx, cy - h/2 + 8, cx, cy + h/2 - 8, (230, 230, 230), 2)

        # Pips/textures
        top_tex = self.pip_textures.get(domino.top)
        bot_tex = self.pip_textures.get(domino.bottom)
        inner_w, inner_h = TILE_SIZE - 10, TILE_SIZE - 10

        if top_tex:
            arcade.draw_texture_rectangle(half_top[0], half_top[1], inner_w, inner_h, top_tex)
        else:
            arcade.draw_text(str(domino.top), half_top[0] - 8, half_top[1] - 10, (0, 0, 0), 20)

        if bot_tex:
            arcade.draw_texture_rectangle(half_bot[0], half_bot[1], inner_w, inner_h, bot_tex)
        else:
            arcade.draw_text(str(domino.bottom), half_bot[0] - 8, half_bot[1] - 10, (0, 0, 0), 20)

        if domino.being_dragged:
            arcade.draw_rectangle_outline(cx, cy, w + 8, h + 8, (120, 180, 255), 3)

    # ------------------------
    #  Interaction
    # ------------------------

    def clear_domino_occupancy(self, domino):
        """Remove this domino's references from the board_state grid."""
        for r in range(len(self.board_state)):
            for c in range(len(self.board_state[0])):
                if self.board_state[r][c] is domino:
                    self.board_state[r][c] = None

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.RIGHT, arcade.key.R):
            if self.dragged_domino and not self.dragged_domino.placed:
                self.dragged_domino.rotation = (self.dragged_domino.rotation + 1) % 4

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for domino in reversed(self.dominoes):
                if self.point_in_domino(x, y, domino):
                    if domino.placed:
                        # pick it back up (free its cells)
                        self.clear_domino_occupancy(domino)
                        domino.placed = False
                    self.dragged_domino = domino
                    domino.being_dragged = True
                    self.drag_offset_x = x - domino.x
                    self.drag_offset_y = y - domino.y
                    break

        elif button == arcade.MOUSE_BUTTON_RIGHT:
            for domino in self.dominoes:
                if self.point_in_domino(x, y, domino) and not domino.placed:
                    domino.rotation = (domino.rotation + 1) % 4
                    break

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragged_domino:
            self.dragged_domino.x = x - self.drag_offset_x
            self.dragged_domino.y = y - self.drag_offset_y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.dragged_domino:
            domino = self.dragged_domino
            domino.being_dragged = False

            if not self.snap_to_grid(domino):
                self.return_to_dock(domino)

            self.dragged_domino = None

    # ------------------------
    #  Logic helpers
    # ------------------------

    def snap_to_grid(self, domino):
        """
        Snap only if the domino's center is within a few pixels of the midpoint
        between *two empty active cells* that match its rotation.
        """
        if not self.active_cells:
            return False

        # remove any old marks from this domino
        self.clear_domino_occupancy(domino)

        # row/col offsets describing how the second half sits relative to the first
        orientation_vectors = {
            0: (1, 0),   # vertical
            1: (0, 1),   # horizontal
            2: (-1, 0),  # vertical flipped
            3: (0, -1),  # horizontal flipped
        }
        dr, dc = orientation_vectors[domino.rotation]

        snap_tolerance = TILE_SIZE * 0.35  # how close center must be

        for (r, c) in self.active_cells:
            other = (r + dr, c + dc)
            if other not in self.active_cells:
                continue
            if self.board_state[r][c] or self.board_state[other[0]][other[1]]:
                continue

            cx1, cy1 = self.cell_center((r, c))
            cx2, cy2 = self.cell_center(other)
            mid_x, mid_y = (cx1 + cx2) / 2, (cy1 + cy2) / 2
            dist = ((domino.x - mid_x) ** 2 + (domino.y - mid_y) ** 2) ** 0.5
            if dist <= snap_tolerance:
                domino.x, domino.y = mid_x, mid_y
                domino.placed = True
                self.board_state[r][c] = domino
                self.board_state[other[0]][other[1]] = domino
                return True

        return False

    def cell_center(self, cell: Tuple[int, int]) -> Tuple[float, float]:
        row, col = cell
        cx = BOARD_START_X + col * TILE_SIZE + TILE_SIZE / 2
        cy = BOARD_START_Y + row * TILE_SIZE + TILE_SIZE / 2
        return cx, cy

    def point_in_domino(self, x, y, domino):
        is_vertical = domino.rotation in (0, 2)
        if is_vertical:
            return abs(x - domino.x) <= TILE_SIZE / 2 and abs(y - domino.y) <= TILE_SIZE
        else:
            return abs(x - domino.x) <= TILE_SIZE and abs(y - domino.y) <= TILE_SIZE / 2

    def return_to_dock(self, domino):
        self.clear_domino_occupancy(domino)
        idx = domino.dock_index
        dock_y = DOCK_Y - idx * (TILE_SIZE * 2 + DOCK_SPACING)
        domino.x, domino.y = DOCK_X, dock_y
        domino.placed = False
        domino.rotation = 0


# ======================
# ---- RUN GAME ----
# ======================

def play(active_cells: List[Tuple[int, int]], domino_data: List[Tuple[int, int]]):
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game = GameView(active_cells, domino_data)
    game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    # Example: Python list (define which cells are visible/active)
    active_cells = [
        (5, 8), (6, 8),
        (7, 8), (8, 8),
        (8, 9), (8, 10),
        (9, 10), (10, 10)
    ]

    domino_data = [
        (1, 2), (3, 5), (6, 4), (2, 6)
    ]

    play(active_cells, domino_data)

    # Later: Load active_cells from JSON
    """
    import json
    with open('board_layout.json', 'r') as f:
        data = json.load(f)
    active_cells = [tuple(cell) for cell in data["active_cells"]]
    play(active_cells, domino_data)
    """