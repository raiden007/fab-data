import plotly.graph_objs as go
import plotly.io as pio
from collections import Counter, defaultdict

def create_graphs(matches, round1_matches=None, matches_by_round=None, all_rounds=None):
    if not matches:
        return [], []

    # --- Identify round 1 players and their decks ---
    round1_players = set()
    round1_player_decks = dict()
    if round1_matches:
        for m in round1_matches:
            p1 = m["player1"]
            p2 = m["player2"]
            round1_players.add(p1["name"])
            round1_players.add(p2["name"])
            round1_player_decks[p1["name"]] = p1["deck"]
            round1_player_decks[p2["name"]] = p2["deck"]
    else:
        for m in matches:
            p1 = m["player1"]
            p2 = m["player2"]
            round1_players.add(p1["name"])
            round1_players.add(p2["name"])
            round1_player_decks[p1["name"]] = p1["deck"]
            round1_player_decks[p2["name"]] = p2["deck"]

    # Deck counts: strictly one per round 1 player
    deck_counts = Counter(round1_player_decks.values())

    # For other stats
    player_match_counts = defaultdict(int)
    player_win_counts = defaultdict(int)
    player_decks = dict()
    player_countries = dict()
    table_rows = []

    for m in matches:
        p1 = m["player1"]
        p2 = m["player2"]
        player_decks[p1["name"]] = p1["deck"]
        player_decks[p2["name"]] = p2["deck"]
        player_countries[p1["name"]] = p1["country"]
        player_countries[p2["name"]] = p2["country"]
        player_match_counts[p1["name"]] += 1
        player_match_counts[p2["name"]] += 1
        winner_name = None
        if m["winner"].lower().startswith("player 1"):
            winner_name = p1["name"]
        elif m["winner"].lower().startswith("player 2"):
            winner_name = p2["name"]
        if winner_name:
            player_win_counts[winner_name] += 1

        table_rows.append([
            p1["name"], p1["deck"], p1["country"],
            m["winner"],
            p2["name"], p2["deck"], p2["country"]
        ])

    total_unique_players = len(round1_players)
    summary_html = f"<h2>Total unique players (from Round 1): {total_unique_players}</h2>"

    # Deck count table
    sorted_decks = deck_counts.most_common()
    deck_table_fig = go.Figure(data=[go.Table(
        header=dict(values=["Deck", "Player Count"]),
        cells=dict(values=[[deck for deck, _ in sorted_decks], [count for _, count in sorted_decks]])
    )])
    deck_table_fig.update_layout(title="Number of Players per Deck (from Round 1 only)")
    deck_table_html = pio.to_html(deck_table_fig, full_html=False)

    # Deck distribution bar chart (normal, not pie)
    deck_bar_fig = go.Figure([go.Bar(
        x=[deck for deck, _ in sorted_decks],
        y=[count for _, count in sorted_decks]
    )])
    deck_bar_fig.update_layout(title="Deck Distribution (Round 1 only)", xaxis_title="Deck", yaxis_title="Number of Players")
    deck_bar_html = pio.to_html(deck_bar_fig, full_html=False)

    # --- Day 2 Analysis: Decks of players with at most 2 losses (6-2 or better, or 5-2 or better depending on Swiss rounds) ---
    swiss_rounds = max(all_rounds) if all_rounds else 8
    win_cutoff = 6 if swiss_rounds >= 8 else 5
    # Players who made Day 2 (at most 2 losses in Swiss)
    day2_players = [name for name, wins in player_win_counts.items() if wins >= win_cutoff]
    day2_decks = [player_decks[name] for name in day2_players if name in player_decks]
    day2_deck_counts = Counter(day2_decks)
    sorted_day2_decks = day2_deck_counts.most_common()

    day2_bar_fig = go.Figure([go.Bar(
        x=[deck for deck, _ in sorted_day2_decks],
        y=[count for _, count in sorted_day2_decks]
    )])
    day2_bar_fig.update_layout(
        title=f"Day 2 Analysis: Decks of Players with {win_cutoff} or More Wins (Swiss Only)",
        xaxis_title="Deck",
        yaxis_title="Number of Players"
    )
    day2_bar_html = pio.to_html(day2_bar_fig, full_html=False)

    # Table of all matches
    headers = ["P1 Name", "P1 Deck", "P1 Country", "Winner", "P2 Name", "P2 Deck", "P2 Country"]
    table_fig = go.Figure(data=[go.Table(
        header=dict(values=headers),
        cells=dict(values=[list(col) for col in zip(*table_rows)])
    )])
    table_fig.update_layout(title="All Matches")
    table_html = pio.to_html(table_fig, full_html=False)

    # Romanian players win rate table (all rounds, wins desc + name asc, no matches column)
    romanian_players = [name for name, country in player_countries.items() if country.upper() == "RO"]
    rom_table_rows = []
    for name in romanian_players:
        wins = player_win_counts.get(name, 0)
        winrate = f"{(wins/player_match_counts[name]*100):.1f}%" if player_match_counts[name] else "0.0%"
        rom_table_rows.append([name, player_decks.get(name, ""), wins, winrate])
    rom_table_rows = sorted(rom_table_rows, key=lambda x: (-x[2], x[0]))
    rom_headers = ["Romanian Player", "Deck", "Wins", "Win Rate"]
    rom_table_fig = go.Figure(data=[go.Table(
        header=dict(values=rom_headers),
        cells=dict(values=[list(col) for col in zip(*rom_table_rows)]) if rom_table_rows else dict(values=[[],[],[],[]])
    )])
    rom_table_fig.update_layout(title="Romanian Players and Their Win Rate (All Rounds, Sorted by Wins)")
    rom_table_html = pio.to_html(rom_table_fig, full_html=False)

    # Per-round match tables - always ascending order and always present
    per_round_tables = []
    if all_rounds is None and matches_by_round:
        all_rounds = sorted(matches_by_round.keys())

    if all_rounds:
        headers = ["P1 Name", "P1 Deck", "P1 Country", "Winner", "P2 Name", "P2 Deck", "P2 Country"]
        for rnd in all_rounds:
            rows = []
            for m in matches_by_round.get(rnd, []):
                p1 = m["player1"]
                p2 = m["player2"]
                rows.append([
                    p1["name"], p1["deck"], p1["country"],
                    m["winner"],
                    p2["name"], p2["deck"], p2["country"]
                ])
            table_fig = go.Figure(data=[go.Table(
                header=dict(values=headers),
                cells=dict(values=[list(col) for col in zip(*rows)]) if rows else dict(values=[[],[],[],[],[],[],[]])
            )])
            table_fig.update_layout(title=f"Matches - Round {rnd}")
            table_html = pio.to_html(table_fig, full_html=False)
            per_round_tables.append(table_html)

    return [
        summary_html,
        deck_table_html,
        deck_bar_html,
        day2_bar_html,
        table_html,
        rom_table_html
    ], per_round_tables