import io
import json
import time
import urllib.request
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Allow huge master scans

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "artworks.json"
MASTERS_DIR = BASE_DIR / "static" / "img" / "masters"
MASTERS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "ClassicArtArchive/2.2 (https://classicartarchive.org; contact: contact@classicartarchive.com)"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    artworks = json.load(f)

print(f"Starting master downloads for {len(artworks)} artworks...")

headers = {
    "User-Agent": USER_AGENT,
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
}

for i, artwork in enumerate(artworks, start=1):
    slug = artwork["slug"]
    url = artwork["image_url"]
    out_file = MASTERS_DIR / f"{slug}.jpg"
    
    print(f"\n[{i}/{len(artworks)}] Processing {artwork['title']} ({slug})...")
    
    if out_file.exists() and out_file.stat().st_size > 1_000_000:
        try:
            with Image.open(out_file) as im:
                w, h = im.size
                mb = out_file.stat().st_size / (1024 * 1024)
                print(f"  -> Already cached: {w}x{h} px ({mb:.2f} MB)")
                artwork["real_resolution"] = f"{w} × {h} px"
                artwork["real_file_size"] = f"{mb:.1f} MB"
                continue
        except Exception:
            pass

    # Download from URL
    retries = 3
    success = False
    for attempt in range(retries):
        try:
            time.sleep(1.5)  # Be polite to Wikimedia servers
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as response:
                content = response.read()
                print(f"  -> Downloaded raw data: {len(content) / (1024*1024):.2f} MB")
                
                # Open with PIL
                img = Image.open(io.BytesIO(content))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                w, h = img.size
                print(f"  -> Raw dimensions: {w} × {h} px")
                
                # If image is excessively giant (>8000px), scale gently down to 6000px max edge to keep file around 10-25MB
                # If it's already under 8000px, save at full 100% resolution with quality=95
                max_edge = 6000
                if max(w, h) > max_edge:
                    ratio = max_edge / max(w, h)
                    new_w = int(w * ratio)
                    new_h = int(h * ratio)
                    print(f"  -> Resizing master to Ultra HD {new_w} × {new_h} px for optimal high-res viewing/export...")
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                img.save(out_file, "JPEG", quality=95, optimize=True)
                final_size = out_file.stat().st_size / (1024 * 1024)
                final_w, final_h = img.size
                print(f"  -> Saved master: {final_w} × {final_h} px ({final_size:.2f} MB)")
                
                artwork["real_resolution"] = f"{final_w} × {final_h} px"
                artwork["real_file_size"] = f"{final_size:.1f} MB"
                success = True
                break
        except Exception as e:
            print(f"  -> Attempt {attempt+1} failed: {e}")
            time.sleep(3)

    if not success:
        # Fallback to local preview if download completely fails
        fallback_file = BASE_DIR / "static" / "img" / "artworks" / f"{slug}.jpg"
        if fallback_file.exists() and not out_file.exists():
            import shutil
            shutil.copyfile(fallback_file, out_file)
            print(f"  -> Copied preview fallback for {slug}")

# Save updated metadata
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(artworks, f, indent=2, ensure_ascii=False)

print("\nDone downloading and updating all master artworks!")
