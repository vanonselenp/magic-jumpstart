"""
Base classes and data structures for the card scoring system.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict
from abc import ABC, abstractmethod


@dataclass
class CardContext:
    """Encapsulates all card information needed for scoring."""
    card: pd.Series
    cmc: int
    power: int
    toughness: int
    oracle_text: str
    card_type: str
    card_name: str
    searchable_text: str
    
    @classmethod
    def from_card(cls, card: pd.Series) -> 'CardContext':
        """Create CardContext from a pandas Series card."""
        cmc = card.get('CMC', 0) if pd.notna(card.get('CMC', 0)) else 0
        power = card.get('Power', 0) if pd.notna(card.get('Power', 0)) else 0
        toughness = card.get('Toughness', 0) if pd.notna(card.get('Toughness', 0)) else 0
        oracle_text = str(card['Oracle Text']).lower() if pd.notna(card['Oracle Text']) else ""
        card_type = str(card['Type']).lower() if pd.notna(card['Type']) else ""
        card_name = str(card['name']).lower() if pd.notna(card['name']) else ""
        searchable_text = f"{oracle_text} {card_type} {card_name}"
        
        return cls(
            card=card,
            cmc=cmc,
            power=power,
            toughness=toughness,
            oracle_text=oracle_text,
            card_type=card_type,
            card_name=card_name,
            searchable_text=searchable_text
        )


class ScoringRule(ABC):
    """Abstract base class for scoring rules."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.weight = 1.0  # Future feature: rule weighting
    
    @abstractmethod
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        """Check if this rule applies to the given card and theme."""
        pass
    
    @abstractmethod
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        """Calculate the score contribution for this rule."""
        pass
    
    def weighted_score(self, card_context: CardContext, theme_config: dict) -> float:
        """Get the weighted score for this rule."""
        if not self.applies(card_context, theme_config):
            return 0.0
        
        return self.score(card_context, theme_config) * self.weight


@dataclass 
class ScoreBreakdown:
    """Detailed breakdown of scoring contributions."""
    total_score: float
    rule_contributions: Dict[str, float]
    
    def __str__(self) -> str:
        """String representation of score breakdown."""
        lines = [f"Total Score: {self.total_score:.2f}"]
        
        if self.rule_contributions:
            lines.append("Rule Contributions:")
            for rule_name, contribution in self.rule_contributions.items():
                lines.append(f"  • {rule_name}: {contribution:+.2f}")
        else:
            lines.append("No scoring rules contributed")
        
        return "\n".join(lines)
