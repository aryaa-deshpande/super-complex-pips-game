import math
import arcade
from pathlib import Path
import sys

# --- ensure project root is on sys.path so `backend` is importable ---
THIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.engine.map_graph import (
    load_map,
    MAP_FILE_PATH,
    generate_valid_map,
    save_map,
    _parse_id,
)

# === CONFIG ===
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Pips Game - Map"

NODE_RADIUS = 22
NUM_LAYERS = 15
NUM_COLS = 7

# world coordinate parameters (we make a tall map so scrolling matters)
WORLD_MARGIN_X = 150
WORLD_MARGIN_Y = 120
LAYER_GAP = 110  # distance between layers vertically

ASSETS_DIR = THIS_DIR / "assets"
BG_IMAGE_PATH = ASSETS_DIR / "background.png"  # your parchment image

ICON_PATHS = {
    "start": ASSETS_DIR / "icon_start.png",
    "boss": ASSETS_DIR / "icon_boss.png",
    "play": ASSETS_DIR / "play.png",
    "event": ASSETS_DIR / "event1.png",
    "rest": ASSETS_DIR / "time2.png",
    "trade": ASSETS_DIR / "trade.png",
}

# fallback colors for nodes
NODE_COLORS = {
    "start": arcade.color.SKY_BLUE,
    "boss": arcade.color.CRIMSON,
    "play": arcade.color.LIGHT_GRAY,
    "event": arcade.color.ORANGE,
    "rest": arcade.color.APPLE_GREEN,
    "trade": arcade.color.GOLD,
}


def safe_load_texture(path: Path):
    if path.is_file():
        try:
            return arcade.load_texture(path.as_posix())
        except Exception as e:
            print(f"Warning: failed to load texture {path}: {e}")
    return None


def draw_dotted_line(x1, y1, x2, y2, color, width=2, seg_len=14, gap_len=10):
    """
    Draw a dotted/dashed line from (x1,y1) to (x2,y2) by drawing small
    segments with gaps. This gives the Slay-the-Spire style path.
    (x*, y*) are in SCREEN coordinates here.)
    """
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    ux = dx / dist
    uy = dy / dist

    step = seg_len + gap_len
    t = 0.0
    while t < dist:
        sx = x1 + ux * t
        sy = y1 + uy * t
        ex = x1 + ux * min(dist, t + seg_len)
        ey = y1 + uy * min(dist, t + seg_len)
        arcade.draw_line(sx, sy, ex, ey, color, width)
        t += step


class MapWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)

        # parchment-ish fallback if texture fails
        arcade.set_background_color((245, 235, 205))

        self.map_graph = None

        # node positions in WORLD coordinates
        self.node_positions: dict[str, tuple[float, float]] = {}
        self.current_node_id: str | None = None

        # world scrolling
        self.scroll_y: float = 0.0
        self.world_height: float = SCREEN_HEIGHT

        # textures
        self.background_tex = safe_load_texture(BG_IMAGE_PATH)
        self.icon_textures = {
            node_type: safe_load_texture(path)
            for node_type, path in ICON_PATHS.items()
        }

    # ---- Setup ----
    def setup(self):
        # Load or generate the map
        if MAP_FILE_PATH.exists():
            self.map_graph = load_map()
            print(f"Loaded map from {MAP_FILE_PATH}")
        else:
            print("No map found — generating a new one...")
            self.map_graph = generate_valid_map(
                num_layers=NUM_LAYERS, num_cols=NUM_COLS, num_paths=3
            )
            save_map(self.map_graph)
            print(f"Generated and saved map to {MAP_FILE_PATH}")

        # World layout
        self._compute_positions()

        # compute world height from max y
        max_y = max(y for (_, y) in self.node_positions.values())
        self.world_height = max_y + WORLD_MARGIN_Y

        # Start node (later you can let the player pick)
        self.current_node_id = self.map_graph.start_id

    def _compute_positions(self):
        """Convert (layer, col) -> (x_world, y_world)."""
        usable_width = SCREEN_WIDTH - 2 * WORLD_MARGIN_X
        col_step = usable_width / max(1, (NUM_COLS - 1))

        self.node_positions.clear()
        for node_id, node in self.map_graph.nodes.items():
            layer, col = _parse_id(node_id)
            x = WORLD_MARGIN_X + col * col_step
            y = WORLD_MARGIN_Y + layer * LAYER_GAP
            self.node_positions[node_id] = (x, y)

    # ---- world <-> screen ----
    def world_to_screen(self, x_w: float, y_w: float) -> tuple[float, float]:
        # Scroll is like a camera moving upward: higher scroll_y shows higher layers
        return x_w, y_w - self.scroll_y

    def screen_to_world(self, x_s: float, y_s: float) -> tuple[float, float]:
        return x_s, y_s + self.scroll_y

    # ---- Draw ----
    def on_draw(self):
        self.clear()

        # background parchment image, if available
        if self.background_tex is not None:
            arcade.draw_lrwh_rectangle_textured(
                0,
                0,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                self.background_tex,
            )

        if not self.map_graph:
            return

        # --- Edges (dotted) ---
        path_color = arcade.color.DARK_SLATE_GRAY
        for node in self.map_graph.nodes.values():
            x1_w, y1_w = self.node_positions[node.id]
            for child_id in node.next_ids:
                x2_w, y2_w = self.node_positions[child_id]
                x1_s, y1_s = self.world_to_screen(x1_w, y1_w)
                x2_s, y2_s = self.world_to_screen(x2_w, y2_w)
                draw_dotted_line(x1_s, y1_s, x2_s, y2_s, path_color, width=2)

        # --- Nodes ---
        for node in self.map_graph.nodes.values():
            x_w, y_w = self.node_positions[node.id]
            x_s, y_s = self.world_to_screen(x_w, y_w)

            # cull off-screen vertically
            if y_s < -50 or y_s > SCREEN_HEIGHT + 50:
                continue

            node_type = node.node_type
            is_current = node.id == self.current_node_id

            # highlight ring
            if is_current:
                arcade.draw_circle_outline(
                    x_s, y_s, NODE_RADIUS + 10, arcade.color.LIME_GREEN, border_width=4
                )

            tex = self.icon_textures.get(node_type)
            if tex is not None:
                size = NODE_RADIUS * 2
                arcade.draw_texture_rectangle(
                    x_s,
                    y_s,
                    size,
                    size,
                    tex,
                )
            else:
                # fallback circle
                color = NODE_COLORS.get(node_type, arcade.color.LIGHT_GRAY)
                arcade.draw_circle_filled(x_s, y_s, NODE_RADIUS, color)
                arcade.draw_circle_outline(x_s, y_s, NODE_RADIUS, arcade.color.BLACK, 2)

            arcade.draw_circle_outline(
                x_s, y_s, NODE_RADIUS + 2, arcade.color.DARK_SLATE_GRAY, 1
            )

        # --- HUD ---
        if self.current_node_id:
            curr = self.map_graph.nodes[self.current_node_id]
            next_ids = curr.next_ids

            arcade.draw_text(
                f"Current: {self.current_node_id} ({curr.node_type})",
                20,
                SCREEN_HEIGHT - 40,
                arcade.color.BLACK,
                14,
                bold=True,
            )

            arcade.draw_text(
                f"Next: {', '.join(next_ids) if next_ids else 'None'}",
                20,
                SCREEN_HEIGHT - 65,
                arcade.color.DARK_GRAY,
                12,
            )

        arcade.draw_text(
            "Click a connected node to move   •   UP/DOWN to scroll   •   ESC to quit",
            20,
            20,
            arcade.color.DARK_SLATE_GRAY,
            12,
        )

    # ---- Mouse Interaction ----
    def on_mouse_press(self, x, y, button, modifiers):
        if not self.map_graph or not self.current_node_id:
            return

        x_w, y_w = self.screen_to_world(x, y)

        clicked_id = None
        min_dist2 = (NODE_RADIUS * 2.2) ** 2

        for node_id, (nx_w, ny_w) in self.node_positions.items():
            dx = x_w - nx_w
            dy = y_w - ny_w
            if dx * dx + dy * dy < min_dist2:
                clicked_id = node_id
                break

        if clicked_id is None:
            return

        current_node = self.map_graph.nodes[self.current_node_id]
        if clicked_id not in current_node.next_ids:
            print(f"⚠️ Illegal move: {self.current_node_id} → {clicked_id}")
            return

        self.current_node_id = clicked_id
        node = self.map_graph.nodes[clicked_id]
        print(f"➡️  Moved to {clicked_id} (type={node.node_type})")
        # later: trigger node-specific actions here

    # ---- Keyboard (scroll + quit) ----
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            print("Exiting Arcade frontend.")
            self.close()
            return

        scroll_step = 40
        max_scroll = max(0.0, self.world_height - SCREEN_HEIGHT)

        # Scroll up the map (towards higher layers / boss)
        if symbol in (arcade.key.UP, arcade.key.W):
            self.scroll_y = min(max_scroll, self.scroll_y + scroll_step)
        # Scroll down the map (towards start)
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.scroll_y = max(0.0, self.scroll_y - scroll_step)


def main():
    window = MapWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()