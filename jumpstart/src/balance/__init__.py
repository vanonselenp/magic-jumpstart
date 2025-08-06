"""
Balance module for Magic: The Gathering deck analysis.

This module provides functions for calculating deck metrics, archetype alignment,
and other analytical measurements for jumpstart cube construction.
"""

from .metrics import (
    average_cmc,
    card_type_distribution,
    keyword_density,
    card_quality_score,
    synergy_score,
    compute_deck_metrics,
    compute_all_deck_metrics
)

from .archetypes import archetype_alignment_score

__all__ = [
    'average_cmc',
    'card_type_distribution', 
    'keyword_density',
    'card_quality_score',
    'synergy_score',
    'archetype_alignment_score',
    'compute_deck_metrics',
    'compute_all_deck_metrics'
]
