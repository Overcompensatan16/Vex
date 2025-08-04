"""Utility helpers for saving dumps, recording download metadata, and managing batch downloads."""

from __future__ import annotations

import hashlib
import json
import hashlib
import json
import os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from urllib.parse import urlparse, unquote
from typing import Dict, List

from audit.audit_logger_factory import AuditLoggerFactory

# Default location for storing downloaded dumps. This should point to the
# external drive so data does not clutter the project directory.
DEFAULT_DUMP_BASE = os.path.normpath(os.getenv("DUMP_BASE", r"E:\\dumps"))
LOG_PATH = os.path.normpath(os.path.join(DEFAULT_DUMP_BASE, "download_log.jsonl"))

# Location for tracking incremental downloads. This file lives alongside the
# external loaders, so it remains within the repo and can be easily inspected.
TRACKER_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "external_loaders", "download_tracker.json")
)

# Directory containing the current download manifest. This allows relative
# ``file:`` URLs to resolve correctly when downloading from different manifests.
MANIFEST_DIR: str | None = None

DL_LOGGERS = {
    "arxiv": AuditLoggerFactory(
        "arxiv_dl", log_path=os.path.join("error_logs", "arxiv_dl.log")
    ),
    "wiki": AuditLoggerFactory(
        "wikipedia_dl", log_path=os.path.join("error_logs", "wikipedia_dl.log")
    ),
    "wikipedia": AuditLoggerFactory(
        "wikipedia_dl", log_path=os.path.join("error_logs", "wikipedia_dl.log")
    ),
}


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

    log_path = os.path.join(base_path, "download_log.jsonl")
    os.makedirs(base_path, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as log_fh:
        log_fh.write(json.dumps(entry) + "\n")


def read_tracker(path: str = TRACKER_PATH) -> Dict[str, int]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def write_tracker(data: Dict[str, int], path: str = TRACKER_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def simple_download(url: str, timeout: int = 20, logger=None) -> bytes:
    parsed = urlparse(url)

    if parsed.scheme == "file":
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
            if logger:
                logger.log_error("download", f"Local file not found: {path}")
            raise

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def download_from_manifest(manifest_path: str, dump_base: str = DEFAULT_DUMP_BASE) -> None:
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
        logger = DL_LOGGERS.get(source)
        try:
            data = simple_download(url, logger=logger)
        except Exception:
            if logger:
                logger.log_error("download", f"Failed {url}")
            continue
        name = os.path.basename(url)
        path = save_dump(data, source, name, dump_base)
        log_metadata(source, path, source)


def download_files(
    records: List[Dict], dump_base: str = DEFAULT_DUMP_BASE, manifest_path: str | None = None
) -> List[Dict]:
    global MANIFEST_DIR
    if manifest_path:
        MANIFEST_DIR = os.path.dirname(manifest_path)

    os.makedirs(dump_base, exist_ok=True)

    def download_single(rec: Dict) -> Dict | None:
        url = rec.get("url")
        src = rec.get("source", "generic")
        domain = rec.get("domain", src)
        if not url:
            return None
        logger = DL_LOGGERS.get(src)
        try:
            data = simple_download(url, logger=logger)
            name = os.path.basename(url)
            path = save_dump(data, src, name, dump_base)
            log_metadata(src, path, domain, dump_base)
            if logger:
                logger.log_event("download", {"message": f"Saved: {path}", "url": url})
            return {**rec, "path": path}
        except Exception as e:
            if logger:
                logger.log_error("download", f"Failed {url}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(download_single, records))

    return [r for r in results if r]