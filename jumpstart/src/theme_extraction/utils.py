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
                       variable_name: str = "EXTRACTED_THEMES") -> Dict[str, Dict[str, Any]]:
    """
    Generate theme dictionary in the same format as ALL_THEMES.
    
    Args:
        themes: Dictionary of theme configurations
        variable_name: Name for the generated variable (kept for backwards compatibility)
        
    Returns:
        Dictionary of themes in the exact same format as ALL_THEMES, ready to use directly
    """
    # Return the themes in the exact same format as ALL_THEMES
    # The structure is already correct, just return as-is
    return themes


def generate_theme_code_string(themes: Dict[str, Dict[str, Any]], 
                              variable_name: str = "EXTRACTED_THEMES") -> str:
    """
    Generate Python code string for the extracted themes.
    
    Args:
        themes: Dictionary of theme configurations
        variable_name: Name for the generated variable
        
    Returns:
        Python code string that can be added to consts.py
    """
    lines = [
        "# Auto-generated themes from theme extraction",
        "from .enums import Archetype, MagicColor",
        "from .scorer import (",
        "    create_default_scorer, create_tribal_scorer, create_equipment_scorer,",
        "    create_aggressive_scorer, create_stompy_scorer, create_artifact_scorer,",
        "    create_control_scorer",
        ")",
        "",
        f"{variable_name} = {{"
    ]
    
    for theme_name, theme_config in themes.items():
        lines.append(f"    '{theme_name}': {{")
        
        # Format colors to use MagicColor references if possible
        colors_formatted = []
        for color in theme_config['colors']:
            if color == 'W':
                colors_formatted.append("MagicColor.WHITE.value")
            elif color == 'U':
                colors_formatted.append("MagicColor.BLUE.value")
            elif color == 'B':
                colors_formatted.append("MagicColor.BLACK.value")
            elif color == 'R':
                colors_formatted.append("MagicColor.RED.value")
            elif color == 'G':
                colors_formatted.append("MagicColor.GREEN.value")
            elif color == 'C':
                colors_formatted.append("MagicColor.COLORLESS.value")
            else:
                colors_formatted.append(f"'{color}'")
        
        lines.append(f"        'colors': [{', '.join(colors_formatted)}],")
        lines.append(f"        'strategy': '{theme_config['strategy']}',")
        lines.append(f"        'keywords': {theme_config['keywords']},")
        lines.append(f"        'archetype': Archetype.{theme_config['archetype'].name},")
        lines.append(f"        'scorer': {theme_config['scorer'].__name__},")
        lines.append(f"        'core_card_count': {theme_config['core_card_count']}")
        lines.append("    },")
    
    lines.append("}")
    return "\n".join(lines)
