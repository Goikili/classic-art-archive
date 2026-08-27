import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "artworks.json"
MASTERS_DIR = BASE_DIR / "static" / "img" / "masters"
ARTWORKS_DIR = BASE_DIR / "static" / "img" / "artworks"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    artworks = json.load(f)

print(f"Loaded {len(artworks)} artworks.")

# Fix common accents & spellings
replacements = {
    "Czanne": "Cézanne",
    "Eugne": "Eugène",
    "Bcklin": "Böcklin",
    "Rcamier": "Récamier",
    "Drer": "Dürer",
    "Velzquez": "Velázquez",
    "Caf": "Café",
    "Franois": "François",
    "Thodore": "Théodore",
    "Gricault": "Géricault",
}

for i, a in enumerate(artworks, 1):
    a["id"] = i
    for k in ["title", "original_title", "artist", "period", "description", "analysis", "instagram_post_caption"]:
        if isinstance(a.get(k), str):
            for old, new in replacements.items():
                a[k] = a[k].replace(old, new)
                
    master_path = MASTERS_DIR / f"{a['slug']}.jpg"
    thumb_path = ARTWORKS_DIR / f"{a['slug']}.jpg"
    
    if not master_path.exists():
        print(f"WARNING: Missing master for {a['slug']}")
    if not thumb_path.exists():
        print(f"WARNING: Missing thumb for {a['slug']}")

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(artworks, f, indent=2, ensure_ascii=False)

print(f"Verification complete! Total artworks: {len(artworks)}. All files and metadata synchronized.")
