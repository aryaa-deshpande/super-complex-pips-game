# backend/engine/map_graph.py

import random
from collections import deque
from typing import List, Dict, Tuple

from .models import Node, MapGraph

import json
from pathlib import Path


# Where we store the last generated map
MAP_FILE_PATH = Path(__file__).parent / "latest_map.json"


def map_to_dict(mg: MapGraph) -> dict:
    """Convert MapGraph -> plain dict so we can save as JSON."""
    return {
        "start_id": mg.start_id,
        "boss_id": mg.boss_id,
        "nodes": [
            {
                "id": n.id,
                "node_type": n.node_type,
                "next_ids": list(n.next_ids),
            }
            for n in mg.nodes.values()
        ],
    }


def map_from_dict(data: dict) -> MapGraph:
    """Convert dict (from JSON) -> MapGraph."""
    nodes = {
        nd["id"]: Node(
            id=nd["id"],
            node_type=nd["node_type"],
            next_ids=list(nd["next_ids"]),
        )
        for nd in data["nodes"]
    }
    return MapGraph(
        nodes=nodes,
        start_id=data["start_id"],
        boss_id=data["boss_id"],
    )


def save_map(mg: MapGraph, path: Path = MAP_FILE_PATH) -> None:
    path.write_text(json.dumps(map_to_dict(mg), indent=2))


def load_map(path: Path = MAP_FILE_PATH) -> MapGraph:
    data = json.loads(path.read_text())
    return map_from_dict(data)


def delete_map(path: Path = MAP_FILE_PATH) -> None:
    """Delete the saved map file if it exists."""
    if path.exists():
        path.unlink()
        print(f"🧹 Deleted {path.name}")
    else:
        print("No saved map to delete.")

        
Coord = Tuple[int, int]  # (layer, col)


# =====================================================================
#  Node typing helpers
# =====================================================================

def choose_node_type(layer: int, num_layers: int) -> str:
    """
    Decide node type based on depth.

    layer 0             -> start
    layer num_layers-1  -> boss
    layer 1             -> play
    others              -> weighted mix of play/event/rest/trade
    """
    if layer == 0:
        return "start"
    if layer == num_layers - 1:
        return "boss"
    if layer == 1:
        return "play"

    depth = layer / (num_layers - 1)

    if depth < 0.4:
        # early: mostly fights, some events
        choices = ["play", "play", "play", "event", "event"]
    elif depth < 0.75:
        # mid: mix of everything
        choices = ["play", "play", "event", "event", "rest", "trade"]
    else:
        # late: more rest/trade, still some fights/events
        choices = ["play", "event", "rest", "rest", "trade", "trade"]

    return random.choice(choices)


def _biased_step_towards(target_col: int, current_col: int) -> int:
    """
    Take a step -1, 0 or +1, but bias slightly towards target_col so
    paths tend to converge on the boss column.
    """
    options = [-1, 0, 1]
    scores = []
    for step in options:
        new_c = current_col + step
        dist_now = abs(current_col - target_col)
        dist_new = abs(new_c - target_col)
        # prefer moves that reduce distance to target
        if dist_new < dist_now:
            score = 3
        elif dist_new == dist_now:
            score = 2
        else:
            score = 1
        scores.append(score)

    total = sum(scores)
    r = random.uniform(0, total)
    acc = 0
    for step, score in zip(options, scores):
        acc += score
        if r <= acc:
            return step
    return 0


# =====================================================================
#  Map generation
# =====================================================================

def generate_map(
    num_layers: int = 15,  # 0..14
    num_cols: int = 7,
    num_paths: int = 3,    # number of distinct routes from bottom to boss
) -> MapGraph:
    """
    Generate a Slay-the-Spire style map:

    - multiple start nodes on bottom layer (layer 0)
    - exactly one boss node on top layer (layer num_layers-1)
    - num_paths continuous paths from bottom to boss (one coord per layer)
      where each step moves at most ±1 column (except the final hop into boss)
    - all nodes lie on at least one path (union of path cells)
    """

    top_layer = num_layers - 1

    # ----- 1. pick a single boss column -----
    boss_col = random.randint(0, num_cols - 1)
    boss_coord: Coord = (top_layer, boss_col)

    # ----- 2. pick starting columns for each path -----
    # up to 5 starts, at least 1
    max_starts = min(5, num_cols)
    actual_paths = min(num_paths, max_starts)
    start_cols_pool = list(range(num_cols))
    random.shuffle(start_cols_pool)
    start_cols = start_cols_pool[:actual_paths]

    # ----- 3. generate continuous paths from each start to boss -----

    paths: List[List[Coord]] = []

    for start_col in start_cols:
        col = start_col
        path: List[Coord] = [(0, col)]  # bottom layer coord

        for layer in range(1, num_layers):
            if layer == top_layer:
                # force final layer to hit boss_col
                col = boss_col
            else:
                step = _biased_step_towards(boss_col, col)
                col = max(0, min(num_cols - 1, col + step))
            path.append((layer, col))

        paths.append(path)

    # ----- 4. collect union of coords per layer -----

    layers: List[Dict[int, Coord]] = [dict() for _ in range(num_layers)]
    for path in paths:
        for layer, col in path:
            layers[layer][col] = (layer, col)

    # guarantee: every layer has >= 1 coord

    # ----- 5. create Node objects with types -----

    coord_to_id: Dict[Coord, str] = {}
    nodes: Dict[str, Node] = {}

    for layer in range(num_layers):
        for col, coord in layers[layer].items():
            node_id = f"L{layer}_C{col}"
            coord_to_id[coord] = node_id
            # override for exact boss coord: ensure boss type there
            if coord == boss_coord:
                node_type = "boss"
            else:
                node_type = choose_node_type(layer, num_layers)
            nodes[node_id] = Node(
                id=node_id,
                node_type=node_type,
                next_ids=[],
            )

    # ----- 6. connect nodes along each path -----

    for path in paths:
        for i in range(len(path) - 1):
            curr = path[i]
            nxt = path[i + 1]
            curr_id = coord_to_id[curr]
            nxt_id = coord_to_id[nxt]
            if nxt_id not in nodes[curr_id].next_ids:
                nodes[curr_id].next_ids.append(nxt_id)

    # (you can add extra lateral edges here if you want more branching,
    #  but this already gives proper continuous routes.)

    # ----- 7. choose canonical start_id -----

    # all nodes on layer 0 are "starts" visually; pick middle one as canonical.
    bottom_cols = sorted(layers[0].keys())
    mid_idx = len(bottom_cols) // 2
    start_coord = layers[0][bottom_cols[mid_idx]]
    start_id = coord_to_id[start_coord]

    boss_id = coord_to_id[boss_coord]

    return MapGraph(nodes=nodes, start_id=start_id, boss_id=boss_id)


# =====================================================================
#  Validation
# =====================================================================

def _parse_id(node_id: str) -> Tuple[int, int]:
    lp, cp = node_id.split("_")
    return int(lp[1:]), int(cp[1:])


def validate_map(map_graph: MapGraph, num_layers: int = 15, num_cols: int = 7) -> bool:
    """
    Validate structural invariants of the map.

    Checks:
      - exactly 1 boss node
      - at least 1 start node
      - every edge goes from layer L -> L+1
      - every non-boss edge moves at most one column (|Δcol| <= 1)
      - every non-start node has at least one incoming edge
      - every node has a path to the boss (all routes converge eventually)
    Raises AssertionError if something is wrong.
    Returns True if everything passes.
    """

    nodes = list(map_graph.nodes.values())
    id_to_node = {n.id: n for n in nodes}

    # find bosses and starts
    bosses = [n for n in nodes if n.node_type == "boss"]
    starts = [n for n in nodes if n.node_type == "start"]

    assert len(bosses) == 1, f"Expected exactly 1 boss, found {len(bosses)}"
    assert len(starts) >= 1, "Expected at least 1 start node"

    boss = bosses[0]

    # ---- check edges: adjacency + layer rules ----
    reverse_adj: Dict[str, List[str]] = {n.id: [] for n in nodes}

    for node in nodes:
        layer, col = _parse_id(node.id)

        if node.node_type == "boss":
            # boss should not have outgoing edges
            assert not node.next_ids, f"Boss {node.id} should not have children"
            continue

        assert layer < num_layers - 1, f"Node {node.id} has invalid layer index"
        assert len(node.next_ids) >= 1, f"Node {node.id} has no outgoing edges"

        for child_id in node.next_ids:
            assert child_id in id_to_node, f"Missing child node {child_id} from {node.id}"
            child_layer, child_col = _parse_id(child_id)

            # must go only one layer up
            assert child_layer == layer + 1, f"Edge {node.id}->{child_id} skips layers"

            # allow big horizontal move ONLY into the boss
            if child_id != boss.id:
                assert abs(child_col - col) <= 1, (
                    f"Edge {node.id}->{child_id} moves too far horizontally"
                )

            reverse_adj[child_id].append(node.id)

    # every non-start node should have at least 1 incoming edge
    for node in nodes:
        if node.node_type == "start":
            continue
        assert len(reverse_adj[node.id]) >= 1, f"Node {node.id} has no incoming edges"

    # ---- check reachability: can every node reach the boss? ----
    reachable_from_boss: set[str] = set()
    q = deque([boss.id])
    reachable_from_boss.add(boss.id)

    while q:
        curr = q.popleft()
        for parent in reverse_adj.get(curr, []):
            if parent not in reachable_from_boss:
                reachable_from_boss.add(parent)
                q.append(parent)

    for node in nodes:
        assert node.id in reachable_from_boss, f"Node {node.id} cannot reach boss {boss.id}"

    return True


# =====================================================================
#  Heuristic "nice map" filter + reroll
# =====================================================================

def is_visually_ok(map_graph: MapGraph, num_layers: int = 15) -> bool:
    """
    Heuristic 'does this look like a decent Slay-style map?'

    Structural rules:
      - bottom layer has at least 2 start nodes
      - at least one middle layer (not 0 or top) has >= 2 nodes (branching)

    Type-count rules (softened so we actually get maps):
      - plays  >= 10
      - rests  >= 1   (we'll *aim* for <= 3 via probabilities)
      - events >= 2   (aim ~2-4)
      - trades >= 1   (aim ~1-3)
    """
    # --- layer structure checks ---
    layers: List[List[int]] = [[] for _ in range(num_layers)]
    for node in map_graph.nodes.values():
        layer, col = _parse_id(node.id)
        layers[layer].append(col)

    # bottom: at least 2 starts (we don't check type here, validator enforces start type)
    if len(layers[0]) < 2:
        return False

    mid_layers = layers[1:-1]
    if not any(len(set(cols)) >= 2 for cols in mid_layers):
        # no branching anywhere -> boring
        return False

    # --- node-type count checks ---
    counts = {"play": 0, "rest": 0, "event": 0, "trade": 0}
    for n in map_graph.nodes.values():
        if n.node_type in counts:
            counts[n.node_type] += 1

    # plays: at least 10
    if counts["play"] < 10:
        return False

    # rests: at least 1
    if counts["rest"] < 1:
        return False

    # events: at least 2
    if counts["event"] < 2:
        return False

    # trades: at least 1
    if counts["trade"] < 1:
        return False

    return True

def generate_valid_map(
    num_layers: int = 15,
    num_cols: int = 7,
    num_paths: int = 3,
    max_attempts: int = 100,
) -> MapGraph:
    """
    Wrapper around generate_map that:
      - generates a map
      - validates structural invariants
      - applies heuristics for 'nice looking' maps
      - rerolls if anything fails
    """
    last_error: Exception | None = None
    for _ in range(max_attempts):
        mg = generate_map(num_layers=num_layers, num_cols=num_cols, num_paths=num_paths)
        try:
            validate_map(mg, num_layers=num_layers, num_cols=num_cols)
        except AssertionError as e:
            last_error = e
            continue

        if not is_visually_ok(mg, num_layers=num_layers):
            continue

        counts = {"play": 0, "rest": 0, "event": 0, "trade": 0}
        for n in mg.nodes.values():
            if n.node_type in counts:
                counts[n.node_type] += 1
        print("Accepted map counts:", counts)


        return mg

    raise RuntimeError(
        f"Could not generate a valid map after {max_attempts} attempts. "
        f"Last error: {last_error}"
    )


# =====================================================================
#  Visualization & debug
# =====================================================================

NODE_CHAR = {
    "start": "S",
    "boss":  "B",
    "play":  ".",
    "event": "?",
    "rest":  "R",
    "trade": "X",
}


def build_node_grid(map_graph: MapGraph, num_layers: int, num_cols: int):
    """Return grid[layer][col] = node_type_char or None."""
    grid = [[None for _ in range(num_cols)] for _ in range(num_layers)]
    for node in map_graph.nodes.values():
        layer_part, col_part = node.id.split("_")
        layer = int(layer_part[1:])
        col = int(col_part[1:])
        grid[layer][col] = NODE_CHAR.get(node.node_type, "?")
    return grid


def visualize_diagram(map_graph: MapGraph, num_layers: int = 15, num_cols: int = 7):
    """
    Pretty-ish ASCII diagram:
      - top layer at top
      - one row of nodes per layer
      - one row of edges between layers (/, \\ or |)
      - columns evenly spaced
    """
    grid = build_node_grid(map_graph, num_layers, num_cols)

    # build child lookup: (layer,col) -> list of child cols (layer+1)
    children_by_coord: Dict[Coord, List[int]] = {}
    for node in map_graph.nodes.values():
        layer_part, col_part = node.id.split("_")
        layer = int(layer_part[1:])
        col = int(col_part[1:])
        coord = (layer, col)
        for child_id in node.next_ids:
            lp, cp = child_id.split("_")
            child_layer = int(lp[1:])
            child_col = int(cp[1:])
            if child_layer == layer + 1:
                children_by_coord.setdefault(coord, []).append(child_col)

    print("\n=== Map Diagram (top to bottom) ===")
    # column header
    header_cells = [f" {c} " for c in range(num_cols)]
    print("      " + "".join(header_cells))

    for layer in reversed(range(num_layers)):
        # ---- node row ----
        node_cells = []
        for col in range(num_cols):
            ch = grid[layer][col] if grid[layer][col] is not None else " "
            node_cells.append(f" {ch} ")
        print(f"L{layer:02d} | " + "".join(node_cells))

        # ---- edge row (between this layer and the one below) ----
        if layer == 0:
            break  # no edges below bottom

        below_layer = layer - 1
        edge_cells = ["   " for _ in range(num_cols)]
        for col in range(num_cols):
            if grid[below_layer][col] is None:
                continue
            coord = (below_layer, col)
            for child_col in children_by_coord.get(coord, []):
                if child_col == col:
                    edge_cells[col] = " | "
                elif child_col == col + 1:
                    edge_cells[col] = " / "
                elif child_col == col - 1:
                    edge_cells[col] = " \\ "
        print("      " + "".join(edge_cells))

    print("Legend: S=start, B=boss, .=play, ?=event, R=rest, X=trade\n")


def debug_node_table(map_graph: MapGraph):
    """
    Print each node as:
      id  (layer,col)  type  ->  list of child (layer,col)
    This is the 'numbers behind the diagram'.
    """
    print("\n=== Node Table ===")
    rows = []
    for node in map_graph.nodes.values():
        layer, col = _parse_id(node.id)
        children = []
        for child_id in node.next_ids:
            child_layer, child_col = _parse_id(child_id)
            children.append(f"({child_layer},{child_col})")
        rows.append((layer, col, node, children))

    rows.sort(key=lambda r: (r[0], r[1]))

    for layer, col, node, children in rows:
        print(
            f"{node.id:7s}  (L{layer:02d},C{col})  {node.node_type:6s} -> "
            f"[{', '.join(children)}]"
        )
    print()


def plot_map_matplotlib(map_graph: MapGraph, num_layers: int = 15, num_cols: int = 7):
    """
    Optional matplotlib visualization:
      - x axis = columns (0..num_cols-1)
      - y axis = layers (0..num_layers-1)
      - different markers per node type
      - lines between connected nodes
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping graphical plot.")
        return

    # positions
    positions: Dict[str, Tuple[int, int]] = {}
    types: Dict[str, str] = {}
    for node in map_graph.nodes.values():
        layer, col = _parse_id(node.id)
        positions[node.id] = (col, layer)
        types[node.id] = node.node_type

    type_style = {
        "start": dict(marker="o", linestyle="None"),
        "boss": dict(marker="s", linestyle="None"),
        "play": dict(marker=".", linestyle="None"),
        "event": dict(marker="^", linestyle="None"),
        "rest": dict(marker="v", linestyle="None"),
        "trade": dict(marker="x", linestyle="None"),
    }

    fig, ax = plt.subplots()

    for node_id, (x, y) in positions.items():
        t = types[node_id]
        style = type_style.get(t, dict(marker=".", linestyle="None"))
        ax.plot(x, y, **style)
        if t in ("boss", "start"):
            ax.text(x + 0.05, y + 0.1, NODE_CHAR[t], fontsize=8)

    for node in map_graph.nodes.values():
        x1, y1 = positions[node.id]
        for child_id in node.next_ids:
            x2, y2 = positions[child_id]
            ax.plot([x1, x2], [y1, y2])

    ax.set_xlabel("column")
    ax.set_ylabel("layer")
    ax.set_xticks(range(num_cols))
    ax.set_yticks(range(num_layers))
    ax.set_ylim(-1, num_layers)
    ax.invert_yaxis()
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_title("Map graph")

    plt.tight_layout()
    plt.show()


# =====================================================================
#  Manual test entrypoint
# =====================================================================

if __name__ == "__main__":
    random.seed()

    mg = generate_valid_map(num_layers=15, num_cols=7, num_paths=3)

    validate_map(mg, num_layers=15, num_cols=7)
    print("✅ Map structure valid.\n")

    # SAVE this map so game_logic can reuse it
    save_map(mg)
    print(f"💾 Saved map to {MAP_FILE_PATH}")

    visualize_diagram(mg, num_layers=15, num_cols=7)
    debug_node_table(mg)
    plot_map_matplotlib(mg, num_layers=15, num_cols=7)