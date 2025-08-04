"""Expose subject-specific parsers.

This package collects the various domain parsers, so they can be imported
directly from :mod:`cerebral_cortex.temporal_lobe.subject_parsers`.
Each parser provides a ``parse_<domain>_text`` function that extracts
structured facts from raw text within its subject area.
"""

# Import each domain parser's public ``parse_*_text`` function and re-export
# it for convenient access by consumers of this package.

from .bio_parser import parse_bio_text
from .chemistry_parser import parse_chemistry_text
from .conservation_parser import parse_conservation_text
from .cs_parser import parse_cs_text
from .econ_parser import parse_econ_text
from .eess_parser import parse_eess_text
from .game_theory_parser import parse_game_theory_text
from .geo_parser import parse_geo_text
from .history_parser import parse_history_text
from .law_parser import parse_law_text
from .math_parser import parse_math_text
from .philosophy_parser import parse_philosophy_text
from .physics_parser import parse_physics_text
from .psychology_parser import parse_psychology_text
from .sociology_parser import parse_sociology_text
from .stats_parser import parse_stats_text

__all__ = [
    "parse_bio_text",
    "parse_chemistry_text",
    "parse_conservation_text",
    "parse_cs_text",
    "parse_econ_text",
    "parse_eess_text",
    "parse_game_theory_text",
    "parse_geo_text",
    "parse_history_text",
    "parse_law_text",
    "parse_math_text",
    "parse_philosophy_text",
    "parse_physics_text",
    "parse_psychology_text",
    "parse_sociology_text",
    "parse_stats_text",
]
