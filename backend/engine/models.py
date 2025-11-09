from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

# ---- Pips & Deck ----

@dataclass
class Pip:
    id: str
    left_val: int
    right_val: int
    rarity: str                  # "common" | "uncommon" | "rare"
    feature: Optional[str] = None  # "wild", "autolock", "+time", etc.

@dataclass
class Deck:
    pips: List[Pip]

# ---- Board & Constraints ----

@dataclass
class RegionConstraint:
    id: str                      # region name, e.g. "R", "B"
    cells: List[Tuple[int, int]] # list of (row, col)
    type: str                    # "sum", "all-different"
    target: Optional[int] = None # sum target if type == "sum"

@dataclass
class BoardDef:
    id: str
    rows: int
    cols: int
    regions: List[RegionConstraint]
    time_limit: int              # seconds

@dataclass
class Placement:
    pip_id: str
    cells: List[Tuple[int, int]]  # two adjacent cells

@dataclass
class BoardState:
    board_def: BoardDef
    placements: List[Placement] = field(default_factory=list)

# ---- Map ----

@dataclass
class Node:
    id: str
    node_type: str                # "play" | "event" | "rest" | "trade" | "boss"
    next_ids: List[str]

@dataclass
class MapGraph:
    nodes: Dict[str, Node]
    start_id: str
    boss_id: str

# ---- Run ----

@dataclass
class RunState:
    run_id: str
    time_remaining: int           # global timer in seconds
    deck: Deck
    map_graph: MapGraph
    current_node_id: str
    current_board: Optional[BoardState] = None
    pending_reward: Optional[List[Pip]] = None
    pending_event: Optional[dict] = None
    status: str = "running"       # "running" | "won" | "lost"