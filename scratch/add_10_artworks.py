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

USER_AGENT = "ClassicArtArchiveBot/2.2 (https://classicartarchive.org; contact: artarchivebusiness@gmail.com)"
HEADERS = {"User-Agent": USER_AGENT}

new_10_artworks = [
    {
        "id": 21,
        "slug": "the-garden-of-earthly-delights",
        "title": "The Garden of Earthly Delights",
        "original_title": "El jardín de las delicias",
        "artist": "Hieronymus Bosch",
        "year": "c. 1490–1510",
        "period": "Northern Renaissance",
        "medium": "Oil on oak panels",
        "dimensions": "220 cm × 389 cm",
        "location": "Museo del Prado, Madrid, Spain",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/ae/El_jard%C3%ADn_de_las_Delicias%2C_de_El_Bosco.jpg",
        "thumbnail_url": "/static/img/artworks/the-garden-of-earthly-delights.jpg",
        "download_filename": "Bosch_Garden_of_Earthly_Delights_UltraHD.jpg",
        "resolution": "5 000 × 2 813 px",
        "file_size": "8.5 MB",
        "description": "Hieronymus Bosch's monumental triptych depicting Eden, the surreal garden of earthly temptations and pleasures, and the harrowing descent into the eternal torments of Hell.",
        "analysis": "Renowned for its boundless fantastical iconography, hybrid creatures, moral warnings, and visionary surrealism centuries ahead of its time.",
        "featured": True,
        "instagram_post_caption": "Bosch's visionary masterpiece: The Garden of Earthly Delights in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 22,
        "slug": "the-tower-of-babel",
        "title": "The Tower of Babel",
        "original_title": "De Toren van Babel",
        "artist": "Pieter Bruegel the Elder",
        "year": "1563",
        "period": "Northern Renaissance",
        "medium": "Oil on oak panel",
        "dimensions": "114 cm × 155 cm",
        "location": "Kunsthistorisches Museum, Vienna, Austria",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/fc/Pieter_Bruegel_the_Elder_-_The_Tower_of_Babel_%28Vienna%29_-_Google_Art_Project_-_edited.jpg",
        "thumbnail_url": "/static/img/artworks/the-tower-of-babel.jpg",
        "download_filename": "Bruegel_Tower_of_Babel_UltraHD.jpg",
        "resolution": "5 000 × 3 670 px",
        "file_size": "9.2 MB",
        "description": "Bruegel's magnificent rendition of the biblical story of human hubris, depicting the colossal tower rising toward heaven modeled on the Roman Colosseum.",
        "analysis": "Features microscopic architectural precision and thousands of bustling laborers, contrasting mortal ambition with inevitable structural collapse.",
        "featured": False,
        "instagram_post_caption": "Bruegel's Tower of Babel: An epic monument to ambition, architecture, and human folly.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 23,
        "slug": "the-milkmaid",
        "title": "The Milkmaid",
        "original_title": "Het melkmeisje",
        "artist": "Johannes Vermeer",
        "year": "c. 1657–1658",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "45.5 cm × 41 cm",
        "location": "Rijksmuseum, Amsterdam, Netherlands",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg",
        "thumbnail_url": "/static/img/artworks/the-milkmaid.jpg",
        "download_filename": "Vermeer_The_Milkmaid_UltraHD.jpg",
        "resolution": "4 400 × 4 800 px",
        "file_size": "7.8 MB",
        "description": "An intimate domestic scene of a maidservant quietly pouring milk into a stoneware pot in a rustic Dutch kitchen illuminated by cool morning window light.",
        "analysis": "Vermeer achieves breathtaking optical realism through pointillé flecks of light on crusty bread and earthenware, elevating humble labor into timeless serenity.",
        "featured": True,
        "instagram_post_caption": "Vermeer's pure light and everyday tranquility: The Milkmaid archived in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 24,
        "slug": "lady-with-an-ermine",
        "title": "Lady with an Ermine",
        "original_title": "Dama con l'ermellino",
        "artist": "Leonardo da Vinci",
        "year": "c. 1489–1490",
        "period": "High Renaissance",
        "medium": "Oil on walnut board",
        "dimensions": "54 cm × 39 cm",
        "location": "Czartoryski Museum, Kraków, Poland",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Leonardo_da_Vinci_-_Lady_with_an_Ermine_%28Czartoryski_Museum%2C_Krak%C3%B3w%29.jpg",
        "thumbnail_url": "/static/img/artworks/lady-with-an-ermine.jpg",
        "download_filename": "DaVinci_Lady_With_An_Ermine_UltraHD.jpg",
        "resolution": "3 600 × 5 000 px",
        "file_size": "6.9 MB",
        "description": "Portrait of Cecilia Gallerani, the mistress of Ludovico Sforza, Duke of Milan, holding a docile white ermine symbolizing purity and moderation.",
        "analysis": "Pioneered three-quarter dynamic turning posture (contrapposto) and subtle anatomical tension, capturing an instantaneous psychological reaction.",
        "featured": False,
        "instagram_post_caption": "Leonardo da Vinci's portrait perfection: Lady with an Ermine in pristine master scan.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 25,
        "slug": "the-raft-of-the-medusa",
        "title": "The Raft of the Medusa",
        "original_title": "Le Radeau de La Méduse",
        "artist": "Théodore Géricault",
        "year": "1818–1819",
        "period": "Romanticism",
        "medium": "Oil on canvas",
        "dimensions": "491 cm × 716 cm",
        "location": "Musée du Louvre, Paris, France",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/15/JEAN_LOUIS_TH%C3%89ODORE_G%C3%89RICAULT_-_La_Balsa_de_la_Medusa_%28Museo_del_Louvre%2C_1818-19%29.jpg",
        "thumbnail_url": "/static/img/artworks/the-raft-of-the-medusa.jpg",
        "download_filename": "Gericault_Raft_of_the_Medusa_UltraHD.jpg",
        "resolution": "5 000 × 3 430 px",
        "file_size": "8.7 MB",
        "description": "An emotionally searing depiction of the aftermath of the wreck of the French naval frigate Méduse, showing survivors sighting an elusive rescue ship on the horizon.",
        "analysis": "A landmark of French Romanticism utilizing theatrical pyramidal composition, chiaroscuro, and raw human tragedy to challenge political corruption and human endurance.",
        "featured": True,
        "instagram_post_caption": "Géricault's triumph of Romantic drama: The Raft of the Medusa.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 26,
        "slug": "the-third-of-may-1808",
        "title": "The Third of May 1808",
        "original_title": "El tres de mayo de 1808 en Madrid",
        "artist": "Francisco de Goya",
        "year": "1814",
        "period": "Romanticism",
        "medium": "Oil on canvas",
        "dimensions": "268 cm × 347 cm",
        "location": "Museo del Prado, Madrid, Spain",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/fd/El_Tres_de_Mayo%2C_by_Francisco_de_Goya%2C_from_Prado_thin_black_margin.jpg",
        "thumbnail_url": "/static/img/artworks/the-third-of-may-1808.jpg",
        "download_filename": "Goya_The_Third_of_May_1808_UltraHD.jpg",
        "resolution": "5 000 × 3 850 px",
        "file_size": "8.1 MB",
        "description": "Commemorates Spanish resistance to Napoleon's invading armies during the Peninsular War, depicting the brutal execution of Spanish freedom fighters by a faceless French firing squad.",
        "analysis": "Heralded as one of history's first truly modern paintings, shattering heroic battle conventions with visceral terror, stark lantern lighting, and raw anti-war anguish.",
        "featured": False,
        "instagram_post_caption": "Goya's groundbreaking anti-war statement: The Third of May 1808 in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 27,
        "slug": "primavera",
        "title": "Primavera",
        "original_title": "Primavera",
        "artist": "Sandro Botticelli",
        "year": "c. 1482",
        "period": "Renaissance",
        "medium": "Tempera on poplar panel",
        "dimensions": "207 cm × 319 cm",
        "location": "Uffizi Gallery, Florence, Italy",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Botticelli-primavera.jpg",
        "thumbnail_url": "/static/img/artworks/primavera.jpg",
        "download_filename": "Botticelli_Primavera_UltraHD.jpg",
        "resolution": "5 000 × 3 240 px",
        "file_size": "9.4 MB",
        "description": "An opulent mythological celebration of Spring, featuring Venus in an orange grove accompanied by Mercury, the Three Graces, Cupid, Flora, Chloris, and Zephyrus.",
        "analysis": "Contains over 500 cataloged botanical species painted with exquisite precision, symbolizing the flourishing renewal of nature and humanist Florentine culture.",
        "featured": True,
        "instagram_post_caption": "Botticelli's poetic forest of mythology and rebirth: Primavera.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 28,
        "slug": "the-gleaners",
        "title": "The Gleaners",
        "original_title": "Des glaneuses",
        "artist": "Jean-François Millet",
        "year": "1857",
        "period": "Realism",
        "medium": "Oil on canvas",
        "dimensions": "83.5 cm × 110 cm",
        "location": "Musée d'Orsay, Paris, France",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Jean-Fran%C3%A7ois_Millet_-_Gleaners_-_Google_Art_Project_2.jpg",
        "thumbnail_url": "/static/img/artworks/the-gleaners.jpg",
        "download_filename": "Millet_The_Gleaners_UltraHD.jpg",
        "resolution": "5 000 × 3 780 px",
        "file_size": "6.8 MB",
        "description": "Three peasant women stoop in a harvested wheat field to collect leftover stalks under the golden afternoon haze of the French countryside.",
        "analysis": "A cornerstone of Realism that grants monumental dignity to impoverished rural workers, balancing warm earthy palette with quiet social gravitas.",
        "featured": False,
        "instagram_post_caption": "Millet's monument to honest toil and golden rural light: The Gleaners.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 29,
        "slug": "cafe-terrace-at-night",
        "title": "Café Terrace at Night",
        "original_title": "Terrasse du café le soir",
        "artist": "Vincent van Gogh",
        "year": "1888",
        "period": "Post-Impressionism",
        "medium": "Oil on canvas",
        "dimensions": "80.7 cm × 65.3 cm",
        "location": "Kröller-Müller Museum, Otterlo, Netherlands",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/21/Vincent_Willem_van_Gogh_-_Caf%C3%A9_Terrace_at_Night_%28Yorck%29.jpg",
        "thumbnail_url": "/static/img/artworks/cafe-terrace-at-night.jpg",
        "download_filename": "VanGogh_Cafe_Terrace_At_Night_UltraHD.jpg",
        "resolution": "4 000 × 5 000 px",
        "file_size": "7.5 MB",
        "description": "A warmly illuminated café terrace on the Place du Forum in Arles, framed by cobblestone streets and a radiant starry southern night sky.",
        "analysis": "Notable as Van Gogh's first painting featuring a starry sky, executed entirely without black paint using contrasting luminous yellows and deep Prussian blues.",
        "featured": True,
        "instagram_post_caption": "Van Gogh's glowing starlight and vibrant evening colors in Arles.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "id": 30,
        "slug": "the-anatomy-lesson-of-dr-nicolaes-tulp",
        "title": "The Anatomy Lesson of Dr. Nicolaes Tulp",
        "original_title": "De anatomische les van Dr. Nicolaes Tulp",
        "artist": "Rembrandt van Rijn",
        "year": "1632",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "169.5 cm × 216.5 cm",
        "location": "Mauritshuis, The Hague, Netherlands",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Rembrandt_-_The_Anatomy_Lesson_of_Dr_Nicolaes_Tulp.jpg",
        "thumbnail_url": "/static/img/artworks/the-anatomy-lesson-of-dr-nicolaes-tulp.jpg",
        "download_filename": "Rembrandt_Anatomy_Lesson_UltraHD.jpg",
        "resolution": "5 000 × 3 920 px",
        "file_size": "6.7 MB",
        "description": "Dr. Nicolaes Tulp explains the musculature of the human arm to fascinated members of the Amsterdam Guild of Surgeons during a public dissection.",
        "analysis": "Revolutionized group portraiture by substituting static poses with intense psychological drama, kinetic curiosity, and masterful tenebrist illumination.",
        "featured": False,
        "instagram_post_caption": "Rembrandt's Baroque medical breakthrough: The Anatomy Lesson of Dr. Tulp.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    }
]


def get_wikimedia_highres_url(image_url: str) -> str:
    filename = image_url.split("/")[-1]
    filename = urllib.parse.unquote(filename)
    if filename.startswith("File:"):
        filename = filename[5:]
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{urllib.parse.quote(filename)}&prop=imageinfo&iiprop=url|size&iiurlwidth=5000&format=json"
    
    req = urllib.request.Request(api_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        if pages:
            first_page = list(pages.values())[0]
            imageinfo = first_page.get("imageinfo", [])
            if imageinfo:
                info = imageinfo[0]
                thumb_url = info.get("thumburl")
                orig_url = info.get("url")
                orig_size = info.get("size", 0)
                if orig_size < 35_000_000 and orig_url:
                    return orig_url
                if thumb_url:
                    return thumb_url
                return orig_url or image_url
    return image_url


print(f"Downloading and processing {len(new_10_artworks)} public domain artworks...")

for i, artwork in enumerate(new_10_artworks, 1):
    slug = artwork["slug"]
    master_file = MASTERS_DIR / f"{slug}.jpg"
    thumb_file = ARTWORKS_DIR / f"{slug}.jpg"
    
    print(f"\n[{i}/{len(new_10_artworks)}] Processing {artwork['title']} ({slug})...", flush=True)
    
    orig_url = artwork["image_url"]
    download_url = orig_url
    try:
        if "upload.wikimedia.org" in orig_url:
            download_url = get_wikimedia_highres_url(orig_url)
            print(f"  -> Resolved URL: {download_url[:80]}...", flush=True)
    except Exception as e:
        print(f"  -> Resolution note: {e}, using direct URL", flush=True)
        download_url = orig_url
        
    download_ok = False
    for attempt in range(3):
        try:
            time.sleep(1.0)
            req = urllib.request.Request(download_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                print(f"  -> Downloaded {len(data) / (1024*1024):.2f} MB", flush=True)
                
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
                    
                artwork["resolution"] = f"{final_w:,} × {final_h:,} px".replace(",", " ")
                artwork["file_size"] = f"{master_mb:.1f} MB"
                print(f"  -> Successfully saved master ({master_mb:.1f} MB) and thumbnail.", flush=True)
                download_ok = True
                break
        except Exception as e:
            print(f"  -> Attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(2)
            
    if not download_ok and not master_file.exists():
        print(f"  -> WARNING: Failed to download {slug}!")

# Load existing artworks and append new artworks
with open(DATA_FILE, "r", encoding="utf-8") as f:
    existing_artworks = json.load(f)

# Ensure no duplicate slugs
existing_slugs = {a["slug"] for a in existing_artworks}
to_add = [a for a in new_10_artworks if a["slug"] not in existing_slugs]

all_artworks = existing_artworks + to_add

# Re-index ids 1..N
for idx, item in enumerate(all_artworks, 1):
    item["id"] = idx

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(all_artworks, f, indent=2, ensure_ascii=False)

print(f"\nSUCCESS! Total artworks now in archive: {len(all_artworks)}")
