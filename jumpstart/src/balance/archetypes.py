"""
Archetype-specific scoring functions.

This module contains functions for scoring how well decks align with specific
Magic: The Gathering archetypes like Aggro, Control, Midrange, etc.
"""

import pandas as pd
from typing import Dict, List, Optional, Union
from ..enums import Archetype
from .utils import (
    get_deck_stats,
    count_keywords_in_text,
    calculate_ratio,
    MAX_SCORE,
    AGGRO_CMC_THRESHOLD,
    STOMPY_CMC_THRESHOLD
)


def _score_aggro_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with aggressive archetype."""
    creature_bonus = stats['creature_ratio']
    cmc_bonus = MAX_SCORE if stats['avg_cmc'] <= AGGRO_CMC_THRESHOLD else 0.5
    return creature_bonus * cmc_bonus


def _score_control_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with control archetype."""
    control_keywords = ['removal', 'destroy', 'counter', 'draw', 'exile']
    control_score = count_keywords_in_text(stats['text'], control_keywords)
    return min(calculate_ratio(control_score, stats['size']), MAX_SCORE)


def _score_midrange_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with midrange archetype."""
    creature_component = stats['creature_ratio'] * 0.5
    removal_score = stats['text'].count('removal')
    removal_component = min(calculate_ratio(removal_score, stats['size']), 0.5) * 0.5
    return creature_component + removal_component


def _score_ramp_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with ramp archetype."""
    ramp_keywords = ['ramp', 'mana', 'search', 'land']
    ramp_score = count_keywords_in_text(stats['text'], ramp_keywords)
    ramp_component = calculate_ratio(ramp_score, stats['size'])
    expensive_component = stats['high_cmc_ratio']
    return min(ramp_component + expensive_component, MAX_SCORE)


def _score_tempo_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with tempo archetype."""
    tempo_keywords = ['flying', 'bounce', 'return', 'counter', 'flash']
    tempo_score = count_keywords_in_text(stats['text'], tempo_keywords)
    return min(calculate_ratio(tempo_score, stats['size']), MAX_SCORE)


def _score_stompy_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with stompy archetype."""
    creature_bonus = stats['creature_ratio']
    cmc_bonus = MAX_SCORE if stats['avg_cmc'] <= STOMPY_CMC_THRESHOLD else 0.8
    return creature_bonus * cmc_bonus


def _score_tribal_alignment(stats: Dict[str, Union[int, float, str]], keywords: List[str]) -> float:
    """Score alignment with tribal archetype."""
    tribal_score = count_keywords_in_text(stats['text'], keywords)
    return min(calculate_ratio(tribal_score, stats['size']), MAX_SCORE)


def _score_artifacts_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with artifacts archetype."""
    return stats['artifact_ratio']


def _normalize_archetype(archetype) -> Optional[Archetype]:
    """Convert archetype input to Archetype enum."""
    if isinstance(archetype, Archetype):
        return archetype
    
    if archetype is None:
        return None
        
    # Try to match string to enum
    archetype_str = str(archetype).upper()
    try:
        return Archetype[archetype_str]
    except (KeyError, AttributeError):
        return None


def archetype_alignment_score(deck_df: pd.DataFrame, theme_config: Dict) -> float:
    """
    Calculate how well a deck aligns with its intended archetype.
    
    Args:
        deck_df: DataFrame containing deck cards
        theme_config: Configuration dictionary containing 'archetype' and 'keywords'
    
    Returns:
        Score between 0 and 1, where 1 indicates perfect alignment.
    """
    if deck_df is None or deck_df.empty:
        return 0.0
    
    archetype = theme_config.get('archetype')
    keywords = theme_config.get('keywords', [])
    
    # Normalize archetype to enum value
    archetype_type = _normalize_archetype(archetype)
    if archetype_type is None:
        return 0.0
    
    # Get deck statistics once
    stats = get_deck_stats(deck_df)
    
    # Route to appropriate scoring function
    scoring_functions = {
        Archetype.AGGRO: _score_aggro_alignment,
        Archetype.CONTROL: _score_control_alignment,
        Archetype.MIDRANGE: _score_midrange_alignment,
        Archetype.RAMP: _score_ramp_alignment,
        Archetype.TEMPO: _score_tempo_alignment,
        Archetype.STOMPY: _score_stompy_alignment,
        Archetype.TRIBAL: lambda stats: _score_tribal_alignment(stats, keywords),
        Archetype.ARTIFACTS: _score_artifacts_alignment,
    }
    
    scoring_function = scoring_functions.get(archetype_type)
    if scoring_function:
        return scoring_function(stats)
    
    return 0.0
