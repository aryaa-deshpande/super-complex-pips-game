
# ----------------------------------------------------------------------
# 1. Deck system
# ----------------------------------------------------------------------
from engine.deck_system import create_starting_deck, sample_rewards

deck = create_starting_deck()
print("Starting deck:", [p.id for p in deck.pips])

rewards = sample_rewards(deck)
print("Reward choices:", [r.id for r in rewards])

# ----------------------------------------------------------------------
# 2. Board template
# ----------------------------------------------------------------------
from engine.board_templates import get_template

template = get_template("early")
print("\nLoaded Template:", template.id)
for region in template.regions:
    print(f"Region {region.id} → type={region.type}, cells={region.cells}")

# ----------------------------------------------------------------------
# 3. Board generation
# ----------------------------------------------------------------------
from engine.board_gen import generate_board_for_node

print("\n--- Generating Board ---")
board_state = generate_board_for_node(deck, "early", "node_1")

print(f"Board ID: {board_state.board_def.id}")
for r in board_state.board_def.regions:
    print(f"Region {r.id}: type={r.type}, target={r.target}")

# ----------------------------------------------------------------------
# 4. Board validation
# ----------------------------------------------------------------------
from engine.board_validator import validate_board
from engine.models import Placement

print("\n--- Validation Test ---")
# Pretend the player perfectly filled it with one pip per region
used_pips = deck.pips[:2]
placements = [
    Placement(pip_id=used_pips[0].id, cells=[(0, 0), (0, 1)]),
    Placement(pip_id=used_pips[1].id, cells=[(1, 0), (1, 1)]),
]
board_state.placements = placements

is_solved = validate_board(board_state, deck)
print("Solved?", is_solved)

# ----------------------------------------------------------------------
# 5. Run manager test (complete flow)
# ----------------------------------------------------------------------
from engine.map_graph import generate_map
from engine.run_manager import (
    start_new_run,
    enter_node,
    submit_board,
    pick_reward,
)

# Generate a map before starting the run
print("\n--- Creating Map ---")
map_graph = generate_map(num_layers=5, num_cols=4, num_paths=2)

# Start a new run
run = start_new_run(map_graph)

# Enter the starting node
enter_node(run, run.current_node_id)
submit_board(run)

if run.pending_reward:
    pick_reward(run, run.pending_reward[0].id)

# Step through some nodes (simulated)
for next_node in list(run.map_graph.nodes.keys())[1:4]:
    enter_node(run, next_node)
