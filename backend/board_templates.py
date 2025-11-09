from models import RegionConstraint, BoardDef

# Basic Board Templates

# Early Game Template (2x2 grid, 2 regions)
EARLY_TEMPLATE = BoardDef(
    id="early_1",
    rows=2,
    cols=2,
    regions=[
        RegionConstraint(
            id="A",
            cells=[(0, 0), (0, 1)],
            type="sum",
            target=None,  # computed later from solution
        ),
        RegionConstraint(
            id="B",
            cells=[(1, 0), (1, 1)],
            type="sum",
            target=None,
        ),
    ],
    time_limit=60,
)

# Mid Game Template (3x3 grid, 3 regions)
MID_TEMPLATE = BoardDef(
    id="mid_1",
    rows=3,
    cols=3,
    regions=[
        RegionConstraint(
            id="R",
            cells=[(0, 0), (0, 1), (1, 0)],
            type="sum",
            target=None,
        ),
        RegionConstraint(
            id="G",
            cells=[(1, 1), (1, 2), (2, 1)],
            type="sum",
            target=None,
        ),
        RegionConstraint(
            id="B",
            cells=[(2, 2), (2, 0)],
            type="all-different",
            target=None,
        ),
    ],
    time_limit=90,
)

# Boss Template (4x4 grid, 4 regions)
BOSS_TEMPLATE = BoardDef(
    id="boss_1",
    rows=4,
    cols=4,
    regions=[
        RegionConstraint(
            id="R1",
            cells=[(0, 0), (0, 1), (1, 0), (1, 1)],
            type="sum",
        ),
        RegionConstraint(
            id="R2",
            cells=[(0, 2), (0, 3), (1, 2), (1, 3)],
            type="sum",
        ),
        RegionConstraint(
            id="R3",
            cells=[(2, 0), (2, 1), (3, 0), (3, 1)],
            type="sum",
        ),
        RegionConstraint(
            id="R4",
            cells=[(2, 2), (2, 3), (3, 2), (3, 3)],
            type="all-different",
        ),
    ],
    time_limit=120,
)

# Template Registry

TEMPLATES = {
    "early": EARLY_TEMPLATE,
    "mid": MID_TEMPLATE,
    "boss": BOSS_TEMPLATE,
}


def get_template(name: str) -> BoardDef:
    """Return a copy of the requested board template."""
    import copy
    if name not in TEMPLATES:
        raise ValueError(f"No template named {name}")
    return copy.deepcopy(TEMPLATES[name])
