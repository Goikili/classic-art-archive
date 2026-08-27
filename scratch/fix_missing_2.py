import io
import json
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

missing_targets = [
    {
        "slug": "lady-with-an-ermine",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Lady_with_an_Ermine_-_Leonardo_da_Vinci_-_Google_Art_Project.jpg/3840px-Lady_with_an_Ermine_-_Leonardo_da_Vinci_-_Google_Art_Project.jpg"
    },
    {
        "slug": "cafe-terrace-at-night",
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/21/Vincent_Willem_van_Gogh_-_Cafe_Terrace_at_Night_%28Yorck%29.jpg"
    }
]

with open(DATA_FILE, "r", encoding="utf-8") as f:
    artworks = json.load(f)

for item in missing_targets:
    slug = item["slug"]
    url = item["url"]
    master_file = MASTERS_DIR / f"{slug}.jpg"
    thumb_file = ARTWORKS_DIR / f"{slug}.jpg"
    
    print(f"Downloading {slug} from {url}...")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    w, h = img.size
    max_side = 5000
    if max(w, h) > max_side:
        ratio = max_side / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        
    img.save(master_file, "JPEG", quality=95, optimize=True)
    master_mb = master_file.stat().st_size / (1024 * 1024)
    final_w, final_h = img.size
    
    web_max = 1600
    if max(final_w, final_h) > web_max:
        ratio_web = web_max / max(final_w, final_h)
        web_img = img.resize((int(final_w * ratio_web), int(final_h * ratio_web)), Image.Resampling.LANCZOS)
        web_img.save(thumb_file, "JPEG", quality=88, optimize=True)
    else:
        img.save(thumb_file, "JPEG", quality=88, optimize=True)
        
    for a in artworks:
        if a["slug"] == slug:
            a["resolution"] = f"{final_w:,} × {final_h:,} px".replace(",", " ")
            a["file_size"] = f"{master_mb:.1f} MB"
            a["image_url"] = url
            break
            
    print(f"Saved {slug} successfully: {final_w}x{final_h}, {master_mb:.1f} MB")

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(artworks, f, indent=2, ensure_ascii=False)

print("Done updating all 30 artworks!")
