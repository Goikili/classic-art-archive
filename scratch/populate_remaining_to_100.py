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

USER_AGENT = "ClassicArtArchiveBot/2.2 (https://classicartarchive.org; contact: contact@classicartarchive.com)"
HEADERS = {"User-Agent": USER_AGENT}

additional_masterpieces = [
    {
        "slug": "the-lady-of-shalott",
        "title": "The Lady of Shalott",
        "original_title": "The Lady of Shalott",
        "artist": "John William Waterhouse",
        "year": "1888",
        "period": "Pre-Raphaelite",
        "medium": "Oil on canvas",
        "dimensions": "153 cm × 200 cm",
        "location": "Tate Britain, London, United Kingdom",
        "query": "John William Waterhouse The Lady of Shalott Tate",
        "description": "The tragic maiden sets sail down the river toward Camelot into the misty autumn dusk, wrapped in an embroidered tapestry beside a single candle.",
        "analysis": "A crowning masterpiece of the Pre-Raphaelite Brotherhood, capturing romantic tragedy, rich fabrics, and autumnal naturalism.",
        "featured": True,
        "instagram_post_caption": "Waterhouse's legendary Pre-Raphaelite romantic tragedy: The Lady of Shalott.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "hylas-and-the-nymphs",
        "title": "Hylas and the Nymphs",
        "original_title": "Hylas and the Nymphs",
        "artist": "John William Waterhouse",
        "year": "1896",
        "period": "Pre-Raphaelite",
        "medium": "Oil on canvas",
        "dimensions": "98.2 cm × 163.7 cm",
        "location": "Manchester Art Gallery, United Kingdom",
        "query": "John William Waterhouse Hylas and the Nymphs Manchester Art Gallery",
        "description": "The youth Hylas is lured into the depths of a moonlit, water-lily-covered spring by seven alluring freshwater Naiad nymphs.",
        "analysis": "Renowned for its ethereal sensuality, delicate water lilies, and atmospheric blend of Classical myth with British Romanticism.",
        "featured": False,
        "instagram_post_caption": "Waterhouse's seductive mythological dream: Hylas and the Nymphs.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "circe-invidiosa",
        "title": "Circe Invidiosa",
        "original_title": "Circe Invidiosa",
        "artist": "John William Waterhouse",
        "year": "1892",
        "period": "Pre-Raphaelite",
        "medium": "Oil on canvas",
        "dimensions": "179 cm × 85 cm",
        "location": "Art Gallery of South Australia, Adelaide",
        "query": "John William Waterhouse Circe Invidiosa Art Gallery of South Australia",
        "description": "The sorceress Circe pours a glowing green poison into the azure waters of a cliffside sea pool to transform her rival Scylla into a sea monster.",
        "analysis": "Notable for its intense palette of cobalt blue and emerald green, embodying femme fatale mystique and mythic vengeance.",
        "featured": False,
        "instagram_post_caption": "Waterhouse's hypnotic sorceress: Circe Invidiosa in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "flaming-june",
        "title": "Flaming June",
        "original_title": "Flaming June",
        "artist": "Frederic Leighton",
        "year": "1895",
        "period": "Academic / Aestheticism",
        "medium": "Oil on canvas",
        "dimensions": "120.6 cm × 120.6 cm",
        "location": "Museo de Arte de Ponce, Puerto Rico",
        "query": "Frederic Leighton Flaming June Ponce",
        "description": "A slumbering woman curled in a marble loggia bathed in shimmering Mediterranean sunlight, wrapped in luminous flame-colored diaphanous silk.",
        "analysis": "The supreme icon of Victorian Aestheticism, celebrated for its radiant drapery curves, warm glowing tones, and tranquil classical beauty.",
        "featured": True,
        "instagram_post_caption": "Frederic Leighton's glowing Victorian icon: Flaming June in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-accolade",
        "title": "The Accolade",
        "original_title": "The Accolade",
        "artist": "Edmund Leighton",
        "year": "1901",
        "period": "Pre-Raphaelite / Romanticism",
        "medium": "Oil on canvas",
        "dimensions": "182.3 cm × 108 cm",
        "location": "Private Collection",
        "query": "Edmund Blair Leighton The Accolade 1901",
        "description": "A graceful medieval queen dubs a kneeling warrior knight with a broadsword in an open castle courtyard before the court.",
        "analysis": "The quintessence of modern Arthurian chivalry, praised for its photographic rendering of chainmail, white silk, and stone arches.",
        "featured": False,
        "instagram_post_caption": "Edmund Leighton's chivalric ideal: The Accolade in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "lady-godiva",
        "title": "Lady Godiva",
        "original_title": "Lady Godiva",
        "artist": "John Collier",
        "year": "c. 1897",
        "period": "Pre-Raphaelite / Academic",
        "medium": "Oil on canvas",
        "dimensions": "142.2 cm × 183 cm",
        "location": "Herbert Art Gallery & Museum, Coventry, United Kingdom",
        "query": "John Collier Lady Godiva Herbert Art Gallery",
        "description": "Lady Godiva rides nude through the deserted stone streets of Coventry draped on a white horse to demand tax relief for the impoverished citizens.",
        "analysis": "Combines Academic perfection of figure drawing with rich medievalist pageantry, emphasizing quiet noble sacrifice.",
        "featured": False,
        "instagram_post_caption": "John Collier's legendary heroine: Lady Godiva (Coventry Museum).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "dante-and-virgil",
        "title": "Dante and Virgil in Hell",
        "original_title": "Dante et Virgile",
        "artist": "William-Adolphe Bouguereau",
        "year": "1850",
        "period": "Academic / Neoclassicism",
        "medium": "Oil on canvas",
        "dimensions": "281 cm × 225 cm",
        "location": "Musée d'Orsay, Paris, France",
        "query": "William Bouguereau Dante et Virgile Musee dOrsay",
        "description": "Dante and Virgil watch in horror in the eighth circle of Hell as Gianni Schicchi bites the neck of the heretic Capocchio in ferocious combat.",
        "analysis": "Bouguereau's thrilling demonstration of anatomical mastery, depicting the tension of sinews, subterranean gloom, and demonic terror.",
        "featured": True,
        "instagram_post_caption": "Bouguereau's ferocious infernal masterpiece: Dante and Virgil in Hell.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-birth-of-venus-bouguereau",
        "title": "The Birth of Venus",
        "original_title": "La Naissance de Vénus",
        "artist": "William-Adolphe Bouguereau",
        "year": "1879",
        "period": "Academic",
        "medium": "Oil on canvas",
        "dimensions": "300 cm × 218 cm",
        "location": "Musée d'Orsay, Paris, France",
        "query": "William-Adolphe Bouguereau La Naissance de Venus Musee dOrsay",
        "description": "Venus stands in a seashell escorted by putti, tritons, and sea nymphs blowing conch shells upon the calm Mediterranean sea.",
        "analysis": "The triumph of 19th-century French Academic polish, renowned for porcelain skin tones and fluid Hellenistic rhythm.",
        "featured": False,
        "instagram_post_caption": "Bouguereau's Academic spectacle: The Birth of Venus (Musée d'Orsay).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-sistine-madonna",
        "title": "The Sistine Madonna",
        "original_title": "Madonna Sistina",
        "artist": "Raphael",
        "year": "1512–1513",
        "period": "High Renaissance",
        "medium": "Oil on canvas",
        "dimensions": "265 cm × 196 cm",
        "location": "Gemäldegalerie Alte Meister, Dresden, Germany",
        "query": "Raphael Sistine Madonna Dresden",
        "description": "The Virgin Mary holding the Christ Child steps forward through parting green curtains on heavenly clouds, flanked by Saint Sixtus and Saint Barbara.",
        "analysis": "Famous worldwide for the two contemplative resting cherubs at the bottom, achieving supreme High Renaissance harmony and spiritual majesty.",
        "featured": True,
        "instagram_post_caption": "Raphael's divine High Renaissance icon: The Sistine Madonna in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "portrait-of-baldassare-castiglione",
        "title": "Portrait of Baldassare Castiglione",
        "original_title": "Ritratto di Baldassarre Castiglione",
        "artist": "Raphael",
        "year": "1514–1515",
        "period": "High Renaissance",
        "medium": "Oil on canvas",
        "dimensions": "82 cm × 67 cm",
        "location": "Musée du Louvre, Paris, France",
        "query": "Raphael Baldassare Castiglione Louvre",
        "description": "The humanist author of The Book of the Courtier gazes calmly toward the viewer in a luxurious black doublet, grey fur, and beret.",
        "analysis": "A benchmark of Renaissance courtly grace (sprezzatura) and psychological warmth that directly influenced Rembrandt and Titian.",
        "featured": False,
        "instagram_post_caption": "Raphael's masterpiece of courtly presence: Baldassare Castiglione (Louvre).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-triumph-of-galatea",
        "title": "The Triumph of Galatea",
        "original_title": "Trionfo di Galatea",
        "artist": "Raphael",
        "year": "1512",
        "period": "High Renaissance",
        "medium": "Fresco",
        "dimensions": "295 cm × 225 cm",
        "location": "Villa Farnesina, Rome, Italy",
        "query": "Raphael Trionfo di Galatea Villa Farnesina",
        "description": "The sea nymph Galatea rides a shell chariot pulled by dolphins across the waves, surrounded by cupids shooting love arrows and sea centaurs.",
        "analysis": "Exemplifies Raphael's perfect compositional equilibrium and joyous recreation of antique pagan mythology.",
        "featured": False,
        "instagram_post_caption": "Raphael's Roman fresco triumph: The Triumph of Galatea.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "venus-of-urbino",
        "title": "Venus of Urbino",
        "original_title": "Venere di Urbino",
        "artist": "Titian",
        "year": "1538",
        "period": "Renaissance",
        "medium": "Oil on canvas",
        "dimensions": "119 cm × 165 cm",
        "location": "Uffizi Gallery, Florence, Italy",
        "query": "Titian Venus of Urbino Uffizi",
        "description": "A voluptuous young woman reclines on a luxurious couch in a Venetian palazzo, holding a bouquet of roses while a puppy sleeps at her feet.",
        "analysis": "The prototype for the domestic reclining female nude across European history, inspiring Goya's Maja and Manet's Olympia.",
        "featured": True,
        "instagram_post_caption": "Titian's pinnacle of Venetian sensuality: The Venus of Urbino (Uffizi).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "assumption-of-the-virgin",
        "title": "Assumption of the Virgin",
        "original_title": "Assunta",
        "artist": "Titian",
        "year": "1516–1518",
        "period": "Renaissance",
        "medium": "Oil on wood panel",
        "dimensions": "690 cm × 360 cm",
        "location": "Santa Maria Gloriosa dei Frari, Venice, Italy",
        "query": "Titian Assumption of the Virgin Frari Venice",
        "description": "The Virgin Mary is lifted upward into golden celestial radiance by a swirling cloud of cherubs as astonished apostles gesture from below.",
        "analysis": "Established Titian as the undisputed master of Venice through heroic scale, incandescent chromatic vitality, and dynamic vertical motion.",
        "featured": False,
        "instagram_post_caption": "Titian's monumental Venetian altarpiece: Assumption of the Virgin.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "david-with-the-head-of-goliath",
        "title": "David with the Head of Goliath",
        "original_title": "Davide con la testa di Golia",
        "artist": "Caravaggio",
        "year": "1610",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "125 cm × 101 cm",
        "location": "Galleria Borghese, Rome, Italy",
        "query": "Caravaggio David with the Head of Goliath Galleria Borghese",
        "description": "A youthful David looks with somber, mournful pity at the severed, bleeding head of Goliath, which is a haunting self-portrait of Caravaggio himself.",
        "analysis": "Caravaggio's desperate personal plea for papal pardon shortly before his death, linking victor and victim in shared tragedy.",
        "featured": True,
        "instagram_post_caption": "Caravaggio's tragic self-portrait in death: David with the Head of Goliath.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "narcissus",
        "title": "Narcissus",
        "original_title": "Narciso",
        "artist": "Caravaggio",
        "year": "c. 1597–1599",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "112 cm × 92 cm",
        "location": "Galleria Nazionale d'Arte Antica, Rome, Italy",
        "query": "Caravaggio Narciso Palazzo Barberini",
        "description": "The handsome youth Narcissus leans over a still pool in an intense circular reflection loop, spellbound by his own reflection.",
        "analysis": "A striking card-like symmetry that explores fatal vanity, obsession, and the very nature of pictorial reflection and illusion.",
        "featured": True,
        "instagram_post_caption": "Caravaggio's hypnotic circular reflection: Narcissus in Ultra HD.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "medusa",
        "title": "Medusa",
        "original_title": "Scudo con testa di Medusa",
        "artist": "Caravaggio",
        "year": "1597",
        "period": "Baroque",
        "medium": "Oil on canvas mounted on convex wooden tournament shield",
        "dimensions": "60 cm × 55 cm",
        "location": "Uffizi Gallery, Florence, Italy",
        "query": "Caravaggio Medusa Uffizi Florence",
        "description": "The severed head of the Gorgon Medusa screams with horror in her final instant of consciousness, with writhing venomous vipers for hair.",
        "analysis": "Painted on a convex wooden shield, overcoming distortion to create a terrifyingly real three-dimensional optical illusion.",
        "featured": True,
        "instagram_post_caption": "Caravaggio's terrifying optical illusion: Medusa (Uffizi Gallery).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-conversion-of-saint-paul",
        "title": "The Conversion of Saint Paul",
        "original_title": "Conversione di San Paolo",
        "artist": "Caravaggio",
        "year": "1601",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "230 cm × 175 cm",
        "location": "Santa Maria del Popolo, Rome, Italy",
        "query": "Caravaggio Conversione di San Paolo Cerasi",
        "description": "Saul of Tarsus falls to the ground beneath the hooves of his horse, arms outstretched in ecstatic surrender to the blinding divine light.",
        "analysis": "Caravaggio strips miraculous revelation of angels and trumpets, grounding spiritual conversion in raw, intimate bodily reality.",
        "featured": False,
        "instagram_post_caption": "Caravaggio's lightning bolt of divine grace: The Conversion of Saint Paul.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "aristotle-with-a-bust-of-homer",
        "title": "Aristotle with a Bust of Homer",
        "original_title": "Aristoteles bij de buste van Homerus",
        "artist": "Rembrandt van Rijn",
        "year": "1653",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "143.5 cm × 136.5 cm",
        "location": "Metropolitan Museum of Art, New York, United States",
        "query": "Rembrandt Aristotle with a Bust of Homer Metropolitan Museum of Art",
        "description": "The philosopher Aristotle, wearing a massive gold medallion chain, rests his hand thoughtfully upon the sculpted marble bust of the blind poet Homer.",
        "analysis": "A profound meditation on worldly success, philosophical wisdom, and enduring artistic immortality.",
        "featured": True,
        "instagram_post_caption": "Rembrandt's philosophical masterpiece: Aristotle with a Bust of Homer (The Met).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "bathsheba-at-her-bath",
        "title": "Bathsheba at Her Bath",
        "original_title": "Bethsabée au bain tenant la lettre de David",
        "artist": "Rembrandt van Rijn",
        "year": "1654",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "142 cm × 142 cm",
        "location": "Musée du Louvre, Paris, France",
        "query": "Rembrandt Bathsheba at Her Bath Louvre",
        "description": "Bathsheba holds King David's summons letter in her lap with a sorrowful, conflicted expression as her maid attends to her feet.",
        "analysis": "Modeled on Rembrandt's companion Hendrickje Stoffels, celebrated for its emotional depth and honest human vulnerability.",
        "featured": False,
        "instagram_post_caption": "Rembrandt's intimate psychological tragedy: Bathsheba at Her Bath (Louvre).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-return-of-the-prodigal-son",
        "title": "The Return of the Prodigal Son",
        "original_title": "De terugkeer van de verloren zoon",
        "artist": "Rembrandt van Rijn",
        "year": "c. 1669",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "262 cm × 205 cm",
        "location": "Hermitage Museum, Saint Petersburg, Russia",
        "query": "Rembrandt The Return of the Prodigal Son Hermitage",
        "description": "A repentant son in tattered rags kneels before his elderly father, who tenderly places his hands on his shoulders in unconditional forgiveness.",
        "analysis": "Rembrandt's spiritual and emotional summit, radiating deep compassion, forgiveness, and universal fatherly love.",
        "featured": True,
        "instagram_post_caption": "Rembrandt's ultimate testament of forgiveness: The Return of the Prodigal Son.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "the-syndics-of-the-drapers-guild",
        "title": "The Syndics of the Drapers' Guild",
        "original_title": "De Staalmeesters",
        "artist": "Rembrandt van Rijn",
        "year": "1662",
        "period": "Baroque",
        "medium": "Oil on canvas",
        "dimensions": "191.5 cm × 279 cm",
        "location": "Rijksmuseum, Amsterdam, Netherlands",
        "query": "Rembrandt De Staalmeesters The Syndics of the Drapers Guild Rijksmuseum",
        "description": "Five inspectors of the Amsterdam clothmaker guild interrupt their meeting at a table covered with a Persian carpet to look up at an arriving visitor.",
        "analysis": "Revolutionary corporate group portrait that transforms a business review into an interactive, spontaneous moment of shared gaze.",
        "featured": False,
        "instagram_post_caption": "Rembrandt's masterwork of collective focus: The Syndics (Rijksmuseum).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "plum-park-in-kameido",
        "title": "Plum Park in Kameido",
        "original_title": "Kameido Umeyashiki",
        "artist": "Utagawa Hiroshige",
        "year": "1857",
        "period": "Edo Period (Ukiyo-e)",
        "medium": "Woodblock print (ink and color on paper)",
        "dimensions": "36 cm × 23.5 cm",
        "location": "Tokyo National Museum / Brooklyn Museum",
        "query": "Hiroshige Plum Park in Kameido Brooklyn Museum",
        "description": "A gnarled plum tree branch blossoms in white against a glowing crimson dusk sky in the famous Garyūbai plum garden of Edo.",
        "analysis": "One of the most famous Ukiyo-e prints in history, famously copied in oil by Vincent van Gogh in 1887.",
        "featured": True,
        "instagram_post_caption": "Hiroshige's iconic Japanese woodblock: Plum Park in Kameido.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "sudden-shower-over-shin-ohashi-bridge",
        "title": "Sudden Shower over Shin-Ōhashi Bridge and Atake",
        "original_title": "Ōhashi Atake no Yūdachi",
        "artist": "Utagawa Hiroshige",
        "year": "1857",
        "period": "Edo Period (Ukiyo-e)",
        "medium": "Woodblock print",
        "dimensions": "34 cm × 22.5 cm",
        "location": "Art Institute of Chicago / Brooklyn Museum",
        "query": "Hiroshige Sudden Shower over Shin-Ohashi bridge and Atake",
        "description": "Pedestrians scurry across the wooden Shin-Ōhashi bridge sheltering under straw mats and umbrellas as torrential summer rain sheets down over the Sumida River.",
        "analysis": "Pioneered diagonal atmospheric rain rendering in printmaking, profoundly transforming Impressionist and Post-Impressionist landscape art.",
        "featured": True,
        "instagram_post_caption": "Hiroshige's masterpiece of summer rain: Sudden Shower over Shin-Ōhashi Bridge.",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    },
    {
        "slug": "fuji-red-fine-wind-clear-morning",
        "title": "Fine Wind, Clear Morning (Red Fuji)",
        "original_title": "Gaifū kaisei",
        "artist": "Katsushika Hokusai",
        "year": "c. 1830–1832",
        "period": "Edo Period (Ukiyo-e)",
        "medium": "Polychrome woodblock print",
        "dimensions": "25.7 cm × 38 cm",
        "location": "Metropolitan Museum of Art / British Museum",
        "query": "Hokusai Fine Wind Clear Morning Red Fuji Metropolitan Museum of Art",
        "description": "Mount Fuji glows in deep reddish-terracotta under late summer morning sunlight beneath a crisp azure sky filled with delicate cirrus clouds.",
        "analysis": "A pinnacle of minimalist Japanese landscape printmaking, revered worldwide for its simplicity and majestic geometric abstraction.",
        "featured": True,
        "instagram_post_caption": "Hokusai's sublime sacred volcano: Fine Wind, Clear Morning (Red Fuji).",
        "instagram_tag": "@classicartarchive",
        "license": "Public Domain (CC0 / PDM 1.0)"
    }
]


def find_commons_image(query: str, fallback_title: str = "") -> str:
    search_queries = [query]
    if fallback_title and fallback_title != query:
        search_queries.append(fallback_title)
        
    for q in search_queries:
        try:
            url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&srsearch={urllib.parse.quote(q)}&format=json"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            results = data.get("query", {}).get("search", [])
            if not results:
                continue
            title = results[0]["title"]
            
            info_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url|size&iiurlwidth=4000&format=json"
            req2 = urllib.request.Request(info_url, headers=HEADERS)
            with urllib.request.urlopen(req2, timeout=15) as resp:
                info_data = json.loads(resp.read().decode("utf-8"))
            pages = info_data.get("query", {}).get("pages", {})
            for p in pages.values():
                for info in p.get("imageinfo", []):
                    orig_size = info.get("size", 0)
                    orig_url = info.get("url")
                    thumb_url = info.get("thumburl")
                    if orig_size < 35_000_000 and orig_url:
                        return orig_url
                    if thumb_url:
                        return thumb_url
                    if orig_url:
                        return orig_url
        except Exception as e:
            print(f"    [Search Error for '{q}']: {e}")
            time.sleep(1)
    return ""


# Load existing database
with open(DATA_FILE, "r", encoding="utf-8") as f:
    existing_artworks = json.load(f)

existing_slugs = {a["slug"] for a in existing_artworks}
print(f"Starting top-up. Current archive count: {len(existing_artworks)}")

for idx, item in enumerate(additional_masterpieces, 1):
    if len(existing_artworks) >= 100:
        print(f"Reached 100 artworks goal!")
        break
        
    slug = item["slug"]
    title = item["title"]
    artist = item["artist"]
    
    if slug in existing_slugs:
        print(f"Skipping already existing '{slug}'")
        continue
        
    master_file = MASTERS_DIR / f"{slug}.jpg"
    thumb_file = ARTWORKS_DIR / f"{slug}.jpg"
    
    print(f"\n[Additional {idx}] Downloading {title} by {artist} ({slug})...", flush=True)
    
    img_url = find_commons_image(item.get("query", f"{artist} {title}"), f"{title} {artist}")
    if not img_url:
        print(f"  -> WARNING: Could not find image for {title}!")
        continue
        
    download_ok = False
    for attempt in range(3):
        try:
            time.sleep(0.8)
            req = urllib.request.Request(img_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = resp.read()
                
            img = Image.open(io.BytesIO(data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            w, h = img.size
            max_side = 5000
            if max(w, h) > max_side:
                ratio = max_side / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
                
            img.save(master_file, "JPEG", quality=94, optimize=True)
            master_mb = master_file.stat().st_size / (1024 * 1024)
            final_w, final_h = img.size
            
            web_max = 1600
            if max(final_w, final_h) > web_max:
                ratio_web = web_max / max(final_w, final_h)
                web_img = img.resize((int(final_w * ratio_web), int(final_h * ratio_web)), Image.Resampling.LANCZOS)
                web_img.save(thumb_file, "JPEG", quality=88, optimize=True)
            else:
                img.save(thumb_file, "JPEG", quality=88, optimize=True)
                
            new_id = len(existing_artworks) + 1
            entry = {
                "id": new_id,
                "slug": slug,
                "title": title,
                "original_title": item.get("original_title", title),
                "artist": artist,
                "year": item.get("year", "Classic Era"),
                "period": item.get("period", "Classic"),
                "medium": item.get("medium", "Oil on canvas"),
                "dimensions": item.get("dimensions", "Standard"),
                "location": item.get("location", "Museum Collection"),
                "image_url": img_url,
                "thumbnail_url": f"/static/img/artworks/{slug}.jpg",
                "download_filename": f"{artist.split()[-1]}_{slug.replace('-', '_').title()}_UltraHD.jpg",
                "resolution": f"{final_w:,} × {final_h:,} px".replace(",", " "),
                "file_size": f"{master_mb:.1f} MB",
                "description": item.get("description", ""),
                "analysis": item.get("analysis", ""),
                "featured": item.get("featured", False),
                "instagram_post_caption": item.get("instagram_post_caption", f"{title} by {artist}"),
                "instagram_tag": "@classicartarchive",
                "license": "Public Domain (CC0 / PDM 1.0)"
            }
            
            existing_artworks.append(entry)
            existing_slugs.add(slug)
            
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_artworks, f, indent=2, ensure_ascii=False)
                
            print(f"  -> Successfully saved #{new_id}: {title} ({final_w}x{final_h}, {master_mb:.1f} MB)", flush=True)
            download_ok = True
            break
        except Exception as e:
            print(f"  -> Attempt {attempt+1} failed: {e}", flush=True)
            time.sleep(2)

print(f"\n=======================================================")
print(f"FINISHED! Total artworks now in archive: {len(existing_artworks)}")
print(f"=======================================================")
