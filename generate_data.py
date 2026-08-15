"""
Generates a realistic synthetic video-game-sales dataset (data/vgsales.csv)
modeled on the structure & statistical patterns of the well-known Kaggle
"Video Game Sales" dataset (Rank, Name, Platform, Year, Genre, Publisher,
NA_Sales, EU_Sales, JP_Sales, Other_Sales, Global_Sales).

Run once: python generate_data.py
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N = 6500  # number of game entries

platforms = ["PS2", "X360", "PS3", "Wii", "DS", "PS4", "PC", "PSP", "XB",
             "GBA", "3DS", "PS", "PSV", "SNES", "N64", "GC", "XOne", "Switch",
             "WiiU", "GB"]

platform_era = {  # rough launch year to keep years plausible per platform
    "PS": 1996, "N64": 1996, "GB": 1996, "SNES": 1994, "GBA": 2001,
    "PS2": 2000, "XB": 2001, "GC": 2001, "DS": 2004, "PSP": 2004,
    "X360": 2005, "PS3": 2006, "Wii": 2006, "PSV": 2011, "WiiU": 2012,
    "PS4": 2013, "XOne": 2013, "3DS": 2011, "PC": 1995, "Switch": 2017,
}
platform_end = {p: min(platform_era[p] + rng.integers(8, 14), 2020) for p in platforms}

genres = ["Action", "Sports", "Shooter", "Role-Playing", "Platform", "Misc",
          "Racing", "Fighting", "Simulation", "Puzzle", "Adventure", "Strategy"]

publishers = ["Nintendo", "Electronic Arts", "Activision", "Sony Computer Entertainment",
              "Ubisoft", "Take-Two Interactive", "THQ", "Konami Digital Entertainment",
              "Sega", "Namco Bandai Games", "Microsoft Game Studios", "Capcom",
              "Square Enix", "Warner Bros. Interactive", "Atari", "Bethesda Softworks",
              "2K Games", "Disney Interactive Studios", "Epic Games", "CD Projekt"]

# Publisher-genre affinity (some publishers lean toward certain genres)
publisher_genre_bias = {
    "Nintendo": ["Platform", "Action", "Role-Playing", "Sports", "Puzzle"],
    "Electronic Arts": ["Sports", "Racing", "Shooter", "Simulation"],
    "Activision": ["Shooter", "Action", "Fighting"],
    "Square Enix": ["Role-Playing", "Adventure"],
    "Konami Digital Entertainment": ["Sports", "Fighting", "Action"],
    "Bethesda Softworks": ["Role-Playing", "Action", "Adventure"],
    "CD Projekt": ["Role-Playing", "Adventure"],
}

name_prefixes = ["Legend of", "Chronicles of", "Call of", "World of", "Rise of",
                 "Shadow of", "Battle for", "Tales of", "Kingdom of", "Age of",
                 "Realm of", "Saga of", "Quest for", "Empire of", "Fall of"]
name_nouns = ["Duty", "Valor", "Honor", "Destiny", "Legends", "Warriors", "Heroes",
              "Champions", "Titans", "Dragons", "Shadows", "Storm", "Fury", "Glory",
              "Empires", "Frontier", "Odyssey", "Rebellion", "Conquest", "Nations",
              "Racing Stars", "Gridiron", "Fairways", "Arena", "Skies", "Depths"]
name_suffixes = ["", "", "", " II", " III", " 2", " 3", ": Reborn", ": Origins",
                  ": Revolution", ": Remastered", " Gold Edition", ": Next Gen"]

def make_name():
    if rng.random() < 0.55:
        return f"{rng.choice(name_prefixes)} {rng.choice(name_nouns)}{rng.choice(name_suffixes)}"
    else:
        return f"{rng.choice(name_nouns)} {rng.choice(name_nouns)}{rng.choice(name_suffixes)}"

rows = []
for i in range(N):
    platform = rng.choice(platforms)
    lo, hi = platform_era[platform], platform_end[platform]
    year = int(rng.integers(lo, hi + 1))

    publisher = rng.choice(publishers)
    if publisher in publisher_genre_bias and rng.random() < 0.6:
        genre = rng.choice(publisher_genre_bias[publisher])
    else:
        genre = rng.choice(genres)

    name = make_name()

    # Base popularity follows a heavy-tailed (power law-ish) distribution,
    # like real sales data: most games sell little, a few are blockbusters.
    base = rng.pareto(a=1.8) * 0.15 + 0.01

    # Platform popularity multiplier (some platforms had bigger install bases)
    platform_mult = {
        "PS2": 1.6, "X360": 1.3, "PS3": 1.3, "Wii": 1.5, "DS": 1.4, "PS4": 1.2,
        "PC": 1.0, "Switch": 1.2, "GBA": 1.0, "PSP": 0.9, "3DS": 1.0
    }.get(platform, 0.8)

    # Genre popularity multiplier
    genre_mult = {
        "Action": 1.3, "Sports": 1.25, "Shooter": 1.3, "Platform": 1.1,
        "Racing": 1.0, "Role-Playing": 1.1, "Misc": 0.9, "Fighting": 0.85,
        "Simulation": 0.8, "Puzzle": 0.7, "Adventure": 0.85, "Strategy": 0.75
    }[genre]

    global_sales = round(base * platform_mult * genre_mult, 2)
    global_sales = max(global_sales, 0.01)

    # Regional split varies by genre (JP loves RPGs, NA/EU love Shooters/Sports)
    if genre == "Role-Playing":
        region_weights = np.array([0.28, 0.22, 0.40, 0.10])
    elif genre in ["Shooter", "Sports", "Racing"]:
        region_weights = np.array([0.50, 0.30, 0.05, 0.15])
    else:
        region_weights = np.array([0.42, 0.30, 0.15, 0.13])

    noise = rng.dirichlet(region_weights * 20)
    na, eu, jp, other = np.round(noise * global_sales, 2)
    # fix rounding drift so components sum ~= global
    diff = round(global_sales - (na + eu + jp + other), 2)
    na = max(round(na + diff, 2), 0.0)

    rows.append({
        "Rank": i + 1,
        "Name": name,
        "Platform": platform,
        "Year": year,
        "Genre": genre,
        "Publisher": publisher,
        "NA_Sales": na,
        "EU_Sales": eu,
        "JP_Sales": jp,
        "Other_Sales": other,
        "Global_Sales": round(na + eu + jp + other, 2),
    })

df = pd.DataFrame(rows)
df = df.sort_values("Global_Sales", ascending=False).reset_index(drop=True)
df["Rank"] = df.index + 1

# introduce a small % of realistic missing values (like the real dataset does)
missing_idx = rng.choice(df.index, size=int(N * 0.015), replace=False)
df.loc[missing_idx, "Year"] = np.nan
missing_idx2 = rng.choice(df.index, size=int(N * 0.01), replace=False)
df.loc[missing_idx2, "Publisher"] = np.nan

import os
os.makedirs("data", exist_ok=True)
df.to_csv("data/vgsales.csv", index=False)
print("Saved data/vgsales.csv with", len(df), "rows")
print(df.head())
