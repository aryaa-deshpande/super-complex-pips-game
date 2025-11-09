from dataclasses import dataclass
from typing import List
import random
from models import Pip, Deck

COMMON_POOL = [
    Pip(f"C{i}{j}", i, j, "common") for i in range(3) for j in range(3)
]
UNCOMMON_POOL = [
    Pip(f"U{i}{j}", i, j, "uncommon") for i in range(3, 6) for j in range(3, 6)
]
RARE_POOL = [
    Pip(f"R{i}{j}", i, j, "rare") for i in range(6, 9) for j in range(6, 9)
]

def get_loot_pool(rarity: str) -> List[Pip]:
    return {
        "common": COMMON_POOL,
        "uncommon": UNCOMMON_POOL,
        "rare": RARE_POOL
    }[rarity]


def create_starting_deck() -> Deck:
    """Make a small deck of common pips."""
    start_pips = random.sample(COMMON_POOL, 6)
    return Deck(pips=start_pips)

def sample_rewards(deck: Deck, n: int = 3) -> List[Pip]:
    """Sample random reward pips after a puzzle."""
    all_pools = COMMON_POOL + UNCOMMON_POOL + RARE_POOL
    return random.sample(all_pools, n)

def upgrade_pip(pip: Pip):
    """Upgrade a pip's rarity."""
    order = ["common", "uncommon", "rare"]
    if pip.rarity in order[:-1]:
        pip.rarity = order[order.index(pip.rarity) + 1]

def remove_pip(deck: Deck, pip_id: str):
    deck.pips = [p for p in deck.pips if p.id != pip_id]
