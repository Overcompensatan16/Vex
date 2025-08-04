"""Collective source handler interface."""

from cerebral_cortex.source_handlers.external_loaders.wiki_handler import download_and_clean
from cerebral_cortex.source_handlers.external_loaders.arxiv_handler import fetch_subject

__all__ = ["download_and_clean", "fetch_subject"]
