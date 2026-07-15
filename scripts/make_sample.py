#!/usr/bin/env python3
"""Generate clearly-labelled SAMPLE data so the site renders before real data.

This produces docs/data/latest.json and docs/data/history.json with `sample: true`
so the frontend shows a "sample data" banner. The real pipeline
(scripts/build_index.py) discards anything flagged sample on its first run and
replaces it with live pokemontcg.io prices, so these numbers never mix with real
market data.

Prices and history here are synthetic and for layout preview ONLY -- they are not
real market values. Runs offline (no API, no dependencies).
"""

import json
import math
import os
import random
from datetime import datetime, timedelta, timezone

random.seed(500)  # reproducible sample

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, os.pardir, "docs", "data")

# A few real chase cards to make the top of the table recognisable, then we fill
# the rest with plausible Pokemon x set combinations. All PRICES are synthetic.
TOP_CARDS = [
    ("Charizard", "Base Set", "4/102", "Holo Rare"),
    ("Charizard", "Base Set 1st Edition", "4/102", "Holo Rare"),
    ("Blastoise", "Base Set", "2/102", "Holo Rare"),
    ("Lugia", "Neo Genesis 1st Edition", "9/111", "Holo Rare"),
    ("Umbreon", "Evolving Skies", "215/203", "Alt Art Secret"),
    ("Rayquaza", "Evolving Skies", "218/203", "Alt Art Secret"),
    ("Pikachu", "Base Set", "58/102", "Common"),
    ("Charizard VMAX", "Champion's Path", "074/073", "Secret Rare"),
    ("Mewtwo", "Base Set", "10/102", "Holo Rare"),
    ("Gengar", "Fossil", "5/62", "Holo Rare"),
    ("Espeon", "Evolving Skies", "217/203", "Alt Art Secret"),
    ("Giratina V", "Lost Origin", "186/196", "Alt Art Secret"),
    ("Mew", "Southern Islands", "53", "Holo Rare"),
    ("Charizard ex", "Obsidian Flames", "223/197", "Special Illustration"),
    ("Moonbreon Umbreon VMAX", "Evolving Skies", "215/203", "Alt Art Secret"),
]

POKEMON = [
    "Charizard", "Blastoise", "Venusaur", "Pikachu", "Mewtwo", "Mew", "Lugia",
    "Ho-Oh", "Rayquaza", "Gyarados", "Dragonite", "Gengar", "Umbreon", "Espeon",
    "Sylveon", "Snorlax", "Eevee", "Gardevoir", "Lucario", "Greninja", "Zapdos",
    "Moltres", "Articuno", "Alakazam", "Machamp", "Tyranitar", "Metagross",
    "Garchomp", "Darkrai", "Arceus", "Giratina", "Dialga", "Palkia", "Reshiram",
    "Zekrom", "Kyurem", "Xerneas", "Yveltal", "Zacian", "Zamazenta", "Cinderace",
    "Pidgeot", "Nidoking", "Raichu", "Vaporeon", "Jolteon", "Flareon", "Leafeon",
    "Glaceon", "Ninetales", "Arcanine", "Lapras", "Ampharos", "Feraligatr",
]

SETS = [
    "Base Set", "Jungle", "Fossil", "Team Rocket", "Gym Heroes", "Neo Genesis",
    "Neo Destiny", "Expedition", "Skyridge", "Aquapolis", "EX Dragon",
    "Evolving Skies", "Lost Origin", "Silver Tempest", "Crown Zenith",
    "Obsidian Flames", "Paldea Evolved", "Scarlet & Violet", "151",
    "Champion's Path", "Hidden Fates", "Shining Fates", "Celebrations",
    "Chilling Reign", "Fusion Strike", "Brilliant Stars", "Astral Radiance",
]

RARITIES = [
    "Holo Rare", "Ultra Rare", "Secret Rare", "Alt Art Secret",
    "Special Illustration", "Full Art", "Rainbow Rare", "Gold Secret",
]


def synthesize_cards(n):
    cards = []
    # Top real-ish cards, priced high and descending.
    top_price = 4200.0
    for i, (name, set_name, number, rarity) in enumerate(TOP_CARDS):
        price = top_price * (0.9 ** i) * random.uniform(0.9, 1.1)
        cards.append((name, set_name, number, rarity, price))
    # Fill the rest with a smooth power-law decline down to ~$40.
    remaining = n - len(cards)
    for i in range(remaining):
        frac = i / max(remaining - 1, 1)
        price = 900.0 * math.exp(-3.1 * frac) * random.uniform(0.75, 1.25) + 38.0
        name = random.choice(POKEMON)
        set_name = random.choice(SETS)
        number = f"{random.randint(1, 250)}"
        rarity = random.choice(RARITIES)
        cards.append((name, set_name, number, rarity, price))
    cards.sort(key=lambda c: c[4], reverse=True)
    return cards


def build():
    n = 500
    cards = synthesize_cards(n)
    constituents = []
    advancing = declining = unchanged = 0
    for rank, (name, set_name, number, rarity, price) in enumerate(cards, start=1):
        change_pct = round(random.gauss(0.4, 3.2), 2)  # mild upward bias
        prev_price = round(price / (1 + change_pct / 100), 2)
        if change_pct > 0:
            advancing += 1
        elif change_pct < 0:
            declining += 1
        else:
            unchanged += 1
        constituents.append(
            {
                "rank": rank,
                "id": f"sample-{rank}",
                "name": name,
                "number": number,
                "rarity": rarity,
                "setName": set_name,
                "setId": "",
                "image": "",
                "price": round(price, 2),
                "prevPrice": prev_price,
                "changePct": change_pct,
                "isNew": False,
            }
        )

    total_value = round(sum(c["price"] for c in constituents), 2)
    index_value = 1000.0 * total_value / total_value  # base anchor for sample

    movable = sorted(constituents, key=lambda c: c["changePct"], reverse=True)
    fields = ("id", "name", "image", "setName", "price", "prevPrice", "changePct")
    gainers = [{k: c[k] for k in fields} for c in movable[:8]]
    losers = [{k: c[k] for k in fields} for c in reversed(movable[-8:])]

    now = datetime.now(timezone.utc)

    # Synthetic history: ~140 days, gentle uptrend + realistic volatility, then a
    # little chop near the top (so the "is this the peak?" story is visible).
    points = []
    value = 820.0
    start = now - timedelta(days=139)
    for d in range(140):
        drift = 0.0016 if d < 110 else -0.0003  # rally then flatten/roll over
        value *= 1 + drift + random.gauss(0, 0.011)
        day = start + timedelta(days=d)
        points.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "index": round(value, 2),
                "totalValue": round(value * total_value / 1000.0, 2),
                "count": n,
            }
        )
    index_value = points[-1]["index"]
    prev_index = points[-2]["index"]

    latest = {
        "sample": True,
        "generated": now.isoformat(),
        "asOfDate": now.strftime("%Y-%m-%d"),
        "index": index_value,
        "prevIndex": prev_index,
        "change": round(index_value - prev_index, 2),
        "changePct": round((index_value / prev_index - 1) * 100, 2),
        "divisor": round(total_value / index_value, 4),
        "baseValue": 1000.0,
        "constituentCount": n,
        "totalValue": total_value,
        "breadth": {"advancing": advancing, "declining": declining, "unchanged": unchanged},
        "gainers": gainers,
        "losers": losers,
        "constituents": constituents,
    }
    history = {"sample": True, "generated": now.isoformat(), "points": points}

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "latest.json"), "w", encoding="utf-8") as handle:
        json.dump(latest, handle, indent=2)
    with open(os.path.join(DATA_DIR, "history.json"), "w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)
    print(f"Wrote SAMPLE data: index {index_value}, {n} cards, {len(points)} history points")


if __name__ == "__main__":
    build()
