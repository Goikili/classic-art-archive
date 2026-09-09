"""
Script para subir todas las imagenes de artworks a Cloudflare R2.
"""
import sys
import io
import boto3
from pathlib import Path
from botocore.exceptions import ClientError

# Forzar UTF-8 en stdout para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# --- CREDENCIALES ---
ACCOUNT_ID    = "ee95ac705cd7012e2d3d5fbfe1663026"
ACCESS_KEY_ID = "58186391571add0e952b54512083a142"
SECRET_KEY    = "4dc2ea3d2aa3c38810f9247c638ec1fdf8784b3d5aefbd940b368736a9ed1d36"
BUCKET_NAME   = "classic-art-archive"
# ---------------------

R2_ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"

BASE_DIR     = Path(__file__).resolve().parent.parent
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


def upload_folder(client, folder: Path, r2_prefix: str):
    if not folder.exists():
        print(f"[SKIP] Carpeta no encontrada: {folder}")
        return

    files = sorted(folder.glob("*.jpg"))
    if not files:
        print(f"[SKIP] No hay imagenes en: {folder}")
        return

    print(f"\n[UPLOAD] {len(files)} imagenes desde '{folder.name}' -> r2/{r2_prefix}/")
    print("-" * 60)

    ok = 0
    errors = []

    for img_path in files:
        r2_key = f"{r2_prefix}/{img_path.name}"
        try:
            client.upload_file(
                Filename=str(img_path),
                Bucket=BUCKET_NAME,
                Key=r2_key,
                ExtraArgs={"ContentType": "image/jpeg"},
            )
            print(f"  OK  {img_path.name}")
            ok += 1
        except ClientError as e:
            print(f"  ERR {img_path.name} -> {e}")
            errors.append(img_path.name)

    print(f"\n  Resultado: {ok} subidas, {len(errors)} errores")
    if errors:
        print(f"  Errores: {errors}")


def main():
    print("=" * 60)
    print("  Classic Art Archive -> Cloudflare R2 Upload")
    print("=" * 60)

    client = get_s3_client()

    try:
        client.head_bucket(Bucket=BUCKET_NAME)
        print(f"\n[OK] Conectado al bucket '{BUCKET_NAME}'.")
    except ClientError as e:
        print(f"\n[ERROR] No se pudo conectar: {e}")
        return

    upload_folder(client, ARTWORKS_DIR, "artworks")
    upload_folder(client, MASTERS_DIR, "masters")

    print("\n" + "=" * 60)
    print("  SUBIDA COMPLETADA.")
    print("\n  URL base publica:")
    print("  https://pub-7ef67ec2a62b4ee9b2eb09ef674cfcb7.r2.dev/artworks/mona-lisa.jpg")
    print("=" * 60)


if __name__ == "__main__":
    main()
