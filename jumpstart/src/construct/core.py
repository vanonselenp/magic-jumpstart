"""
Core data structures and constraints for Jumpstart deck construction.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Set, List


@dataclass
class CardConstraints:
    """Encapsulates deck building constraints for a theme."""
    min_creatures: int = 3
    max_creatures: int = 9
    max_lands_mono: int = 1
    max_lands_dual: int = 3
    target_deck_size: int = 13
    total_non_land: int = 12  # Total non-land cards allowed (target_deck_size - lands)
    
    # CMC balancing constraints
    target_avg_cmc: float = 2.42  # Target average CMC for balanced gameplay
    cmc_tolerance: float = 0.3   # Allowed deviation from target CMC
    min_low_cmc_pct: float = 0.4   # Minimum % of cards with CMC 0-2
    max_low_cmc_pct: float = 0.6   # Maximum % of cards with CMC 0-2
    min_med_cmc_pct: float = 0.25  # Minimum % of cards with CMC 3-4
    max_med_cmc_pct: float = 0.4   # Maximum % of cards with CMC 3-4
    max_high_cmc_pct: float = 0.25 # Maximum % of cards with CMC 5+
    
    def get_max_lands(self, is_mono_color: bool) -> int:
        return self.max_lands_mono if is_mono_color else self.max_lands_dual
    
    def get_max_non_lands(self) -> int:
        """Get the maximum number of non-land cards allowed."""
        return self.total_non_land
    
    def get_cmc_range(self) -> tuple:
        """Get the acceptable CMC range."""
        return (self.target_avg_cmc - self.cmc_tolerance, 
                self.target_avg_cmc + self.cmc_tolerance)


@dataclass
class DeckState:
    """Tracks the current state of a deck being built."""
    cards: List[int]  # Card indices
    creature_count: int = 0
    land_count: int = 0
    land_names: Set[str] = None
    total_cmc: int = 0  # Sum of CMC for all non-land cards
    cmc_counts: dict = None  # Count of cards in each CMC category
    
    def __post_init__(self):
        if self.land_names is None:
            self.land_names = set()
        if self.cmc_counts is None:
            self.cmc_counts = {'low': 0, 'med': 0, 'high': 0}  # 0-2, 3-4, 5+
    
    @property
    def size(self) -> int:
        return len(self.cards)
    
    @property
    def non_land_count(self) -> int:
        """Count of non-land cards in the deck."""
        return self.size - self.land_count
    
    @property
    def avg_cmc(self) -> float:
        """Calculate current average CMC of non-land cards."""
        non_land_count = self.non_land_count
        return self.total_cmc / non_land_count if non_land_count > 0 else 0.0
    
    def can_add_creature(self, constraints: CardConstraints) -> bool:
        return self.creature_count < constraints.max_creatures
    
    def get_cmc_distribution(self) -> dict:
        """Get current CMC distribution percentages."""
        total = sum(self.cmc_counts.values())
        if total == 0:
            return {'low': 0.0, 'med': 0.0, 'high': 0.0}
        return {
            'low': self.cmc_counts['low'] / total,
            'med': self.cmc_counts['med'] / total,
            'high': self.cmc_counts['high'] / total
        }
    
    def would_violate_cmc_constraints(self, card_cmc: int, constraints: CardConstraints) -> bool:
        """Check if adding a card with given CMC would violate constraints."""
        if self.non_land_count == 0:
            return False  # First card can't violate constraints
        
        # Calculate what the new average would be
        new_total_cmc = self.total_cmc + card_cmc
        new_non_land_count = self.non_land_count + 1
        new_avg_cmc = new_total_cmc / new_non_land_count
        
        # Check if it would exceed CMC range
        min_cmc, max_cmc = constraints.get_cmc_range()
        if new_avg_cmc < min_cmc or new_avg_cmc > max_cmc:
            return True
        
        # Check CMC distribution constraints
        new_cmc_counts = self.cmc_counts.copy()
        if card_cmc <= 2:
            new_cmc_counts['low'] += 1
        elif card_cmc <= 4:
            new_cmc_counts['med'] += 1
        else:
            new_cmc_counts['high'] += 1
        
        total_cards = sum(new_cmc_counts.values())
        new_dist = {k: v / total_cards for k, v in new_cmc_counts.items()}
        
        # Check distribution constraints
        if (new_dist['low'] > constraints.max_low_cmc_pct or
            new_dist['med'] > constraints.max_med_cmc_pct or
            new_dist['high'] > constraints.max_high_cmc_pct):
            return True
        
        return False
    
    def needs_more_creatures(self, constraints: CardConstraints) -> bool:
        """Check if we need more creatures to meet the minimum requirement."""
        return self.creature_count < constraints.min_creatures
    
    def can_add_land(self, constraints: CardConstraints, is_mono: bool, land_name: str) -> bool:
        max_lands = constraints.get_max_lands(is_mono)
        return (self.land_count < max_lands and 
                land_name not in self.land_names)
    
    def can_add_non_land(self, constraints: CardConstraints) -> bool:
        """Check if we can add another non-land card."""
        return self.non_land_count < constraints.get_max_non_lands()
    
    def add_card(self, card_idx: int, card: pd.Series):
        """Add a card to the deck and update counters."""
        from .utils import is_creature_card, is_land_card
        
        self.cards.append(card_idx)
        
        if is_creature_card(card):
            self.creature_count += 1
        elif is_land_card(card):
            self.land_count += 1
            self.land_names.add(card['name'])
        
        # Update CMC tracking for non-land cards
        if not is_land_card(card):
            card_cmc = int(card['CMC'])
            self.total_cmc += card_cmc
            
            # Update CMC distribution counts
            if card_cmc <= 2:
                self.cmc_counts['low'] += 1
            elif card_cmc <= 4:
                self.cmc_counts['med'] += 1
            else:
                self.cmc_counts['high'] += 1
