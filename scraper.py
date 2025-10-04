import requests
from bs4 import BeautifulSoup
import os

def parse_player(td):
    """Extract player info from a player cell."""
    # Name
    strong = td.select_one('.player-text strong')
    name = strong.get_text(strip=True) if strong else ""
    # Deck
    deck = td.select_one('.player-text span')
    deck = deck.get_text(strip=True) if deck else ""
    # Country (from <i class="flag XX">)
    flag = td.select_one('.player-text i.flag')
    country = ""
    if flag and 'class' in flag.attrs:
        for c in flag['class']:
            if c != 'flag':
                country = c.upper()
                break
    return {"name": name, "deck": deck, "country": country}

def scrape_results_page(results_url, round_number=None, use_local=True):
    """
    Scrape a results page. If use_local=True and a local file exists, use it.
    Otherwise, download from the web.
    """
    local_filename = None
    if round_number is not None:
        local_filename = f"results_round{round_number}.html"
    
    html = None
    if use_local and local_filename and os.path.exists(local_filename):
        with open(local_filename, encoding="utf-8") as f:
            html = f.read()
    else:
        resp = requests.get(results_url)
        resp.raise_for_status()
        html = resp.text
        # Optional: Save to file for future runs
        if local_filename:
            with open(local_filename, "w", encoding="utf-8") as f:
                f.write(html)
    
    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    for row in soup.select('tr.match-row'):
        tds = row.find_all('td')
        if len(tds) != 3:
            continue
        player1 = parse_player(tds[0])
        player2 = parse_player(tds[2])
        winner_span = tds[1].select_one('.winner-pill')
        winner = winner_span.get_text(strip=True) if winner_span else ""
        matches.append({
            "player1": player1,
            "player2": player2,
            "winner": winner
        })
    return matches