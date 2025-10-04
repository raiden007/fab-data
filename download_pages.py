import requests

BASE_URL = "https://fabtcg.com/coverage/calling-hamburg/results/"
ROUNDS = range(1, 9)  # For rounds 1 to 8

for rnd in ROUNDS:
    url = f"{BASE_URL}{rnd}/"
    print(f"Downloading Round {rnd} ...")
    resp = requests.get(url)
    resp.raise_for_status()
    with open(f"results_round{rnd}.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
print("Done.")