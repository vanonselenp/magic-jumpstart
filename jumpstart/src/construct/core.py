"""
Core data structures and constraints for Jumpstart deck construction.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Set, List


@dataclass
class CardConstraints:
    """Encapsulates deck building constraints for a theme."""
    max_creatures: int = 9
    max_lands_mono: int = 1
    max_lands_dual: int = 3
    target_deck_size: int = 13
    total_non_land: int = 12  # Total non-land cards allowed (target_deck_size - lands)
    
    def get_max_lands(self, is_mono_color: bool) -> int:
        return self.max_lands_mono if is_mono_color else self.max_lands_dual
    
    def get_max_non_lands(self) -> int:
        """Get the maximum number of non-land cards allowed."""
        return self.total_non_land


@dataclass
class DeckState:
    """Tracks the current state of a deck being built."""
    cards: List[int]  # Card indices
    creature_count: int = 0
    land_count: int = 0
    land_names: Set[str] = None
    
    def __post_init__(self):
        if self.land_names is None:
            self.land_names = set()
    
    @property
    def size(self) -> int:
        return len(self.cards)
    
    @property
    def non_land_count(self) -> int:
        """Count of non-land cards in the deck."""
        return self.size - self.land_count
    
    def can_add_creature(self, constraints: CardConstraints) -> bool:
        return self.creature_count < constraints.max_creatures
    
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
