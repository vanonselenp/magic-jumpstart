"""Theme extraction module for Magic: The Gathering Jumpstart cubes.

This module provides comprehensive theme extraction capabilities from Magic card data,
including tribal themes, keyword-based archetypes, and mana curve analysis.
"""

from .extractor import ThemeExtractor
from .utils import extract_themes_from_oracle, generate_theme_code
from . import keywords

__all__ = [
    'ThemeExtractor',
    'extract_themes_from_oracle', 
    'generate_theme_code',
    'keywords'
]
