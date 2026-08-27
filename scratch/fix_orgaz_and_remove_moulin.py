import io
import json
import os
import urllib.request
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "artworks.json"
MASTERS_DIR = BASE_DIR / "static" / "img" / "masters"
ARTWORKS_DIR = BASE_DIR / "static" / "img" / "artworks"

USER_AGENT = "ClassicArtArchiveBot/2.2 (https://classicartarchive.org; contact: artarchivebusiness@gmail.com)"
HEADERS = {"User-Agent": USER_AGENT}

# 1. Remove at-the-moulin-rouge
moulin_slug = "at-the-moulin-rouge"
moulin_master = MASTERS_DIR / f"{moulin_slug}.jpg"
moulin_thumb = ARTWORKS_DIR / f"{moulin_slug}.jpg"

if moulin_master.exists():
    os.remove(moulin_master)
    print(f"Removed {moulin_master}")
if moulin_thumb.exists():
    os.remove(moulin_thumb)
    print(f"Removed {moulin_thumb}")

# 2. Download authentic El entierro del señor de Orgaz
orgaz_url = "https://upload.wikimedia.org/wikipedia/commons/3/37/El_entierro_del_se%C3%B1or_de_Orgaz_-_El_Greco.jpg"
orgaz_slug = "the-burial-of-the-count-of-orgaz"
orgaz_master = MASTERS_DIR / f"{orgaz_slug}.jpg"
orgaz_thumb = ARTWORKS_DIR / f"{orgaz_slug}.jpg"

print(f"Downloading authentic master for {orgaz_slug} from {orgaz_url}...")
req = urllib.request.Request(orgaz_url, headers=HEADERS)
with urllib.request.urlopen(req, timeout=90) as resp:
    data = resp.read()

print(f"Downloaded {len(data)/(1024*1024):.2f} MB")
img = Image.open(io.BytesIO(data))
if img.mode in ("RGBA", "P"):
    img = img.convert("RGB")

w, h = img.size
max_side = 5000
if max(w, h) > max_side:
    ratio = max_side / max(w, h)
    img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

img.save(orgaz_master, "JPEG", quality=94, optimize=True)
master_mb = orgaz_master.stat().st_size / (1024 * 1024)
final_w, final_h = img.size

web_max = 1600
if max(final_h, final_w) > web_max:
    ratio_web = web_max / max(final_h, final_w)
    web_img = img.resize((int(final_w * ratio_web), int(final_h * ratio_web)), Image.Resampling.LANCZOS)
    web_img.save(orgaz_thumb, "JPEG", quality=88, optimize=True)
else:
    img.save(orgaz_thumb, "JPEG", quality=88, optimize=True)

print(f"Saved authentic Orgaz master ({final_w}x{final_h}, {master_mb:.1f} MB) and thumbnail.")

# 3. Update artworks.json
with open(DATA_FILE, "r", encoding="utf-8") as f:
    artworks = json.load(f)

# Filter out moulin rouge
artworks = [a for a in artworks if a["slug"] != moulin_slug]

# Update Orgaz data
for a in artworks:
    if a["slug"] == orgaz_slug:
        a["title"] = "The Burial of the Count of Orgaz"
        a["original_title"] = "El entierro del señor de Orgaz"
        a["artist"] = "El Greco"
        a["year"] = "1586–1588"
        a["period"] = "Mannerism"
        a["medium"] = "Oil on canvas"
        a["dimensions"] = "480 cm × 360 cm"
        a["location"] = "Iglesia de Santo Tomé, Toledo, Spain"
        a["image_url"] = orgaz_url
        a["resolution"] = f"{final_w:,} × {final_h:,} px".replace(",", " ")
        a["file_size"] = f"{master_mb:.1f} MB"
        a["description"] = "El Greco's supreme monumental altarpiece in the Church of Santo Tomé in Toledo, illustrating the miraculous burial of Don Gonzalo Ruiz by Saint Stephen and Saint Augustine beneath the celestial glory of Christ, the Virgin Mary, and Saint John the Baptist."
        a["analysis"] = "A towering masterpiece of Mannerist spirituality and theological depth, dividing the canvas between the stark terrestrial grief of Toledo's nobility and the luminous celestial realm above."
        break

# Re-index ids 1..N
for i, a in enumerate(artworks, 1):
    a["id"] = i

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(artworks, f, indent=2, ensure_ascii=False)

print(f"Database successfully updated. Total artworks: {len(artworks)}")
