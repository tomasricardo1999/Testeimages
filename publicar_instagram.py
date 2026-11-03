#!/usr/bin/env python3
"""Publica o pacote aprovado no Instagram via Instagram Graph API."""
from __future__ import annotations
import os
import time
from pathlib import Path
from urllib.parse import quote

import requests

ticker = os.environ["TICKER"].upper()
style = os.environ["ESTILO"]
ig_user_id = os.environ.get("IG_USER_ID", "").strip()
token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
repo = os.environ["GITHUB_REPOSITORY"]
branch = os.environ.get("GITHUB_REF_NAME", "main")
api_base = os.environ.get("IG_GRAPH_API_BASE", "https://graph.facebook.com/v25.0").rstrip("/")

if not ig_user_id or not token:
    raise SystemExit("Faltam os GitHub Secrets IG_USER_ID e/ou IG_ACCESS_TOKEN.")
if style not in {"standard", "editorial", "institucional", "criativo"}:
    raise SystemExit(f"Estilo inválido: {style}")

base = Path("dados_main" if ticker == "MAIN" else "dados_amd") / "instagram"
folder = base if style == "standard" else base / "variantes" / style
caption_path = folder / "legenda_instagram.txt"
caption = caption_path.read_text(encoding="utf-8").strip()
slides = sorted(folder.glob("slide_*.jpg"))
if len(slides) != 11:
    raise SystemExit(f"Esperados 11 JPEGs preparados; encontrados {len(slides)}.")

def api_post(path: str, data: dict) -> dict:
    response = requests.post(f"{api_base}/{path.lstrip('/')}", data={**data, "access_token": token}, timeout=90)
    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError(f"Resposta não JSON da Meta ({response.status_code}): {response.text[:500]}")
    if not response.ok or "error" in payload:
        raise RuntimeError(f"Erro da Meta ({response.status_code}): {payload}")
    return payload

def api_get(path: str, params: dict) -> dict:
    response = requests.get(f"{api_base}/{path.lstrip('/')}", params={**params, "access_token": token}, timeout=60)
    payload = response.json()
    if not response.ok or "error" in payload:
        raise RuntimeError(f"Erro da Meta ({response.status_code}): {payload}")
    return payload

def public_url(jpeg: Path) -> str:
    relative = jpeg.as_posix()
    return f"https://raw.githubusercontent.com/{repo}/{quote(branch, safe='/')}/{quote(relative, safe='/')}"

def wait_until_ready(container_id: str) -> None:
    for _ in range(30):
        status = api_get(container_id, {"fields": "status_code"})
        code = status.get("status_code")
        if code == "FINISHED":
            return
        if code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Container {container_id} terminou com estado {code}: {status}")
        time.sleep(10)
    raise TimeoutError(f"Container {container_id} não ficou pronto após 5 minutos.")

def publish_single_image(jpeg: Path, text: str) -> str:
    container = api_post(f"{ig_user_id}/media", {"image_url": public_url(jpeg), "caption": text})
    container_id = container["id"]
    wait_until_ready(container_id)
    media = api_post(f"{ig_user_id}/media_publish", {"creation_id": container_id})
    media_id = media["id"]
    details = api_get(media_id, {"fields": "id,permalink"})
    return details.get("permalink", f"ID {media_id}")

print(f"A publicar {ticker} ({style}) em duas publicações: 10 imagens + slide final.")
child_ids = []
for jpeg in slides[:10]:
    item = api_post(f"{ig_user_id}/media", {
        "image_url": public_url(jpeg),
        "is_carousel_item": "true",
    })
    child_ids.append(item["id"])

carousel = api_post(f"{ig_user_id}/media", {
    "media_type": "CAROUSEL",
    "children": ",".join(child_ids),
    "caption": caption,
})
carousel_id = carousel["id"]
wait_until_ready(carousel_id)
published = api_post(f"{ig_user_id}/media_publish", {"creation_id": carousel_id})
carousel_media_id = published["id"]
carousel_details = api_get(carousel_media_id, {"fields": "id,permalink"})
carousel_url = carousel_details.get("permalink", f"ID {carousel_media_id}")
print(f"Carrossel (slides 1-10) publicado: {carousel_url}")

final_caption = caption + "\n\nContinuação — slide final (11/11)."
final_url = publish_single_image(slides[10], final_caption)
print(f"Slide final (11/11) publicado separadamente: {final_url}")
print("PUBLICAÇÃO CONCLUÍDA.")
