import pandas as pd
import numpy as np
from collections import Counter
from typing import Dict, List, Optional, Union
from .enums import Archetype

# Constants for scoring thresholds
AGGRO_CMC_THRESHOLD = 3
STOMPY_CMC_THRESHOLD = 4
HIGH_CMC_THRESHOLD = 4
MAX_SCORE = 1.0

def _safe_get_column_mean(deck_df: pd.DataFrame, column: str, default: float = 0.0) -> float:
    """Safely get the mean of a column, returning default if column doesn't exist."""
    if column in deck_df.columns:
        return deck_df[column].mean()
    return default

def _get_combined_text(deck_df: pd.DataFrame) -> str:
    """Combine Oracle Text and Type fields into a single searchable string."""
    if deck_df.empty:
        return ""
    
    oracle_text = deck_df.get('Oracle Text', pd.Series()).fillna('')
    type_text = deck_df.get('Type', pd.Series()).fillna('')
    combined = oracle_text + ' ' + type_text
    return ' '.join(combined).lower()

def _count_card_type(deck_df: pd.DataFrame, card_type: str) -> int:
    """Count cards of a specific type (case-insensitive)."""
    if 'Type' not in deck_df.columns or deck_df.empty:
        return 0
    return deck_df['Type'].str.contains(card_type, case=False, na=False).sum()

def _calculate_ratio(count: int, total: int) -> float:
    """Calculate a ratio, returning 0 if total is 0."""
    return count / total if total > 0 else 0.0

def average_cmc(deck_df: pd.DataFrame) -> float:
    """Calculate average converted mana cost of the deck."""
    return _safe_get_column_mean(deck_df, 'CMC', 0.0)

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
    return {k: _calculate_ratio(v, total) for k, v in type_counts.items()}

def keyword_density(deck_df: pd.DataFrame, keywords: List[str]) -> float:
    """
    Calculate density of specific keywords in the deck's Oracle text.
    
    Returns the ratio of found keywords to total keywords searched.
    """
    if not keywords or deck_df.empty:
        return 0.0
    
    text = _get_combined_text(deck_df)
    found_keywords = sum(1 for keyword in keywords if keyword.lower() in text)
    return _calculate_ratio(found_keywords, len(keywords))

def _get_deck_stats(deck_df: pd.DataFrame) -> Dict[str, Union[int, float, str]]:
    """Extract common deck statistics for archetype scoring."""
    if deck_df.empty:
        return {
            'size': 0,
            'avg_cmc': 0.0,
            'text': '',
            'creature_ratio': 0.0,
            'artifact_ratio': 0.0,
            'high_cmc_ratio': 0.0
        }
    
    deck_size = len(deck_df)
    avg_cmc = _safe_get_column_mean(deck_df, 'CMC', 0.0)
    full_text = _get_combined_text(deck_df)
    
    # Count card types
    creature_count = _count_card_type(deck_df, 'creature')
    artifact_count = _count_card_type(deck_df, 'artifact')
    
    # Count high CMC cards
    high_cmc_count = 0
    if 'CMC' in deck_df.columns:
        high_cmc_count = (deck_df['CMC'] > HIGH_CMC_THRESHOLD).sum()
    
    return {
        'size': deck_size,
        'avg_cmc': avg_cmc,
        'text': full_text,
        'creature_ratio': _calculate_ratio(creature_count, deck_size),
        'artifact_ratio': _calculate_ratio(artifact_count, deck_size),
        'high_cmc_ratio': _calculate_ratio(high_cmc_count, deck_size)
    }

def _count_keywords_in_text(text: str, keywords: List[str]) -> int:
    """Count occurrences of keywords in text."""
    return sum(text.count(keyword.lower()) for keyword in keywords)

def _score_aggro_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with aggressive archetype."""
    creature_bonus = stats['creature_ratio']
    cmc_bonus = MAX_SCORE if stats['avg_cmc'] <= AGGRO_CMC_THRESHOLD else 0.5
    return creature_bonus * cmc_bonus

def _score_control_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with control archetype."""
    control_keywords = ['removal', 'destroy', 'counter', 'draw', 'exile']
    control_score = _count_keywords_in_text(stats['text'], control_keywords)
    return min(_calculate_ratio(control_score, stats['size']), MAX_SCORE)

def _score_midrange_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with midrange archetype."""
    creature_component = stats['creature_ratio'] * 0.5
    removal_score = stats['text'].count('removal')
    removal_component = min(_calculate_ratio(removal_score, stats['size']), 0.5) * 0.5
    return creature_component + removal_component

def _score_ramp_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with ramp archetype."""
    ramp_keywords = ['ramp', 'mana', 'search', 'land']
    ramp_score = _count_keywords_in_text(stats['text'], ramp_keywords)
    ramp_component = _calculate_ratio(ramp_score, stats['size'])
    expensive_component = stats['high_cmc_ratio']
    return min(ramp_component + expensive_component, MAX_SCORE)

def _score_tempo_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with tempo archetype."""
    tempo_keywords = ['flying', 'bounce', 'return', 'counter', 'flash']
    tempo_score = _count_keywords_in_text(stats['text'], tempo_keywords)
    return min(_calculate_ratio(tempo_score, stats['size']), MAX_SCORE)

def _score_stompy_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with stompy archetype."""
    creature_bonus = stats['creature_ratio']
    cmc_bonus = MAX_SCORE if stats['avg_cmc'] <= STOMPY_CMC_THRESHOLD else 0.8
    return creature_bonus * cmc_bonus

def _score_tribal_alignment(stats: Dict[str, Union[int, float, str]], keywords: List[str]) -> float:
    """Score alignment with tribal archetype."""
    tribal_score = _count_keywords_in_text(stats['text'], keywords)
    return min(_calculate_ratio(tribal_score, stats['size']), MAX_SCORE)

def _score_artifacts_alignment(stats: Dict[str, Union[int, float, str]]) -> float:
    """Score alignment with artifacts archetype."""
    return stats['artifact_ratio']

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
    stats = _get_deck_stats(deck_df)
    
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
    
    text = _get_combined_text(deck_df)
    keyword_matches = _count_keywords_in_text(text, keywords)
    return _calculate_ratio(keyword_matches, len(deck_df))

def compute_deck_metrics(deck_df: pd.DataFrame, theme_config: Dict) -> Dict[str, Union[int, float]]:
    """
    Compute comprehensive metrics for a single deck.
    
    Args:
        deck_df: DataFrame containing deck cards
        theme_config: Theme configuration dictionary
        
    Returns:
        Dictionary of metric names to values
    """
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
