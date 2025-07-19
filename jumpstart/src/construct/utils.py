"""
Utility functions for card type checking, color analysis, and land evaluation.
"""

import pandas as pd
from typing import List, Set


def is_land_card(card: pd.Series) -> bool:
    """Check if a card is a land."""
    card_type = str(card['Type']).lower() if pd.notna(card['Type']) else ""
    return 'land' in card_type


def is_creature_card(card: pd.Series) -> bool:
    """Check if a card is a creature."""
    card_type = str(card['Type']).lower() if pd.notna(card['Type']) else ""
    return 'creature' in card_type


def get_card_colors(card: pd.Series) -> List[str]:
    """Get the colors of a card."""
    color = str(card['Color']) if pd.notna(card['Color']) else ""
    if not color or color == 'C':  # Colorless
        return []
    return list(color)


def can_land_produce_colors(land_card: pd.Series, required_colors: set) -> bool:
    """
    Check if a land can produce all the required colors for a dual-color theme.
    This function checks for DIRECT mana production, not fetch/cycling abilities.
    """
    if not is_land_card(land_card):
        return False
    
    oracle_text = str(land_card.get('Oracle Text', '')).lower()
    
    # Get the land's color identity first
    land_colors = set(get_card_colors(land_card))
    
    # Check for direct mana production in oracle text
    directly_producible = set()
    
    # Look for mana production patterns like "{T}: Add {U}" or "{T}: Add {U} or {B}"
    if '{t}: add' in oracle_text:
        for color in ['W', 'U', 'B', 'R', 'G']:
            color_symbol = '{' + color.lower() + '}'
            # Check if this color appears in a mana production ability (not cycling cost)
            if color_symbol in oracle_text:
                # Make sure it's in a mana production line, not a cycling cost
                lines = oracle_text.split('|')
                for line in lines:
                    line = line.strip()
                    if '{t}: add' in line and color_symbol in line:
                        directly_producible.add(color)
                        break
    
    # If land has color identity, it can produce those colors
    if land_colors:
        directly_producible.update(land_colors)
    
    # For basic lands, add their inherent color
    basic_land_types = {
        'plains': 'W', 'island': 'U', 'swamp': 'B', 
        'mountain': 'R', 'forest': 'G'
    }
    
    for basic_type, color in basic_land_types.items():
        if basic_type in oracle_text and f'basic {basic_type}' in oracle_text:
            directly_producible.add(color)
    
    # Check if this land can directly produce all required colors
    return required_colors.issubset(directly_producible)


def score_land_for_dual_colors(land_card: pd.Series, required_colors: set) -> float:
    """
    Score a land based on how well it supports a dual-color theme.
    Higher scores are given to lands that can produce both colors.
    """
    if not is_land_card(land_card):
        return 0.0
    
    if len(required_colors) == 1:
        # For mono-color themes, any land that produces the color is good
        if can_land_produce_colors(land_card, required_colors):
            return 1.0
        return 0.0
    
    # For dual-color themes, prioritize lands that can produce both colors
    if not can_land_produce_colors(land_card, required_colors):
        return 0.0  # Can't produce both colors
    
    oracle_text = str(land_card.get('Oracle Text', '')).lower()
    
    # Check for DIRECT mana production (not just fetchable)
    directly_producible_colors = set()
    
    # Look for explicit mana symbols in the oracle text (e.g., {U}, {B})
    for color in ['W', 'U', 'B', 'R', 'G']:
        color_symbol = '{' + color.lower() + '}'
        if color_symbol in oracle_text:
            directly_producible_colors.add(color)
    
    # Check for color identity from the card's colors
    land_colors = set(get_card_colors(land_card))
    if land_colors:
        directly_producible_colors.update(land_colors)
    
    # IMPORTANT: Don't count lands that only fetch basics as direct producers
    if not directly_producible_colors:
        # This is likely a utility land (cycling, fetch, etc.)
        if '{c}' in oracle_text or 'add {c}' in oracle_text:
            return 0.1  # Minimal score for utility
    
    # Score based on direct color production efficiency
    if not required_colors.issubset(directly_producible_colors):
        # Check if it's a fetch/utility land that can get the colors
        can_fetch_both = True
        for color in required_colors:
            color_names = {
                'W': 'plains', 'U': 'island', 'B': 'swamp', 
                'R': 'mountain', 'G': 'forest'
            }
            if color in color_names and color_names[color] not in oracle_text:
                can_fetch_both = False
                break
        
        if can_fetch_both and ('search' in oracle_text or 'cycling' in oracle_text):
            return 0.3  # Low score for utility lands
        else:
            return 0.0  # Can't help with mana fixing
    
    # Land can directly produce both colors - calculate score
    score = 2.0  # Base score for direct dual-color production
    
    # Bonus for perfect dual land match
    if directly_producible_colors == required_colors:
        score += 2.0  # Exactly the colors we need
    elif len(directly_producible_colors) <= 3:
        score += 1.0  # Good but not perfect
    else:
        score += 0.5  # Many colors (less focused)
    
    # Penalty for enters-tapped lands (slower)
    if 'enters tapped' in oracle_text or 'enters the battlefield tapped' in oracle_text:
        score -= 0.3  # Small penalty for being slow
    
    # Bonus for utility abilities
    if 'cycling' in oracle_text:
        score += 0.2
    if 'draw a card' in oracle_text:
        score += 0.1
    
    return score


def get_card_type_display(card: pd.Series) -> str:
    """Get a clean display name for card type."""
    card_type = str(card['Type'])
    if ' - ' in card_type:
        return card_type.split(' - ')[0]
    return card_type
