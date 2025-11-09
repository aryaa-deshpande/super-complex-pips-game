import random
from models import Pip, Deck, BoardDef, BoardState, Placement
from engine.board_templates import get_template

# Select Pips for This Board

def select_pips_for_board(deck: Deck, template: BoardDef) -> list[Pip]:
    """Pick N pips from the player's deck based on number of regions."""
    n = len(template.regions)
    if len(deck.pips) < n:
        raise ValueError("Not enough pips in deck for this board!")
    return random.sample(deck.pips, n)

# Place Pips on Template (hidden valid layout)

def place_pips_on_template(template: BoardDef, used_pips: list[Pip]) -> list[Placement]:
    """Assign each region one pip (temporary logic)."""
    placements = []
    for region, pip in zip(template.regions, used_pips):
        # For simplicity: assign each pip to the first two cells of the region
        cells = region.cells[:2]
        placement = Placement(pip_id=pip.id, cells=cells)
        placements.append(placement)
    return placements

#  Derive Constraints from That Layout

def derive_constraints(template: BoardDef, placements: list[Placement], deck: Deck) -> BoardDef:
    """Set target sums or uniqueness conditions based on the hidden solution."""
    # Build pip lookup
    pip_lookup = {p.id: p for p in deck.pips}

    for region, placement in zip(template.regions, placements):
        pip = pip_lookup[placement.pip_id]
        if region.type == "sum":
            region.target = pip.left_val + pip.right_val
        elif region.type == "all-different":
            region.target = None  # checked during validation
    return template


# Generate a Full Board for a Node

def generate_board_for_node(deck: Deck, template_name: str, node_id: str) -> BoardState:
    """Main pipeline: deck → board."""
    template = get_template(template_name)
    used_pips = select_pips_for_board(deck, template)
    placements = place_pips_on_template(template, used_pips)
    board_def = derive_constraints(template, placements, deck)

    # Start with empty board for the player
    board_state = BoardState(board_def=board_def, placements=[])
    return board_state
