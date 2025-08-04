"""
Core deck metrics calculation functions.

This module contains functions for calculating various deck metrics such as
average CMC, card type distribution, keyword density, and overall deck analysis.
"""

import pandas as pd
from typing import Dict, List, Union
from collections import Counter
from .utils import (
    safe_get_column_mean, 
    get_combined_text, 
    calculate_ratio,
    count_keywords_in_text
)


def average_cmc(deck_df: pd.DataFrame) -> float:
    """Calculate average converted mana cost of the deck."""
    return safe_get_column_mean(deck_df, 'CMC', 0.0)


def card_type_distribution(deck_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate the distribution of card types in the deck.
    
    Returns a dictionary mapping type names to their frequency ratios.
    """
    if 'Type' not in deck_df.columns or deck_df.empty:
        return {}
    
    types = deck_df['Type'].fillna('').str.lower()
    type_counts = Counter()
    
    for type_line in types:
        # Split on common delimiters and spaces
        parts = type_line.replace('—', ' ').replace('-', ' ').split()
        for part in parts:
            if part.strip():  # Only count non-empty parts
                type_counts[part.strip()] += 1
    
    total = sum(type_counts.values())
    return {k: calculate_ratio(v, total) for k, v in type_counts.items()}


def keyword_density(deck_df: pd.DataFrame, keywords: List[str]) -> float:
    """
    Calculate density of specific keywords in the deck's Oracle text.
    
    Returns the ratio of found keywords to total keywords searched.
    """
    if not keywords or deck_df.empty:
        return 0.0
    
    text = get_combined_text(deck_df)
    found_keywords = sum(1 for keyword in keywords if keyword.lower() in text)
    return calculate_ratio(found_keywords, len(keywords))


def card_quality_score(deck_df: pd.DataFrame) -> float:
    """
    Calculate average card quality based on power and toughness.
    
    Returns the average combined power and toughness, or 0.0 if unavailable.
    """
    if deck_df.empty or 'Power' not in deck_df.columns or 'Toughness' not in deck_df.columns:
        return 0.0
    
    try:
        power = pd.to_numeric(deck_df['Power'], errors='coerce').fillna(0)
        toughness = pd.to_numeric(deck_df['Toughness'], errors='coerce').fillna(0)
        return (power + toughness).mean()
    except Exception:
        return 0.0


def synergy_score(deck_df: pd.DataFrame, keywords: List[str]) -> float:
    """
    Calculate how well cards in the deck synergize based on shared keywords.
    
    Returns the average number of keyword matches per card.
    """
    if deck_df.empty or not keywords:
        return 0.0
    
    text = get_combined_text(deck_df)
    keyword_matches = count_keywords_in_text(text, keywords)
    return calculate_ratio(keyword_matches, len(deck_df))


def compute_deck_metrics(deck_df: pd.DataFrame, theme_config: Dict) -> Dict[str, Union[int, float]]:
    """
    Compute comprehensive metrics for a single deck.
    
    Args:
        deck_df: DataFrame containing deck cards
        theme_config: Theme configuration dictionary
        
    Returns:
        Dictionary of metric names to values
    """
    # Import here to avoid circular imports
    from .archetypes import archetype_alignment_score
    
    if deck_df is None or deck_df.empty:
        return {
            'avg_cmc': 0.0,
            'keyword_density': 0.0,
            'archetype_alignment': 0.0,
            'card_quality': 0.0,
            'synergy': 0.0,
            'deck_size': 0
        }
    
    metrics = {
        'avg_cmc': average_cmc(deck_df),
        'keyword_density': keyword_density(deck_df, theme_config.get('keywords', [])),
        'archetype_alignment': archetype_alignment_score(deck_df, theme_config),
        'card_quality': card_quality_score(deck_df),
        'synergy': synergy_score(deck_df, theme_config.get('keywords', [])),
        'deck_size': len(deck_df)
    }
    
    # Add card type distribution metrics
    type_distribution = card_type_distribution(deck_df)
    for card_type, ratio in type_distribution.items():
        metrics[f'type_{card_type}'] = ratio
    
    return metrics


def compute_all_deck_metrics(deck_dataframes: Dict[str, pd.DataFrame], 
                           all_themes: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compute metrics for all decks in the collection.
    
    Args:
        deck_dataframes: Dictionary mapping theme names to deck DataFrames
        all_themes: Dictionary mapping theme names to theme configurations
        
    Returns:
        DataFrame with one row per deck and columns for each metric
    """
    rows = []
    
    for theme_name, deck_df in deck_dataframes.items():
        theme_config = all_themes.get(theme_name, {})
        
        row = {'theme': theme_name}
        row.update(compute_deck_metrics(deck_df, theme_config))
        rows.append(row)
    
    return pd.DataFrame(rows)
