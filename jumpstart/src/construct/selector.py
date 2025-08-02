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

            # Apply phase-specific filtering
            if phase == "multicolor" and not self._is_multicolor_appropriate(card, theme_colors):
                continue
            
            # Score the card
            score = self._score_card_for_theme(card, theme_name, theme_config, theme_colors, is_mono, phase, deck_state, constraints)

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
        else:
            # For non-land cards, check the total_non_land constraint
            if not deck_state.can_add_non_land(constraints):
                return False
        
        return True
    
    def _get_specialized_scorer_and_count(self, theme_name: str, theme_config: dict) -> tuple:
        """Get the appropriate specialized scorer and core card count for a theme."""
        # Get scorer function directly from theme config, fallback to default
        scorer_function = theme_config.get('scorer')
        core_card_count = theme_config.get('core_card_count', 3)
        
        # If no scorer function is configured, import and use default
        if scorer_function is None:
            from ..scorer import create_default_scorer
            scorer_function = create_default_scorer
        
        # Call the scorer factory function to create the actual scorer
        return scorer_function(), core_card_count
    
    def _score_card_for_theme(self, card: pd.Series, theme_name: str, theme_config: dict, 
                             theme_colors: Set[str], is_mono: bool, phase: str = "general", 
                             deck_state: DeckState = None, constraints: CardConstraints = None) -> float:
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

        # Creature prioritization boost when below minimum
        if (deck_state and constraints and 
            is_creature_card(card) and 
            deck_state.needs_more_creatures(constraints)):
            base_score += 2.0  # Significant boost to prioritize creatures when below minimum

        # CMC balance factor integration
        if deck_state is not None and constraints is not None:
            base_score = self._add_cmc_balance_factor(base_score, card, deck_state, constraints)

        return base_score

    def _add_cmc_balance_factor(self, card_score: float, card: pd.Series, 
                               deck_state: DeckState, constraints: CardConstraints) -> float:
        """
        Add CMC balance factor to card scoring.
        This encourages selecting cards that bring the deck closer to target CMC.
        """
        # Skip land cards for CMC balancing
        if is_land_card(card):
            return card_score
        
        card_cmc = int(card['CMC'])
        current_avg_cmc = deck_state.avg_cmc
        target_cmc = constraints.target_avg_cmc
        
        # If we have no non-land cards yet, any card is fine
        if deck_state.non_land_count == 0:
            # Slight preference for cards closer to target
            cmc_deviation = abs(card_cmc - target_cmc)
            cmc_bonus = max(0, 1.0 - (cmc_deviation * 0.2))
            return card_score + cmc_bonus
        
        # Calculate what the average would be if we add this card
        projected_total_cmc = deck_state.total_cmc + card_cmc
        projected_count = deck_state.non_land_count + 1
        projected_avg_cmc = projected_total_cmc / projected_count
        
        # Calculate how much this card improves/worsens CMC balance
        current_deviation = abs(current_avg_cmc - target_cmc)
        projected_deviation = abs(projected_avg_cmc - target_cmc)
        
        # CMC balance factor: positive if card improves balance, negative if it worsens it
        cmc_improvement = current_deviation - projected_deviation
        cmc_balance_factor = cmc_improvement * 2.0  # Scale factor for impact
        
        # Additional distribution balance factor
        distribution = deck_state.get_cmc_distribution()
        
        # Check if we need more of this CMC category
        distribution_bonus = 0.0
        if card_cmc <= 2:  # Low CMC
            if distribution['low'] < constraints.min_low_cmc_pct:
                distribution_bonus = 1.0  # Encourage low CMC cards if below minimum
            elif distribution['low'] > constraints.max_low_cmc_pct * 0.8:
                distribution_bonus = -0.5  # Discourage if approaching maximum
        elif card_cmc <= 4:  # Medium CMC
            if distribution['med'] < constraints.min_med_cmc_pct:
                distribution_bonus = 1.0
            elif distribution['med'] > constraints.max_med_cmc_pct * 0.8:
                distribution_bonus = -0.5
        else:  # High CMC
            if distribution['high'] > constraints.max_high_cmc_pct * 0.8:
                distribution_bonus = -1.0  # Strongly discourage high CMC if approaching limit
        
        # Constraint violation check - heavily penalize cards that would violate hard constraints
        violation_penalty = 0.0
        if deck_state.would_violate_cmc_constraints(card_cmc, constraints):
            violation_penalty = -5.0  # Heavy penalty for constraint violations
        
        # Combine all factors
        total_cmc_adjustment = cmc_balance_factor + distribution_bonus + violation_penalty
        
        return card_score + total_cmc_adjustment

    def _get_score_threshold(self, phase: str) -> float:
        """Get minimum score threshold for different phases."""
        thresholds = {
            "core": 6.0,        # High threshold for core card reservation
            "multicolor": 1.0,  # Raised from 0.5 to be more selective
            "general": 0.5,     # Raised from 0.2 to be more selective  
            "completion": 0.2   # Raised from 0.1 for better quality
        }
        return thresholds.get(phase, 0.5)
