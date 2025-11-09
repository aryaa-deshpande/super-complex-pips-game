# backend/engine/game_logic.py

import uuid
from typing import Optional

from .models import (
    RunState,
    Deck,
    Pip,
    BoardDef,
    BoardState,
    RegionConstraint,
)
from .map_graph import generate_valid_map


# =====================================================================
#  Deck & board stubs (you / Girl 1 will replace these)
# =====================================================================

def get_starting_deck() -> Deck:
    """
    Temporary starting deck.
    Replace later with your real pip loot-pool logic.
    """
    pips = [
        Pip(id="p1", left_val=1, right_val=2, rarity="common"),
        Pip(id="p2", left_val=2, right_val=3, rarity="common"),
        Pip(id="p3", left_val=3, right_val=4, rarity="common"),
    ]
    return Deck(pips=pips)


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

def start_new_run() -> RunState:
    """
    Create a fresh RunState:
      - 15 minute global timer
      - starting deck
      - freshly generated & validated map
      - current node set to start_id
      - no board yet; first 'play' node will attach one
    """
    run_id = str(uuid.uuid4())
    deck = get_starting_deck()
    map_graph = generate_valid_map(num_layers=15, num_cols=7, num_paths=3)

    run = RunState(
        run_id=run_id,
        time_remaining=15 * 60,  # 15 minutes
        deck=deck,
        map_graph=map_graph,
        current_node_id=map_graph.start_id,
        current_board=None,
        pending_reward=None,
        pending_event=None,
        status="running",
    )
    return run


def enter_node(run: RunState, node_id: str) -> RunState:
    """
    Move the run into a node.
    For now:
      - if node_type in ('play', 'boss'): attach a fake board
      - if 'event': stub a simple event
      - if 'rest': add 60 seconds
      - if 'trade': stub a trade
    """
    node = run.map_graph.nodes[node_id]
    run.current_node_id = node_id

    if node.node_type in ("play", "boss"):
        run.current_board = fake_board_for_node(node_id)
        run.pending_event = None
        run.pending_reward = None
    elif node.node_type == "event":
        run.pending_event = {"type": "upgrade", "desc": "Upgrade one pip"}
        run.current_board = None
    elif node.node_type == "rest":
        run.time_remaining += 60
        run.current_board = None
        run.pending_event = None
    elif node.node_type == "trade":
        run.pending_event = {"type": "trade", "desc": "Trade time for pip change"}
        run.current_board = None

    return run


# simple manual test
if __name__ == "__main__":
    run = start_new_run()
    print("Run ID:", run.run_id)
    print("Start node:", run.current_node_id)
    print("Map start_id:", run.map_graph.start_id, "boss_id:", run.map_graph.boss_id)
    print("Deck:", [p.id for p in run.deck.pips])

    # enter the start node (which will usually be a 'start' or 'play' type)
    run = enter_node(run, run.current_node_id)
    print("After entering start, current_board:", run.current_board.board_def.id if run.current_board else None)