"""
Main card scoring orchestrator and configuration.

This module provides the CardScorer class that coordinates multiple scoring rules
to evaluate cards for theme appropriateness.
"""

import pandas as pd
from typing import Dict, List, Optional
from .base import ScoringRule, CardContext, ScoreBreakdown
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


class CardScorer:
    """Orchestrates multiple scoring rules to evaluate cards for themes."""
    
    def __init__(self, custom_rules: Optional[List[ScoringRule]] = None):
        """
        Initialize scorer with default rules or custom rule set.
        
        Args:
            custom_rules: Optional list of rules to use instead of defaults
        """
        if custom_rules is not None:
            self.rules = custom_rules
        else:
            self.rules = self._get_default_rules()
    
    def _get_default_rules(self) -> List[ScoringRule]:
        """Get the default set of scoring rules."""
        return [
            KeywordMatchingRule(),
            ArchetypeManaCurveRule(),
            SpecificKeywordRule(),
            TypeBasedRule(),
            ArtifactRule(),
            EquipmentCreatureRule(),
            # TribalSynergyRule(),  # Optional - can be added as needed
            # PowerToughnessRatioRule(),  # Optional - more advanced scoring
            # ColorRequirementRule(),  # Optional - requires mana cost parsing
        ]
    
    def add_rule(self, rule: ScoringRule) -> None:
        """Add a new rule to the scorer."""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a rule by name.
        
        Returns:
            True if rule was found and removed, False otherwise
        """
        original_length = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        return len(self.rules) < original_length
    
    def get_rule(self, rule_name: str) -> Optional[ScoringRule]:
        """Get a rule by name."""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def set_rule_weight(self, rule_name: str, weight: float) -> bool:
        """
        Set the weight for a specific rule.
        
        Returns:
            True if rule was found and weight set, False otherwise
        """
        rule = self.get_rule(rule_name)
        if rule:
            rule.weight = weight
            return True
        return False
    
    def score_card(self, card: pd.Series, theme_config: dict) -> float:
        """Score a card for theme appropriateness using all applicable rules."""
        card_context = CardContext.from_card(card)
        total_score = 0.0
        
        for rule in self.rules:
            total_score += rule.weighted_score(card_context, theme_config)
        
        return total_score
    
    def score_with_breakdown(self, card: pd.Series, theme_config: dict) -> ScoreBreakdown:
        """Get both score and detailed breakdown."""
        card_context = CardContext.from_card(card)
        contributions = {}
        total_score = 0.0
        
        for rule in self.rules:
            if rule.applies(card_context, theme_config):
                rule_score = rule.weighted_score(card_context, theme_config)
                if rule_score != 0:  # Only include rules that contributed
                    contributions[rule.name] = rule_score
                    total_score += rule_score
        
        return ScoreBreakdown(total_score, contributions)
    
    def explain_score(self, card: pd.Series, theme_config: dict) -> Dict[str, float]:
        """Get detailed breakdown of how the score was calculated (legacy method)."""
        breakdown = self.score_with_breakdown(card, theme_config)
        return breakdown.rule_contributions
    
    def list_rules(self) -> List[str]:
        """Get list of all active rule names."""
        return [rule.name for rule in self.rules]
    
    def get_rule_info(self) -> List[Dict[str, str]]:
        """Get detailed information about all rules."""
        return [
            {
                'name': rule.name,
                'description': rule.description,
                'weight': rule.weight
            }
            for rule in self.rules
        ]


# Factory functions for common scorer configurations
def create_default_scorer() -> CardScorer:
    """Create a scorer with the standard rule set."""
    return CardScorer()


def create_aggressive_scorer() -> CardScorer:
    """Create a scorer optimized for aggressive themes."""
    rules = [
        KeywordMatchingRule(),
        ArchetypeManaCurveRule(),
        SpecificKeywordRule(),
        TypeBasedRule(),
        PowerToughnessRatioRule(),  # Include P/T efficiency for aggro
    ]
    
    scorer = CardScorer(rules)
    # Weight mana curve more heavily for aggro
    scorer.set_rule_weight("Archetype Mana Curve", 1.5)
    return scorer


def create_tribal_scorer() -> CardScorer:
    """Create a scorer optimized for tribal themes."""
    rules = [
        KeywordMatchingRule(),
        ArchetypeManaCurveRule(),
        SpecificKeywordRule(),
        TypeBasedRule(),
        TribalSynergyRule(),  # Include tribal bonuses
    ]
    
    scorer = CardScorer(rules)
    # Weight tribal synergy heavily
    scorer.set_rule_weight("Tribal Synergy", 2.0)
    return scorer


def create_equipment_scorer() -> CardScorer:
    """Create a scorer optimized for equipment themes."""
    rules = [
        KeywordMatchingRule(),
        ArchetypeManaCurveRule(),
        SpecificKeywordRule(),
        TypeBasedRule(),
        ArtifactRule(),
        EquipmentCreatureRule(),  # Include equipment-specific creature evaluation
    ]
    
    scorer = CardScorer(rules)
    # Weight equipment rules more heavily
    scorer.set_rule_weight("Artifact/Equipment", 1.5)
    scorer.set_rule_weight("Equipment Creatures", 1.3)
    return scorer


def create_stompy_scorer() -> CardScorer:
    """Create a scorer optimized for stompy themes (big creatures + pump)."""
    rules = [
        KeywordMatchingRule(),
        ArchetypeManaCurveRule(),
        SpecificKeywordRule(),
        TypeBasedRule(),
        PowerToughnessRatioRule(),  # Heavily weight P/T efficiency
    ]
    
    scorer = CardScorer(rules)
    # Weight big creatures and P/T efficiency heavily
    scorer.set_rule_weight("P/T Efficiency", 2.0)
    scorer.set_rule_weight("Keyword Matching", 1.5)  # For pump spells
    return scorer


def create_artifact_scorer() -> CardScorer:
    """Create a scorer optimized for artifact themes."""
    rules = [
        KeywordMatchingRule(),
        ArchetypeManaCurveRule(),
        SpecificKeywordRule(),
        TypeBasedRule(),
        ArtifactRule(),  # Heavy emphasis on artifact cards and synergies
    ]
    
    scorer = CardScorer(rules)
    # Weight artifact rules extremely heavily
    scorer.set_rule_weight("Artifact/Equipment", 3.0)  # Triple weight for artifacts
    scorer.set_rule_weight("Keyword Matching", 2.0)    # Double weight for artifact keywords
    scorer.set_rule_weight("Type-based", 1.5)          # Bonus for artifact creatures
    return scorer


def create_control_scorer() -> CardScorer:
    """Create a scorer optimized for control themes (counterspells, removal, card draw)."""
    rules = [
        KeywordMatchingRule(),      # Heavy emphasis on control keywords
        ArchetypeManaCurveRule(),   # Control prefers higher CMC
        SpecificKeywordRule(),      # Context-aware control terms
        TypeBasedRule(),            # Prefer instants/sorceries over creatures
    ]
    
    scorer = CardScorer(rules)
    # Weight control elements extremely heavily
    scorer.set_rule_weight("Keyword Matching", 3.0)      # Triple weight for control keywords
    scorer.set_rule_weight("Specific Keywords", 2.5)     # Heavy weight for specific control terms  
    scorer.set_rule_weight("Archetype Mana Curve", 1.5)  # Bonus for control mana curve
    scorer.set_rule_weight("Type-based", 1.3)            # Prefer non-creature spells
    return scorer
