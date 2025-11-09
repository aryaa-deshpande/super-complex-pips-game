# engine/run_manager.py
"""
Girl 2 — Game Flow Orchestrator
Integrates deck, board, validation, events, and timer.
"""

import random
import time
from engine.models import RunState, Deck, Pip, Node, MapGraph, Placement
from engine.deck_system import create_starting_deck, sample_rewards, upgrade_pip, remove_pip
from engine.board_gen import generate_board_for_node
from engine.board_validator import validate_board


#run timer
TOTAL_RUN_TIME = 15 * 60  # 15 minutes

def spend_time(run: RunState, seconds: int):
    run.time_remaining = max(run.time_remaining - seconds, 0)
    if run.time_remaining <= 0:
        run.status = "lost"
        print(" Out of time!")
    else:
        print(f" Time left: {run.time_remaining} s")


#  Game Flow


def start_new_run(map_graph: MapGraph) -> RunState:
    """Create a fresh run with a new deck and full timer."""
    deck = create_starting_deck()
    start_id = map_graph.start_id
    return RunState(
        run_id=f"run_{int(time.time())}",
        time_remaining=TOTAL_RUN_TIME,
        deck=deck,
        map_graph=map_graph,
        current_node_id=start_id,
        status="running",
    )


def enter_node(run: RunState, node_id: str):
    node = run.map_graph.nodes[node_id]
    run.current_node_id = node_id
    print(f"\n🔹 Entered node {node.id} ({node.node_type})")

    if node.node_type in ("play", "boss"):
        run.current_board = generate_board_for_node(run.deck, "early", node_id)
        print(f"🧩 Board generated for {node.node_type}")
    elif node.node_type in ("event", "rest", "trade"):
        resolve_event(run, node.node_type)
    return run


def submit_board(run: RunState):
    if not run.current_board:
        print(" No board to submit.")
        return run

    solved = validate_board(run.current_board, run.deck)
    spend_time(run, 10)
    if solved:
        print(" Puzzle solved!")
        run.pending_reward = sample_rewards(run.deck)
        run.current_board = None
    else:
        print(" Failed puzzle.")
        spend_time(run, 30)
    return run


def pick_reward(run: RunState, pip_id: str):
    if not run.pending_reward:
        print("No reward available.")
        return
    chosen = next((p for p in run.pending_reward if p.id == pip_id), None)
    if chosen:
        run.deck.pips.append(chosen)
        run.pending_reward = None
        print(f" Added pip {chosen.id} to deck.")

#  Events / Rest / Trade Logic


def resolve_event(run: RunState, node_type: str):
    deck = run.deck

    if node_type == "rest":
        run.time_remaining += 60
        print("💤 Rest node: +60 seconds.")
        return run

    if node_type == "event":
        event = random.choice(["upgrade_random", "remove_random", "add_random"])
        print(f" Event: {event}")
        if event == "upgrade_random" and deck.pips:
            pip = random.choice(deck.pips)
            upgrade_pip(pip)
            print(f" Upgraded {pip.id}")
        elif event == "remove_random" and deck.pips:
            pip = random.choice(deck.pips)
            remove_pip(deck, pip.id)
            print(f" Removed {pip.id}")
        elif event == "add_random":
            reward = sample_rewards(deck, 1)[0]
            deck.pips.append(reward)
            print(f" Added pip {reward.id}")
        spend_time(run, 10)
        return run

    if node_type == "trade":
        trade = random.choice(["upgrade", "remove", "add"])
        print(f" Trade: {trade}")
        spend_time(run, 30)
        if trade == "upgrade" and deck.pips:
            pip = random.choice(deck.pips)
            upgrade_pip(pip)
            print(f" Upgraded {pip.id}")
        elif trade == "remove" and deck.pips:
            pip = random.choice(deck.pips)
            remove_pip(deck, pip.id)
            print(f" Removed {pip.id}")
        elif trade == "add":
            reward = sample_rewards(deck, 1)[0]
            deck.pips.append(reward)
            print(f" Added {reward.id}")
        return run
