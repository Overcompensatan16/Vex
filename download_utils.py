"""Utility helpers for saving dumps and recording download metadata."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
import urllib.request
from urllib.parse import urlparse, unquote
from typing import List, Dict

DEFAULT_DUMP_BASE = os.path.normpath(
    os.getenv("DUMP_BASE", os.path.join(".", "dumps"))
)
LOG_PATH = os.path.normpath(os.path.join(DEFAULT_DUMP_BASE, "download_log.jsonl"))

# Directory containing the current download manifest. This allows relative
# ``file:`` URLs to resolve correctly when downloading from different manifests.
MANIFEST_DIR: str | None = None


def save_dump(data: bytes, src_name: str, file_name: str, base_path: str = DEFAULT_DUMP_BASE) -> str:
    dest_dir = os.path.normpath(os.path.join(base_path, src_name))
    os.makedirs(dest_dir, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{file_name}_{ts}.txt"
    path = os.path.normpath(os.path.join(dest_dir, filename))
    with open(path, "wb") as fh:
        fh.write(data)
    return path


def log_metadata(src_name: str, file_path: str, domain: str, base_path: str = DEFAULT_DUMP_BASE) -> None:
    with open(file_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": src_name,
        "file": file_path,
        "hash": digest,
        "domain": domain,
    }

    os.makedirs(base_path, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as log_fh:
        log_fh.write(json.dumps(entry) + "\n")


def simple_download(url: str, timeout: int = 20) -> bytes:
    """Return raw bytes from a URL or local file."""
    parsed = urlparse(url)

    if parsed.scheme == "file":
        # urllib will produce a leading '/' on Windows paths; remove it for
        # compatibility.
        path = unquote(parsed.path)
        if os.name == "nt" and path.startswith("/") and not path.startswith("//"):
            path = path[1:]
        if not os.path.isabs(path):
            base = MANIFEST_DIR or os.getcwd()
            path = os.path.join(base, path)
        try:
            with open(path, "rb") as fh:
                return fh.read()
        except FileNotFoundError:
            print(f"Local file not found: {path}")
            raise

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def download_from_manifest(manifest_path: str, dump_base: str = DEFAULT_DUMP_BASE) -> None:
    """Download all enabled entries in a manifest."""
    global MANIFEST_DIR
    MANIFEST_DIR = os.path.dirname(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    for source, info in config.items():
        if not info.get("enabled", True):
            continue
        url = info.get("url")
        if not url:
            continue
        try:
            data = simple_download(url)
        except Exception:
            continue
        name = os.path.basename(url)
        path = save_dump(data, source, name, dump_base)
        log_metadata(source, path, source)


def download_files(records: List[Dict], dump_base: str = DEFAULT_DUMP_BASE, manifest_path: str | None = None) -> List[Dict]:
    """Download multiple files defined by a list of record dicts."""
    global MANIFEST_DIR
    if manifest_path:
        MANIFEST_DIR = os.path.dirname(manifest_path)
    results: List[Dict] = []
    for rec in records:
        url = rec.get("url")
        src = rec.get("source", "generic")
        domain = rec.get("domain", src)
        if not url:
            continue
        try:
            data = simple_download(url)
        except Exception:
            continue
        name = os.path.basename(url)
        path = save_dump(data, src, name, dump_base)
        log_metadata(src, path, domain, dump_base)
        results.append({**rec, "path": path})
    return results
