# backend/engine/game_logic.py

import uuid
from typing import Optional

import uuid
from dataclasses import dataclass
from typing import List

from .models import RunState, Deck, Pip, BoardDef, BoardState, RegionConstraint
from .map_graph import load_map, _parse_id, visualize_diagram, delete_map



@dataclass
class NodeView:
    id: str
    node_type: str
    layer: int
    col: int
    next_ids: List[str]


def get_position(run: RunState) -> NodeView:
    node = run.map_graph.nodes[run.current_node_id]
    layer, col = _parse_id(node.id)
    return NodeView(
        id=node.id,
        node_type=node.node_type,
        layer=layer,
        col=col,
        next_ids=list(node.next_ids),
    )


def get_next_options(run: RunState) -> List[str]:
    current = run.map_graph.nodes[run.current_node_id]
    return list(current.next_ids)
# =====================================================================
#  Deck & board stubs (you / Girl 1 will replace these)
# =====================================================================

def get_starting_deck() -> Deck:
    pips = [
        Pip(id="p1", left_val=1, right_val=2, rarity="common"),
        Pip(id="p2", left_val=2, right_val=3, rarity="common"),
        Pip(id="p3", left_val=3, right_val=4, rarity="common"),
    ]
    return Deck(pips=pips)


def start_new_run() -> RunState:
    try:
        map_graph = load_map()  # load the exact map saved by map_graph.py
    except FileNotFoundError:
        raise RuntimeError(
            "No saved map found. Run `python -m backend.engine.map_graph` first "
            "to generate and save a map."
        )

    deck = get_starting_deck()

    return RunState(
        run_id=str(uuid.uuid4()),
        time_remaining=15 * 60,
        deck=deck,
        map_graph=map_graph,
        current_node_id=map_graph.start_id,
        current_board=None,
        pending_reward=None,
        pending_event=None,
        status="running",
    )

def fake_board_for_node(node_id: str) -> BoardState:
    """
    Temporary board generator so the game loop works.
    Girl 1 will replace this later with actual constraint-based boards.
    """
    regions = [
        RegionConstraint(
            id="R",
            cells=[(0, 0), (0, 1), (1, 0), (1, 1)],
            type="sum",
            target=10,
        )
    ]
    board_def = BoardDef(
        id=f"board_{node_id}",
        rows=2,
        cols=2,
        regions=regions,
        time_limit=60,
    )
    return BoardState(board_def=board_def)


# =====================================================================
#  Run orchestration
# =====================================================================




def enter_node(run: RunState, node_id: str) -> RunState:
    """
    Move the player token to a new node on the map.
    For now: only checks that it's a legal next step and updates current_node_id.
    """
    current = run.map_graph.nodes[run.current_node_id]

    if node_id not in current.next_ids and node_id != run.current_node_id:
        raise ValueError(f"Illegal move: {current.id} -> {node_id}")

    run.current_node_id = node_id
    return run

def debug_cli_run():
    """
    Manual trial:
      - load the saved map and create a run
      - let the player choose a starting node
      - show the map in ASCII
      - let the player pick where to go next
      - repeat until boss or quit
      - delete the saved map at the end
    """
    run = start_new_run()

    # --- let the player choose which start node to begin from ---
    start_nodes = []
    for node in run.map_graph.nodes.values():
        if node.node_type == "start":
            layer, col = _parse_id(node.id)
            start_nodes.append((layer, col, node.id))

    # sort by column so the list is stable & easy to read
    start_nodes.sort(key=lambda t: t[1])

    if len(start_nodes) > 1:
        print("Choose your starting node:")
        for i, (layer, col, nid) in enumerate(start_nodes):
            print(f"  [{i}] {nid} (layer={layer}, col={col})")

        while True:
            choice = input("Enter the index of your starting node: ").strip()
            try:
                idx = int(choice)
            except ValueError:
                print("Not a number, try again.")
                continue

            if 0 <= idx < len(start_nodes):
                _, _, chosen_id = start_nodes[idx]
                run.current_node_id = chosen_id
                break
            else:
                print("Index out of range, try again.")
    else:
        # only one start, just use it
        if start_nodes:
            _, _, only_id = start_nodes[0]
            run.current_node_id = only_id

    # --- main navigation loop ---
    try:
        while True:
            print("\n" + "=" * 60)

            # show whole map (same “great map thingy” from map_graph)
            visualize_diagram(run.map_graph, num_layers=15, num_cols=7)

            # show where we are
            pos = get_position(run)
            print(f"You are at: {pos.id} (type={pos.node_type}, layer={pos.layer}, col={pos.col})")

            # check for boss
            if pos.node_type == "boss":
                print("🎉 You reached the boss! Trial over.")
                break

            # list options
            options = get_next_options(run)
            print("\nYou can go to:")
            for i, nid in enumerate(options):
                node = run.map_graph.nodes[nid]
                layer, col = _parse_id(nid)
                print(f"  [{i}] {nid} (type={node.node_type}, layer={layer}, col={col})")

            # ask user choice
            choice = input("\nEnter the index of where you want to go next (or 'q' to quit): ").strip()
            if choice.lower() == "q":
                print("Exiting trial.")
                break

            try:
                idx = int(choice)
            except ValueError:
                print("Not a number, try again.")
                continue

            if idx < 0 or idx >= len(options):
                print("Invalid index, try again.")
                continue

            # move!
            next_id = options[idx]
            run = enter_node(run, next_id)
            run = handle_node_event(run)

    finally:
        # --- cleanup after run, no matter how we exit the loop ---
        print("🧹 Deleting saved map for a clean next run...")
        delete_map()
        print("✅ Map file removed. Generate a new one next time!")
    
def handle_node_event(run: RunState):
    """Perform actions depending on the node type you entered."""
    node = run.map_graph.nodes[run.current_node_id]
    node_type = node.node_type

    print(f"\n🔸 Entered node {node.id} ({node_type})")

    # --- Behavior by type ---
    if node_type == "play":
        print("🧩 This is a puzzle/combat node. (Placeholder: you solved it!)")
        # later: hook your puzzle/mini-game logic here

    elif node_type == "event":
        print("🎲 Random event triggered! You got a mystery bonus.")
        # later: random effects, story snippets, etc.

    elif node_type == "rest":
        print("💤 Rest site — you recovered time or health.")
        run.time_remaining += 60  # gain +1 minute as placeholder

    elif node_type == "trade":
        print("💰 Merchant visit! (Placeholder: traded items)")
        # later: trade inventory/pips

    elif node_type == "boss":
        print("👑 Boss room! Final challenge ahead.")
        # later: trigger boss puzzle or fight

    elif node_type == "start":
        print("🚪 Starting node. Nothing happens yet.")
    else:
        print("❓ Unknown node type — no behavior defined.")

    return run

# simple manual test
if __name__ == "__main__":
    debug_cli_run()