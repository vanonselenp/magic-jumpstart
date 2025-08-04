"""
Utility functions for deck analysis.

This module contains helper functions for data processing, text analysis,
and common calculations used across the balance module.
"""

import pandas as pd
from typing import Dict, List, Union
from collections import Counter

# Constants for scoring thresholds
AGGRO_CMC_THRESHOLD = 3
STOMPY_CMC_THRESHOLD = 4
HIGH_CMC_THRESHOLD = 4
MAX_SCORE = 1.0


def safe_get_column_mean(deck_df: pd.DataFrame, column: str, default: float = 0.0) -> float:
    """Safely get the mean of a column, returning default if column doesn't exist."""
    if column in deck_df.columns:
        return deck_df[column].mean()
    return default


def get_combined_text(deck_df: pd.DataFrame) -> str:
    """Combine Oracle Text and Type fields into a single searchable string."""
    if deck_df.empty:
        return ""
    
    oracle_text = deck_df.get('Oracle Text', pd.Series()).fillna('')
    type_text = deck_df.get('Type', pd.Series()).fillna('')
    combined = oracle_text + ' ' + type_text
    return ' '.join(combined).lower()


def count_card_type(deck_df: pd.DataFrame, card_type: str) -> int:
    """Count cards of a specific type (case-insensitive)."""
    if 'Type' not in deck_df.columns or deck_df.empty:
        return 0
    return deck_df['Type'].str.contains(card_type, case=False, na=False).sum()


def calculate_ratio(count: int, total: int) -> float:
    """Calculate a ratio, returning 0 if total is 0."""
    return count / total if total > 0 else 0.0


def count_keywords_in_text(text: str, keywords: List[str]) -> int:
    """Count occurrences of keywords in text."""
    return sum(text.count(keyword.lower()) for keyword in keywords)


def get_deck_stats(deck_df: pd.DataFrame) -> Dict[str, Union[int, float, str]]:
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
    avg_cmc = safe_get_column_mean(deck_df, 'CMC', 0.0)
    full_text = get_combined_text(deck_df)
    
    # Count card types
    creature_count = count_card_type(deck_df, 'creature')
    artifact_count = count_card_type(deck_df, 'artifact')
    
    # Count high CMC cards
    high_cmc_count = 0
    if 'CMC' in deck_df.columns:
        high_cmc_count = (deck_df['CMC'] > HIGH_CMC_THRESHOLD).sum()
    
    return {
        'size': deck_size,
        'avg_cmc': avg_cmc,
        'text': full_text,
        'creature_ratio': calculate_ratio(creature_count, deck_size),
        'artifact_ratio': calculate_ratio(artifact_count, deck_size),
        'high_cmc_ratio': calculate_ratio(high_cmc_count, deck_size)
    }
