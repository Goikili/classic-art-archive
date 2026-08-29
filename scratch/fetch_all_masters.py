import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "artworks.json"
MASTERS_DIR = BASE_DIR / "static" / "img" / "masters"
ARTWORKS_DIR = BASE_DIR / "static" / "img" / "artworks"
MASTERS_DIR.mkdir(parents=True, exist_ok=True)
ARTWORKS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "ClassicArtArchiveBot/2.2 (https://classicartarchive.org; contact: contact@classicartarchive.com)"
HEADERS = {"User-Agent": USER_AGENT}

with open(DATA_FILE, "r", encoding="utf-8") as f:
    artworks = json.load(f)


def get_wikimedia_highres_url(image_url: str) -> str:
    """Extract File name from upload.wikimedia.org URL and query API for 4096px+ render or original."""
    parsed = urllib.parse.urlparse(image_url)
    filename = parsed.path.split("/")[-1]
    filename_unquoted = urllib.parse.unquote(filename)
    
    api_url = (
        f"https://commons.wikimedia.org/w/api.php?action=query"
        f"&titles=File:{urllib.parse.quote(filename_unquoted)}"
        f"&prop=imageinfo&iiprop=url|size&iiurlwidth=4096&format=json"
    )
    
    req = urllib.request.Request(api_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
        pages = data.get("query", {}).get("pages", {})
        if pages:
            first_page = list(pages.values())[0]
            imageinfo = first_page.get("imageinfo", [])
            if imageinfo:
                info = imageinfo[0]
                # If thumburl exists and is 4K/high-res, use it; otherwise fallback to original url
                thumb_url = info.get("thumburl")
                orig_url = info.get("url")
                orig_size = info.get("size", 0)
                
                # If original is small (<35MB), original is great; if gigantic, thumburl is fast & high-res
                if orig_size < 35_000_000 and orig_url:
                    return orig_url
                if thumb_url:
                    return thumb_url
                return orig_url or image_url
    return image_url


for i, artwork in enumerate(artworks, 1):
    slug = artwork["slug"]
    master_file = MASTERS_DIR / f"{slug}.jpg"
    thumb_file = ARTWORKS_DIR / f"{slug}.jpg"
    
    print(f"\n[{i}/{len(artworks)}] Processing '{artwork['title']}' ({slug})...", flush=True)
    
    # Check if master is already present and > 2MB
    if master_file.exists() and master_file.stat().st_size > 2_000_000:
        try:
            with Image.open(master_file) as im:
                w, h = im.size
                mb = master_file.stat().st_size / (1024 * 1024)
                print(f"  -> Already cached master: {w} × {h} px ({mb:.1f} MB)", flush=True)
                artwork["resolution"] = f"{w:,} × {h:,} px".replace(",", " ")
                artwork["file_size"] = f"{mb:.1f} MB"
                continue
        except Exception:
            pass

    # Find best high-res download URL
    orig_url = artwork["image_url"]
    download_url = orig_url
    try:
        if "upload.wikimedia.org" in orig_url:
            download_url = get_wikimedia_highres_url(orig_url)
            print(f"  -> Resolved high-res URL: {download_url[:90]}...", flush=True)
    except Exception as e:
        print(f"  -> API resolution warning ({e}), falling back to direct URL", flush=True)
        download_url = orig_url

    # Download
    download_success = False
    for attempt in range(3):
        try:
            time.sleep(1.0)
            req = urllib.request.Request(download_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
                print(f"  -> Downloaded {len(content) / (1024*1024):.2f} MB", flush=True)
                
                img = Image.open(io.BytesIO(content))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                w, h = img.size
                print(f"  -> Original size: {w} × {h} px", flush=True)
                
                # If excessively large (>6000px on longest side), downsample with lanczos to 5000px
                max_side = 5000
                if max(w, h) > max_side:
                    ratio = max_side / max(w, h)
                    img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
                
                # Save Ultra HD Master
                img.save(master_file, "JPEG", quality=95, optimize=True)
                master_mb = master_file.stat().st_size / (1024 * 1024)
                final_w, final_h = img.size
                print(f"  -> Saved Master: {final_w} × {final_h} px ({master_mb:.1f} MB)", flush=True)
                
                # Also save high-quality web preview (1600px)
                web_max = 1600
                if max(final_w, final_h) > web_max:
                    ratio_web = web_max / max(final_w, final_h)
                    web_img = img.resize((int(final_w * ratio_web), int(final_h * ratio_web)), Image.Resampling.LANCZOS)
                    web_img.save(thumb_file, "JPEG", quality=88, optimize=True)
                else:
                    img.save(thumb_file, "JPEG", quality=88, optimize=True)
                
                artwork["resolution"] = f"{final_w:,} × {final_h:,} px".replace(",", " ")
                artwork["file_size"] = f"{master_mb:.1f} MB"
                download_success = True
                break
        except Exception as e:
            print(f"  -> Attempt {attempt+1} error: {e}", flush=True)
            time.sleep(2)
            
    if not download_success and not master_file.exists():
        if thumb_file.exists():
            import shutil
            shutil.copyfile(thumb_file, master_file)
            print(f"  -> Copied thumb fallback for {slug}", flush=True)

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(artworks, f, indent=2, ensure_ascii=False)

print("\nAll master scans downloaded and metadata updated successfully!", flush=True)
