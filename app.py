from flask import Flask, render_template, request
from scraper import scrape_results_page
from analysis import create_graphs

app = Flask(__name__)

DEFAULT_BASE_URL = "https://fabtcg.com/coverage/calling-hamburg/results/"
DEFAULT_ROUNDS = "1-8"

def parse_rounds(rounds_str):
    rounds = set()
    for part in rounds_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            rounds.update(range(int(start), int(end) + 1))
        elif part.isdigit():
            rounds.add(int(part))
    return sorted(rounds)

@app.route('/', methods=['GET', 'POST'])
def index():
    graphs = None
    error = None
    base_url = DEFAULT_BASE_URL
    rounds_str = DEFAULT_ROUNDS
    matches_by_round = {}
    per_round_tables = None
    round1_matches = []
    all_matches = []

    if request.method == 'POST':
        base_url = request.form.get('base_url') or DEFAULT_BASE_URL
        rounds_str = request.form.get('rounds') or DEFAULT_ROUNDS
        rounds = parse_rounds(rounds_str)
        try:
            for r in rounds:
                url = f"{base_url}{r}/"
                matches = scrape_results_page(url, round_number=r, use_local=True)
                matches_by_round[r] = matches
                if r == 1:
                    round1_matches = matches
                all_matches.extend(matches)
            if not all_matches:
                error = "No match data found."
                graphs = None
            else:
                all_rounds = list(range(1, max(rounds)+1))
                graphs, per_round_tables = create_graphs(all_matches, round1_matches, matches_by_round, all_rounds=all_rounds)
        except Exception as e:
            error = f"Error: {e}"
    else:
        rounds = parse_rounds(rounds_str)

    return render_template(
        'index.html',
        graphs=graphs,
        error=error,
        base_url=base_url,
        rounds=rounds_str,
        per_round_tables=per_round_tables
    )

if __name__ == '__main__':
    app.run(debug=True)