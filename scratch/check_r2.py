"""
Script para verificar qué imágenes están en Cloudflare R2
y cuáles faltan respecto al archivo artworks.json local.
"""
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import boto3
from botocore.exceptions import ClientError

# --- CREDENCIALES ---
ACCOUNT_ID    = "ee95ac705cd7012e2d3d5fbfe1663026"
ACCESS_KEY_ID = "58186391571add0e952b54512083a142"
SECRET_KEY    = "4dc2ea3d2aa3c38810f9247c638ec1fdf8784b3d5aefbd940b368736a9ed1d36"
BUCKET_NAME   = "classic-art-archive"
# ---------------------

R2_ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_FILE  = BASE_DIR / "data" / "artworks.json"
ARTWORKS_DIR = BASE_DIR / "static" / "img" / "artworks"
MASTERS_DIR  = BASE_DIR / "static" / "img" / "masters"


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_KEY,
        region_name="auto",
    )


def list_r2_keys(client, prefix: str) -> set:
    """Lista todas las keys en R2 bajo un prefijo dado."""
    keys = set()
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])
    return keys


def main():
    print("=" * 65)
    print("  Classic Art Archive - Verificacion Cloudflare R2")
    print("=" * 65)

    # 1. Conectar
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=BUCKET_NAME)
        print(f"\n[OK] Conectado al bucket '{BUCKET_NAME}'.")
    except ClientError as e:
        print(f"\n[ERROR] No se pudo conectar: {e}")
        return

    # 2. Obtener keys de R2
    r2_artworks = list_r2_keys(client, "artworks/")
    r2_masters  = list_r2_keys(client, "masters/")
    print(f"\n[R2] artworks/ : {len(r2_artworks)} archivos")
    print(f"[R2] masters/  : {len(r2_masters)} archivos")

    # 3. Artworks locales (artworks.json)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        artworks = json.load(f)
    slugs = [a["slug"] for a in artworks]
    print(f"\n[LOCAL] artworks.json: {len(slugs)} obras")

    # 4. Archivos locales en disco
    local_artworks = {p.name for p in ARTWORKS_DIR.glob("*.jpg")}
    local_masters  = {p.name for p in MASTERS_DIR.glob("*.jpg")}
    print(f"[LOCAL] artworks/ en disco: {len(local_artworks)} archivos")
    print(f"[LOCAL] masters/  en disco: {len(local_masters)} archivos")

    # 5. Comparacion artworks
    print("\n" + "-" * 65)
    print("ARTWORKS (thumbnails web)")
    print("-" * 65)

    expected_artworks = {f"artworks/{slug}.jpg" for slug in slugs}
    in_r2_artworks = expected_artworks & r2_artworks
    missing_artworks = expected_artworks - r2_artworks
    extra_artworks   = r2_artworks - expected_artworks

    print(f"  OK En R2    : {len(in_r2_artworks)}/{len(expected_artworks)}")
    if missing_artworks:
        print(f"  FALTAN en R2 ({len(missing_artworks)}):")
        for k in sorted(missing_artworks):
            on_disk = "en disco" if k.split("/")[-1] in local_artworks else "NO en disco"
            print(f"      {k}  [{on_disk}]")
    else:
        print("  Todas las thumbnails estan en R2.")

    if extra_artworks:
        print(f"\n  Extra en R2 (no en artworks.json) ({len(extra_artworks)}):")
        for k in sorted(extra_artworks):
            print(f"      {k}")

    # 6. Comparacion masters
    print("\n" + "-" * 65)
    print("MASTERS (descarga HD)")
    print("-" * 65)

    expected_masters = {f"masters/{slug}.jpg" for slug in slugs}
    in_r2_masters  = expected_masters & r2_masters
    missing_masters = expected_masters - r2_masters
    extra_masters   = r2_masters - expected_masters

    print(f"  OK En R2    : {len(in_r2_masters)}/{len(expected_masters)}")
    if missing_masters:
        print(f"  FALTAN en R2 ({len(missing_masters)}):")
        for k in sorted(missing_masters):
            on_disk = "en disco" if k.split("/")[-1] in local_masters else "NO en disco"
            print(f"      {k}  [{on_disk}]")
    else:
        print("  Todas las imagenes master estan en R2.")

    if extra_masters:
        print(f"\n  Extra en R2 (no en artworks.json) ({len(extra_masters)}):")
        for k in sorted(extra_masters):
            print(f"      {k}")

    # 7. Resumen final
    print("\n" + "=" * 65)
    total_ok = len(in_r2_artworks) + len(in_r2_masters)
    total_expected = len(expected_artworks) + len(expected_masters)
    print(f"  RESUMEN: {total_ok}/{total_expected} archivos presentes en R2")
    if not missing_artworks and not missing_masters:
        print("  Todo esta en R2. El archivo esta completo!")
    else:
        total_missing = len(missing_artworks) + len(missing_masters)
        print(f"  FALTAN {total_missing} archivos en R2.")
        can_upload = sum(
            1 for k in missing_artworks if k.split("/")[-1] in local_artworks
        ) + sum(
            1 for k in missing_masters if k.split("/")[-1] in local_masters
        )
        if can_upload:
            print(f"  -> {can_upload} de ellos SI estan en disco y se pueden subir.")
    print("=" * 65)


if __name__ == "__main__":
    main()
