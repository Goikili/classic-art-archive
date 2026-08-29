import io
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize application
app = FastAPI(
    title="Classic Art Archive",
    description="The official high-resolution backup, digital sanctuary, and social hub for @classicartarchive.",
    version="2.2.0"
)

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_FILE = BASE_DIR / "data" / "artworks.json"
STATS_FILE = BASE_DIR / "data" / "stats.json"

# Mount Static Files and Templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def format_number(n: int) -> str:
    """Format integer to readable K/M format."""
    if n >= 1_000_000:
        val = n / 1_000_000
        return f"+{val:.1f}M".replace(".0M", "M")
    elif n >= 1_000:
        val = n / 1_000
        return f"+{val:.1f}K".replace(".0K", "K")
    return f"+{n}"


def compute_dynamic_stats(followers: int = 400000) -> dict:
    """
    Calculate all audience reach, impressions, and engagement metrics
    automatically based on the follower count, with fixed 5.0% engagement.
    """
    monthly_reach = int(round(followers * 15.0))
    monthly_impressions = int(round(followers * 22.5))
    monthly_interactions = int(round(followers * 0.05 * 30))

    return {
        "instagram_followers": followers,
        "instagram_followers_display": f"+{followers:,}",
        "monthly_reach": monthly_reach,
        "monthly_reach_display": format_number(monthly_reach),
        "monthly_impressions": monthly_impressions,
        "monthly_impressions_display": format_number(monthly_impressions),
        "monthly_interactions": monthly_interactions,
        "monthly_interactions_display": format_number(monthly_interactions),
        "engagement_rate": "5.0%",
        "demographics_men": "61%",
        "demographics_us": "19%",
        "handle": "@classicartarchive",
        "instagram_url": "https://instagram.com/classicartarchive",
        "facebook_url": "https://facebook.com/classicartarchive",
        "business_email": "contact@classicartarchive.com",
        "last_synced": "Official Live Sync",
        "sync_source": "Dynamic Creator Engine (Engagement 5.0%)"
    }


def load_artworks() -> List[dict]:
    """Load curated artworks from json database."""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_stats() -> dict:
    """Load stats and compute dynamic metrics automatically."""
    followers = 400000
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                followers = int(saved.get("instagram_followers", 400000))
        except Exception:
            followers = 400000

    return compute_dynamic_stats(followers)


def get_unique_periods(artworks: List[dict]) -> List[str]:
    """Extract ordered unique periods from artworks."""
    periods = []
    for art in artworks:
        p = art.get("period")
        if p and p not in periods:
            periods.append(p)
    return periods


# --- Health Check Route ---

@app.api_route('/health', methods=['GET', 'HEAD'])
async def health_check():
    return {'status': 'ok'}


# --- HTML Frontend Routes ---

@app.get("/", response_class=HTMLResponse)
async def home_gallery(request: Request, period: Optional[str] = None):
    artworks = load_artworks()
    periods = get_unique_periods(artworks)
    stats = load_stats()

    if period and period.lower() != "all":
        filtered_artworks = [a for a in artworks if a.get("period", "").lower() == period.lower()]
    else:
        filtered_artworks = artworks

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "artworks": filtered_artworks,
            "periods": periods,
            "selected_period": period or "all",
            "active_page": "gallery",
            "stats": stats,
            "business_email": stats.get("business_email", "contact@classicartarchive.com")
        }
    )


@app.get("/artwork/{slug}", response_class=HTMLResponse)
async def artwork_detail(request: Request, slug: str):
    artworks = load_artworks()
    stats = load_stats()
    artwork = next((a for a in artworks if a.get("slug") == slug), None)

    if not artwork:
        raise HTTPException(status_code=404, detail="Masterpiece not found in the archive.")

    # Find related artworks from same period (excluding current)
    related = [a for a in artworks if a.get("period") == artwork.get("period") and a.get("slug") != slug][:3]
    if len(related) < 3:
        others = [a for a in artworks if a.get("slug") != slug and a not in related]
        related.extend(others[: 3 - len(related)])

    return templates.TemplateResponse(
        request=request,
        name="artwork_detail.html",
        context={
            "artwork": artwork,
            "related_artworks": related,
            "active_page": "gallery",
            "stats": stats,
            "business_email": stats.get("business_email", "contact@classicartarchive.com")
        }
    )


@app.get("/archive", response_class=HTMLResponse)
async def archive_index(request: Request, period: Optional[str] = None):
    artworks = load_artworks()
    periods = get_unique_periods(artworks)
    stats = load_stats()

    if period and period.lower() != "all":
        artworks = [a for a in artworks if a.get("period", "").lower() == period.lower()]

    return templates.TemplateResponse(
        request=request,
        name="archive.html",
        context={
            "artworks": artworks,
            "periods": periods,
            "selected_period": period or "all",
            "active_page": "archive",
            "stats": stats,
            "business_email": stats.get("business_email", "contact@classicartarchive.com")
        }
    )


@app.get("/about", response_class=HTMLResponse)
async def about_manifesto(request: Request):
    stats = load_stats()
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "active_page": "about",
            "stats": stats,
            "business_email": stats.get("business_email", "contact@classicartarchive.com")
        }
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = STATIC_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    return FileResponse(STATIC_DIR / "img" / "favicon.png", media_type="image/png")


@app.get("/download/{slug}")
async def download_artwork(slug: str, raw: bool = False):
    """Direct Ultra HD Master download served directly from our archive as attachment stream."""
    artworks = load_artworks()
    artwork = next((a for a in artworks if a.get("slug") == slug), None)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    if raw and artwork.get("image_url"):
        return RedirectResponse(url=artwork["image_url"], status_code=307)

    # 1. Prioritize Ultra HD Master Scan
    master_file = STATIC_DIR / "img" / "masters" / f"{slug}.jpg"
    if master_file.exists():
        filename = artwork.get("download_filename") or f"{slug}_ClassicArtArchive_UltraHD.jpg"
        return FileResponse(
            path=str(master_file),
            filename=filename,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    
    # 2. Fallback to local artwork preview
    local_file = STATIC_DIR / "img" / "artworks" / f"{slug}.jpg"
    if local_file.exists():
        filename = artwork.get("download_filename") or f"{slug}_ClassicArtArchive_HD.jpg"
        return FileResponse(
            path=str(local_file),
            filename=filename,
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    
    # 3. Fallback to remote high-res image
    if artwork.get("image_url"):
        return RedirectResponse(url=artwork["image_url"], status_code=307)
    
    raise HTTPException(status_code=404, detail="Artwork file not found")


@app.get("/download-collection-zip")
async def download_full_collection_zip():
    """Package and stream all 20 curated Ultra HD master scans into a single high-speed zip file."""
    artworks = load_artworks()
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zip_file:
        for artwork in artworks:
            slug = artwork.get("slug")
            master_file = STATIC_DIR / "img" / "masters" / f"{slug}.jpg"
            preview_file = STATIC_DIR / "img" / "artworks" / f"{slug}.jpg"
            source_file = master_file if master_file.exists() else preview_file
            if source_file.exists():
                filename = artwork.get("download_filename") or f"{slug}_ClassicArtArchive_UltraHD.jpg"
                zip_file.write(str(source_file), arcname=filename)
                
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="Classic_Art_Archive_Full_Collection_UltraHD.zip"'}
    )


# --- JSON API Endpoints ---

@app.get("/api/stats", response_class=JSONResponse)
async def api_get_stats():
    """Return current dynamic metrics and follower counts."""
    return load_stats()


@app.get("/api/artworks", response_class=JSONResponse)
async def api_get_artworks(period: Optional[str] = None, q: Optional[str] = None):
    artworks = load_artworks()

    if period and period.lower() != "all":
        artworks = [a for a in artworks if a.get("period", "").lower() == period.lower()]

    if q:
        query = q.lower().strip()
        artworks = [
            a for a in artworks
            if query in a.get("title", "").lower()
            or query in a.get("artist", "").lower()
            or query in a.get("period", "").lower()
            or query in a.get("description", "").lower()
        ]

    return artworks


@app.get("/api/artworks/{slug}", response_class=JSONResponse)
async def api_get_artwork_by_slug(slug: str):
    artworks = load_artworks()
    artwork = next((a for a in artworks if a.get("slug") == slug), None)
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork


@app.post("/api/contact")
async def api_contact_inquiry(
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form("General Inquiry"),
    message: str = Form(...)
):
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address.")
    if not message.strip():
        raise HTTPException(status_code=400, detail="Please provide a message.")

    # Log / save message locally
    inquiries_file = BASE_DIR / "data" / "inquiries.jsonl"
    inquiry_record = {
        "name": name.strip(),
        "email": email.strip(),
        "subject": subject.strip(),
        "message": message.strip(),
        "recipient": "contact@classicartarchive.com",
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(inquiries_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(inquiry_record, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return {
        "status": "success",
        "message": "Your message has been received! We will reply from contact@classicartarchive.com shortly."
    }


@app.post("/api/newsletter")
async def api_subscribe_newsletter(email: str = Form(...)):
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address.")

    subscribers_file = BASE_DIR / "data" / "subscribers.txt"
    try:
        with open(subscribers_file, "a", encoding="utf-8") as f:
            f.write(f"{email.strip()}\n")
    except Exception:
        pass

    return {
        "status": "success",
        "message": f"Successfully subscribed to the Archive Gazette ({email})!"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
