"""Generate a heatmap showing fact counts per domain.

The script scans the ``AI_Memory_Stores`` directory for ``.jsonl`` files,
counts the number of facts in each domain, and renders a simple heatmap using
``matplotlib``. The resulting image is saved alongside this script as
``heatmap.png``.
"""

from __future__ import annotations

import os
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "AI_Memory_Stores")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "heatmap.png")


def _count_facts(base_dir: str) -> Dict[str, int]:
    """Return a mapping of domain name to fact count."""
    counts: Dict[str, int] = {}
    for root, _, files in os.walk(base_dir):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            domain = os.path.splitext(os.path.relpath(path, base_dir))[0]
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    counts[domain] = sum(1 for _ in fh)
            except OSError:
                counts[domain] = 0
    return counts


def render_heatmap(counts: Dict[str, int], out_path: str = OUTPUT_PATH) -> None:
    """Render ``counts`` as a 1×N heatmap."""
    if not counts:
        print("No fact files found.")
        return

    labels = list(counts.keys())
    values = np.array(list(counts.values()))

    fig, ax = plt.subplots(figsize=(max(8, len(labels)), 2))
    im = ax.imshow(values[np.newaxis, :], cmap="hot", aspect="auto")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks([])

    for i, v in enumerate(values):
        ax.text(i, 0, str(v), ha="center", va="center", color="white")

    fig.colorbar(im, ax=ax, label="Fact count")
    plt.tight_layout()
    plt.savefig(out_path)
    print(f"Heatmap saved to {out_path}")


def main() -> None:  # pragma: no cover - convenience wrapper
    counts = _count_facts(os.path.normpath(MEMORY_DIR))
    render_heatmap(counts)


if __name__ == "__main__":  # pragma: no cover
    main()
