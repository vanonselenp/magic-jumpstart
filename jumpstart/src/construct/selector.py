"""
Card selection and scoring logic for theme-based deck construction.
"""

import pandas as pd
from typing import Dict, List, Tuple, Set
from .core import DeckState, CardConstraints
from .utils import (
    is_land_card, is_creature_card, get_card_colors, 
    can_land_produce_colors, score_land_for_dual_colors
)


class CardSelector:
    """Handles card selection and scoring logic."""
    
    def __init__(self, oracle_df: pd.DataFrame):
        self.oracle_df = oracle_df
        self.used_cards = set()
    
    def mark_used(self, card_idx: int):
        """Mark a card as used."""
        self.used_cards.add(card_idx)
    
    def mark_unused(self, card_idx: int):
        """Mark a card as unused (for reorganization)."""
        self.used_cards.discard(card_idx)
    
    def get_candidates_for_theme(self, 
                                theme_name: str,
                                theme_config: dict, 
                                deck_state: DeckState,
                                constraints: CardConstraints,
                                phase: str = "general") -> List[Tuple[int, pd.Series, float]]:
        """
        Get candidate cards for a theme with appropriate filtering and scoring.
        
        Args:
            theme_name: Name of the theme being built
            theme_config: Theme configuration
            deck_state: Current deck state
            constraints: Deck building constraints
            phase: Building phase ("multicolor", "general", "completion")
            
        Returns:
            List of (card_idx, card, score) tuples, sorted by score
        """
        theme_colors = set(theme_config['colors'])
        is_mono = len(theme_colors) == 1
        candidates = []
        
        for idx, card in self.oracle_df.iterrows():
            if idx in self.used_cards:
                continue
            
            # Check basic color compatibility
            if not self._is_color_compatible(card, theme_colors, phase):
                continue
            
            # Check constraints
            if not self._check_constraints(card, deck_state, constraints, is_mono, theme_colors):
                continue
            
            # Score the card
            score = self._score_card_for_theme(card, theme_name, theme_config, theme_colors, is_mono, phase)
            
            # Apply phase-specific filtering
            if phase == "multicolor" and not self._is_multicolor_appropriate(card, theme_colors):
                continue
            
            if score >= self._get_score_threshold(phase):
                candidates.append((idx, card, score))
        
        return sorted(candidates, key=lambda x: x[2], reverse=True)
    
    def _is_color_compatible(self, card: pd.Series, theme_colors: Set[str], phase: str) -> bool:
        """Check if card colors are compatible with theme."""
        card_colors = set(get_card_colors(card))
        
        if not card_colors:  # Colorless cards are generally OK
            return True
        
        return card_colors.issubset(theme_colors)
    
    def _is_multicolor_appropriate(self, card: pd.Series, theme_colors: Set[str]) -> bool:
        """Check if card is appropriate for multicolor phase."""
        card_colors = set(get_card_colors(card))
        
        if is_land_card(card):
            return can_land_produce_colors(card, theme_colors)
        
        # For non-lands, require multiple colors or be colorless
        return not card_colors or len(card_colors) >= 2
    
    def _check_constraints(self, card: pd.Series, deck_state: DeckState, 
                          constraints: CardConstraints, is_mono: bool, 
                          theme_colors: Set[str]) -> bool:
        """Check if adding this card would violate constraints."""
        if is_creature_card(card) and not deck_state.can_add_creature(constraints):
            return False
        
        if is_land_card(card):
            if not deck_state.can_add_land(constraints, is_mono, card['name']):
                return False
            
            # For dual-color themes, ensure lands can produce both colors
            if not is_mono and not can_land_produce_colors(card, theme_colors):
                return False
        
        return True
    
    def _get_specialized_scorer_and_count(self, theme_name: str, theme_config: dict) -> tuple:
        """Get the appropriate specialized scorer and core card count for a theme."""
        from ..scorer import (
            create_equipment_scorer, create_tribal_scorer, 
            create_aggressive_scorer, create_stompy_scorer, create_default_scorer
        )
        
        if 'equipment' in theme_name.lower():
            return create_equipment_scorer(), 5  # Reserve more equipment cards
        elif any(tribe in theme_name.lower() for tribe in ['soldiers', 'wizards', 'goblins', 'elves']):
            return create_tribal_scorer(), 4  # Reserve key tribal cards
        elif theme_config.get('archetype') == 'Stompy':
            return create_stompy_scorer(), 3  # Reserve key stompy creatures
        elif theme_config.get('archetype') == 'Aggressive':
            return create_aggressive_scorer(), 3  # Reserve key aggressive cards
        else:
            return create_default_scorer(), 3  # Standard reservation
    
    def _score_card_for_theme(self, card: pd.Series, theme_name: str, theme_config: dict, 
                             theme_colors: Set[str], is_mono: bool, phase: str = "general") -> float:
        """Score a card for theme appropriateness using specialized scorers."""
        if is_land_card(card):
            return score_land_for_dual_colors(card, theme_colors)
        
        # For core phase, we use specialized scorers in the reservation method
        # For other phases, use enhanced scoring with specialization
        if phase == "core":
            from ..scorer import score_card_for_theme
            base_score = score_card_for_theme(card, theme_config)
        else:
            # Use specialized scoring based on theme type
            from ..scorer import score_card_for_theme
            
            scorer, _ = self._get_specialized_scorer_and_count(theme_name, theme_config)
            
            # Use scorer if it's not the default scorer, otherwise use standard scoring
            if scorer.__class__.__name__ != 'CardScorer' or hasattr(scorer, '_is_specialized'):
                base_score = scorer.score_card(card, theme_config)
            else:
                base_score = score_card_for_theme(card, theme_config)
        
        # Color preference bonus
        card_colors = set(get_card_colors(card))
        if card_colors == theme_colors:
            base_score += 0.5
        elif card_colors and card_colors.issubset(theme_colors):
            base_score += 0.3
        elif not card_colors:  # Colorless
            base_score += 0.1
        
        return base_score
    
    def _get_score_threshold(self, phase: str) -> float:
        """Get minimum score threshold for different phases."""
        thresholds = {
            "core": 6.0,        # High threshold for core card reservation
            "multicolor": 1.0,  # Raised from 0.5 to be more selective
            "general": 0.5,     # Raised from 0.2 to be more selective  
            "completion": 0.2   # Raised from 0.1 for better quality
        }
        return thresholds.get(phase, 0.5)
