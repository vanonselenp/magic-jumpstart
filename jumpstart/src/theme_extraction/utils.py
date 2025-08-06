"""Utility functions for theme extraction and code generation."""

from typing import Dict, Any
import pandas as pd
from .extractor import ThemeExtractor


def extract_themes_from_oracle(oracle_df: pd.DataFrame, 
                              min_cards_per_theme: int = 10) -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to extract themes from oracle DataFrame.
    
    Args:
        oracle_df: DataFrame containing Magic card data
        min_cards_per_theme: Minimum cards required to generate a theme
        
    Returns:
        Dictionary of theme configurations in the same format as MONO_COLOR_THEMES
    """
    extractor = ThemeExtractor(oracle_df)
    return extractor.extract_themes(min_cards_per_theme)


def generate_theme_code(themes: Dict[str, Dict[str, Any]], 
                       variable_name: str = "EXTRACTED_THEMES") -> str:
    """
    Generate Python code for the extracted themes.
    
    Args:
        themes: Dictionary of theme configurations
        variable_name: Name for the generated variable
        
    Returns:
        Python code string that can be added to consts.py
    """
    lines = [f"{variable_name} = {{"]
    
    for theme_name, theme_config in themes.items():
        lines.append(f"    '{theme_name}': {{")
        lines.append(f"        'colors': {theme_config['colors']},")
        lines.append(f"        'strategy': '{theme_config['strategy']}',")
        lines.append(f"        'keywords': {theme_config['keywords']},")
        lines.append(f"        'archetype': Archetype.{theme_config['archetype'].name},")
        lines.append(f"        'scorer': {theme_config['scorer'].__name__},")
        lines.append(f"        'core_card_count': {theme_config['core_card_count']}")
        lines.append("    },")
    
    lines.append("}")
    return "\n".join(lines)
