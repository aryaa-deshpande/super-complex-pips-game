import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from engine.models import BoardDef, BoardState, Placement, Deck
# Board Validation Logic

def validate_board(board_state: BoardState, deck: Deck) -> bool:
    """
    Given the player's current placements and the board definition,
    check if the puzzle is correctly solved.
    """

    board_def: BoardDef = board_state.board_def
    placements = board_state.placements

    # All regions filled?
    region_ids = {r.id for r in board_def.regions}
    placed_regions = set()

    for pl in placements:
        placed_regions.update(_find_regions_for_cells(pl.cells, board_def))

    if region_ids != placed_regions:
        # Not all regions have any pip covering them
        return False

    # No overlapping cells
    used_cells = []
    for pl in placements:
        for cell in pl.cells:
            if cell in used_cells:
                print(f" Overlap detected at cell {cell}")
                return False
            used_cells.append(cell)

    # Check each region’s rule
    pip_lookup = {p.id: p for p in deck.pips}

    for region in board_def.regions:
        region_cells = set(region.cells)
        # Get placements overlapping this region
        region_pips = [pip_lookup[p.pip_id] for p in placements if set(p.cells) & region_cells]

        # Skip empty regions
        if not region_pips:
            return False

        if region.type == "sum":
            total = sum(p.left_val + p.right_val for p in region_pips)
            if region.target is not None and total != region.target:
                print(f" Region {region.id} sum {total} != target {region.target}")
                return False

        elif region.type == "all-different":
            vals = [v for p in region_pips for v in (p.left_val, p.right_val)]
            if len(vals) != len(set(vals)):
                print(f" Region {region.id} has duplicates: {vals}")
                return False

    print(" All checks passed! Puzzle solved.")
    return True

#find region(s) covering a given set of cells

def _find_regions_for_cells(cells, board_def: BoardDef):
    found = set()
    for region in board_def.regions:
        for c in cells:
            if c in region.cells:
                found.add(region.id)
    return found
