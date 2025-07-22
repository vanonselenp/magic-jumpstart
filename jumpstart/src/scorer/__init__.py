"""
Card scoring system for Magic: The Gathering Jumpstart cube construction.

This package provides a modular, rule-based system for evaluating how well
cards fit specific theme requirements. The system is designed to be:

- Modular: Each rule is independent and focused
- Extensible: Easy to add new rules without breaking existing ones  
- Transparent: Detailed score breakdowns show why cards are selected
- Configurable: Rules can be weighted, enabled, or disabled as needed

Basic usage:
    from src.scorer import score_card_for_theme, explain_card_score
    
    score = score_card_for_theme(card, theme_config)
    breakdown = explain_card_score(card, theme_config)

Advanced usage:
    from src.scorer import CardScorer, create_equipment_scorer
    
    scorer = create_equipment_scorer()
    breakdown = scorer.score_with_breakdown(card, theme_config)
"""

from .base import CardContext, ScoringRule, ScoreBreakdown
from .rules import (
    KeywordMatchingRule,
    ArchetypeManaCurveRule,
    SpecificKeywordRule, 
    TypeBasedRule,
    ArtifactRule,
    EquipmentCreatureRule,
    TribalSynergyRule,
    PowerToughnessRatioRule,
    ColorRequirementRule
)
from .scorer import (
    CardScorer,
    create_default_scorer,
    create_aggressive_scorer,
    create_tribal_scorer,
    create_equipment_scorer
)

import pandas as pd
from typing import Dict

# Global default scorer instance
_default_scorer = create_default_scorer()


def score_card_for_theme(card: pd.Series, theme_config: dict) -> float:
    """
    Score a card based on how well it fits a theme using rule-based system.
    
    This is the main entry point that maintains compatibility with existing code.
    Uses the default scorer configuration.
    
    Args:
        card: Pandas Series containing card data
        theme_config: Dictionary with theme configuration (keywords, archetype, etc.)
        
    Returns:
        Float score indicating theme appropriateness
    """
    return _default_scorer.score_card(card, theme_config)


def explain_card_score(card: pd.Series, theme_config: dict) -> Dict[str, float]:
    """
    Get detailed breakdown of how a card's score was calculated.
    
    Args:
        card: Pandas Series containing card data
        theme_config: Dictionary with theme configuration
        
    Returns:
        Dictionary mapping rule names to their score contributions
    """
    return _default_scorer.explain_score(card, theme_config)


def get_score_breakdown(card: pd.Series, theme_config: dict) -> ScoreBreakdown:
    """
    Get a complete ScoreBreakdown object with total score and rule contributions.
    
    Args:
        card: Pandas Series containing card data  
        theme_config: Dictionary with theme configuration
        
    Returns:
        ScoreBreakdown object with total score and detailed contributions
    """
    return _default_scorer.score_with_breakdown(card, theme_config)


def configure_default_scorer(scorer: CardScorer) -> None:
    """
    Replace the default scorer with a custom configuration.
    
    This allows global configuration of the scoring system without
    changing all the call sites.
    
    Args:
        scorer: CardScorer instance to use as the new default
    """
    global _default_scorer
    _default_scorer = scorer


def get_default_scorer() -> CardScorer:
    """Get the current default scorer instance."""
    return _default_scorer


# Export all the main classes and functions
__all__ = [
    # Base classes
    'CardContext',
    'ScoringRule', 
    'ScoreBreakdown',
    
    # Individual rules
    'KeywordMatchingRule',
    'ArchetypeManaCurveRule',
    'SpecificKeywordRule',
    'TypeBasedRule', 
    'ArtifactRule',
    'EquipmentCreatureRule',
    'TribalSynergyRule',
    'PowerToughnessRatioRule',
    'ColorRequirementRule',
    
    # Main scorer
    'CardScorer',
    
    # Factory functions
    'create_default_scorer',
    'create_aggressive_scorer',
    'create_tribal_scorer', 
    'create_equipment_scorer',
    
    # Main API functions
    'score_card_for_theme',
    'explain_card_score',
    'get_score_breakdown',
    'configure_default_scorer',
    'get_default_scorer',
]
