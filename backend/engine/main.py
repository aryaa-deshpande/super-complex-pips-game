#deck_system
from engine.deck_system import create_starting_deck, sample_rewards

deck = create_starting_deck()
print("Starting deck:", [p.id for p in deck.pips])

rewards = sample_rewards(deck)
print("Reward choices:", [r.id for r in rewards])


#template
from engine.board_templates import get_template

template = get_template("early")
print("\nLoaded Template:", template.id)
for region in template.regions:
    print(f"Region {region.id} → type={region.type}, cells={region.cells}")

#board generate
from engine.board_gen import generate_board_for_node

print("\n--- Generating Board ---")
board_state = generate_board_for_node(deck, "early", "node_1")

print(f"Board ID: {board_state.board_def.id}")
for r in board_state.board_def.regions:
    print(f"Region {r.id}: type={r.type}, target={r.target}")


#board validator

from engine.board_validator import validate_board
from models import Placement

print("\n--- Validation Test ---")

# Use same deck + board_state from earlier
# Pretend the player perfectly filled it with one pip per region
used_pips = deck.pips[:2]
placements = [
    Placement(pip_id=used_pips[0].id, cells=[(0,0), (0,1)]),
    Placement(pip_id=used_pips[1].id, cells=[(1,0), (1,1)])
]
board_state.placements = placements

# Validate
is_solved = validate_board(board_state, deck)
print("Solved?", is_solved)
