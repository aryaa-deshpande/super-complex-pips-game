# backend/engine/node_actions.py

from .models import RunState

def handle_node_event(run: RunState) -> RunState:
    """
    Defines what happens when the player enters a node.
    Simple CLI-driven version for now.
    """
    node = run.map_graph.nodes[run.current_node_id]
    node_type = node.node_type

    print(f"\n🔸 Entered node {node.id} (type={node_type})")
    print(f"⏱️  Time remaining: {run.time_remaining} seconds")

    # START
    if node_type == "start":
        print("🚪 Starting node – nothing happens yet.")
        return run

    # REST
    if node_type == "rest":
        print("💤 Rest site: you recovered some time.")
        run.time_remaining += 60
        print(f"⏱️  New time remaining: {run.time_remaining} seconds")
        return run

    # EVENT
    if node_type == "event":
        print("🎲 Event node!")
        print("  [1] Take risk (-20s)")
        print("  [2] Play safe (0s)")
        choice = input("Choose event option (1/2): ").strip()
        if choice == "1":
            run.time_remaining -= 20
            print("You took the risk. -20s.")
        else:
            print("You played it safe.")
        return run

    # TRADE
    if node_type == "trade":
        print("💰 Trade node!")
        print("  [1] Big trade (-30s)")
        print("  [2] Small trade (-10s)")
        print("  [3] Skip")
        choice = input("Choose trade option (1/2/3): ").strip()
        if choice == "1":
            run.time_remaining -= 30
            print("Big trade done.")
        elif choice == "2":
            run.time_remaining -= 10
            print("Small trade done.")
        else:
            print("Skipped.")
        return run

    # PLAY / BOSS
    if node_type in ("play", "boss"):
        print(f"🧩 {'BOSS FIGHT' if node_type == 'boss' else 'PUZZLE NODE'}")

        t_str = input("How many seconds did this take? ").strip()
        try:
            t_spent = int(t_str)
        except ValueError:
            t_spent = 30

        run.time_remaining -= t_spent

        if run.time_remaining <= 0:
            print("💀 Out of time! Game over.")
            run.status = "lost"
            return run

        result = input("Did you succeed? (y/n): ").strip().lower()
        if result == "n":
            run.status = "lost"
            print("❌ Puzzle failed.")
            return run

        if node_type == "boss":
            run.status = "won"
            print("👑 You defeated the boss!")
        else:
            print("✅ Puzzle cleared!")

        return run

    print("❓ Unknown node type.")
    return run

