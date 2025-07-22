"""
Refactored Jumpstart Cube Deck Construction

This module provides a cleaner, more modular approach to constructing jumpstart decks
by separating concerns into focused classes and functions.
"""

import pandas as pd
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from .consts import ALL_THEMES, MONO_COLOR_THEMES, DUAL_COLOR_THEMES


@dataclass
class CardConstraints:
    """Encapsulates deck building constraints for a theme."""
    max_creatures: int = 9
    max_lands_mono: int = 1
    max_lands_dual: int = 3
    target_deck_size: int = 13
    
    def get_max_lands(self, is_mono_color: bool) -> int:
        return self.max_lands_mono if is_mono_color else self.max_lands_dual


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
    
    def can_add_creature(self, constraints: CardConstraints) -> bool:
        return self.creature_count < constraints.max_creatures
    
    def can_add_land(self, constraints: CardConstraints, is_mono: bool, land_name: str) -> bool:
        max_lands = constraints.get_max_lands(is_mono)
        return (self.land_count < max_lands and 
                land_name not in self.land_names)
    
    def add_card(self, card_idx: int, card: pd.Series):
        """Add a card to the deck and update counters."""
        self.cards.append(card_idx)
        
        if is_creature_card(card):
            self.creature_count += 1
        elif is_land_card(card):
            self.land_count += 1
            self.land_names.add(card['name'])


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
                                theme_config: dict, 
                                deck_state: DeckState,
                                constraints: CardConstraints,
                                phase: str = "general") -> List[Tuple[int, pd.Series, float]]:
        """
        Get candidate cards for a theme with appropriate filtering and scoring.
        
        Args:
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
            score = self._score_card_for_theme(card, theme_config, theme_colors, is_mono)
            
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
    
    def _score_card_for_theme(self, card: pd.Series, theme_config: dict, 
                             theme_colors: Set[str], is_mono: bool) -> float:
        """Score a card for theme appropriateness."""
        if is_land_card(card):
            return score_land_for_dual_colors(card, theme_colors)
        
        # Use existing keyword matching logic
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
            "multicolor": 0.5,
            "general": 0.2,
            "completion": 0.1
        }
        return thresholds.get(phase, 0.2)


class DeckBuilder:
    """Main deck building orchestrator."""
    
    def __init__(self, oracle_df: pd.DataFrame, constraints: CardConstraints = None):
        self.oracle_df = oracle_df
        self.constraints = constraints or CardConstraints()
        self.selector = CardSelector(oracle_df)
        self.decks = {}  # theme_name -> DeckState
    
    def build_all_decks(self) -> Dict[str, pd.DataFrame]:
        """Build all jumpstart decks using a clean phase-based approach."""
        self._initialize_decks()
        
        print("🏗️ CONSTRUCTING JUMPSTART DECKS")
        print("=" * 50)
        
        # Phase 1: Multicolor cards for dual-color themes
        self._build_multicolor_phase()
        
        # Phase 2: General card assignment
        self._build_general_phase()
        
        # Phase 3: Complete remaining decks
        self._build_completion_phase()
        
        # Phase 4: Validate and fix constraint violations
        self._validate_and_fix_constraints()
        
        # Phase 5: Final summary and optional reorganization
        result = self._convert_to_dataframes()
        
        # Check if we need reorganization for incomplete decks
        incomplete_count = sum(1 for df in result.values() if len(df) < self.constraints.target_deck_size)
        if incomplete_count > 0:
            print(f"\n🔄 Attempting reorganization for {incomplete_count} incomplete decks...")
            result = self._attempt_reorganization(result)
        
        return result
    
    def _initialize_decks(self):
        """Initialize empty deck states for all themes."""
        for theme_name in ALL_THEMES:
            self.decks[theme_name] = DeckState(cards=[])
    
    def _build_multicolor_phase(self):
        """Phase 1: Assign multicolor cards to dual-color themes."""
        print("\n📦 Phase 1: Multicolor card assignment")
        
        for theme_name, theme_config in DUAL_COLOR_THEMES.items():
            self._build_deck_phase(theme_name, theme_config, "multicolor")
    
    def _build_general_phase(self):
        """Phase 2: General card assignment for all themes."""
        print("\n📦 Phase 2: General card assignment")
        
        for theme_name, theme_config in ALL_THEMES.items():
            if self.decks[theme_name].size < self.constraints.target_deck_size:
                self._build_deck_phase(theme_name, theme_config, "general")
    
    def _build_completion_phase(self):
        """Phase 3: Complete remaining incomplete decks."""
        print("\n📦 Phase 3: Completion phase")
        
        incomplete_themes = [
            (name, state) for name, state in self.decks.items() 
            if state.size < self.constraints.target_deck_size
        ]
        
        # Sort by completion level (most complete first)
        incomplete_themes.sort(key=lambda x: x[1].size, reverse=True)
        
        for theme_name, _ in incomplete_themes:
            theme_config = ALL_THEMES[theme_name]
            self._build_deck_phase(theme_name, theme_config, "completion")
    
    def _build_deck_phase(self, theme_name: str, theme_config: dict, phase: str):
        """Build cards for a specific theme in a specific phase."""
        deck_state = self.decks[theme_name]
        cards_needed = self.constraints.target_deck_size - deck_state.size
        
        if cards_needed <= 0:
            return
        
        print(f"\n🎯 {phase.title()} phase: {theme_name} ({deck_state.size}/{self.constraints.target_deck_size})")
        
        candidates = self.selector.get_candidates_for_theme(
            theme_config, deck_state, self.constraints, phase
        )
        
        added_count = 0
        theme_colors = set(theme_config['colors'])
        is_mono = len(theme_colors) == 1
        
        for card_idx, card, score in candidates:
            if added_count >= cards_needed:
                break
            
            # Re-check constraints before adding each card since deck state changes
            if not self.selector._check_constraints(card, deck_state, self.constraints, is_mono, theme_colors):
                # Provide specific feedback about why the card was skipped
                if is_creature_card(card) and not deck_state.can_add_creature(self.constraints):
                    print(f"  ⚠️  Skipping {card['name']}: would exceed creature limit ({deck_state.creature_count}/9)")
                elif is_land_card(card) and not deck_state.can_add_land(self.constraints, is_mono, card['name']):
                    print(f"  ⚠️  Skipping {card['name']}: would exceed land limit")
                elif is_land_card(card) and not is_mono and not can_land_produce_colors(card, theme_colors):
                    print(f"  ⚠️  Skipping {card['name']}: cannot produce required colors")
                else:
                    print(f"  ⚠️  Skipping {card['name']}: constraint violation")
                continue

            deck_state.add_card(card_idx, card)
            self.selector.mark_used(card_idx)
            added_count += 1
            
            print(f"  ✅ Added: {card['name']} (Score: {score:.1f}) [{self._get_card_type_display(card)}]")
        
        print(f"  📊 {phase.title()} complete: {deck_state.size}/{self.constraints.target_deck_size} cards")
    
    def _get_card_type_display(self, card: pd.Series) -> str:
        """Get a clean display name for card type."""
        card_type = str(card['Type'])
        if ' - ' in card_type:
            return card_type.split(' - ')[0]
        return card_type
    
    def _validate_and_fix_constraints(self):
        """Validate all decks meet constraints and fix violations."""
        print("\n📦 Phase 4: Constraint validation")
        
        violations_found = 0
        for theme_name, deck_state in self.decks.items():
            if deck_state.size == 0:
                continue
            
            theme_config = ALL_THEMES[theme_name]
            is_mono = len(theme_config['colors']) == 1
            max_lands = self.constraints.get_max_lands(is_mono)
            
            violations = []
            if deck_state.creature_count > self.constraints.max_creatures:
                violations.append(f"creatures: {deck_state.creature_count}/{self.constraints.max_creatures}")
            if deck_state.land_count > max_lands:
                violations.append(f"lands: {deck_state.land_count}/{max_lands}")
            
            if violations:
                violations_found += 1
                print(f"  ⚠️  {theme_name}: VIOLATION - {', '.join(violations)}")
                self._fix_constraint_violations(theme_name, deck_state, violations)
        
        if violations_found == 0:
            print("  ✅ No constraint violations found")
        else:
            print(f"  🔧 Fixed {violations_found} constraint violations")
    
    def _fix_constraint_violations(self, theme_name: str, deck_state: DeckState, violations: List[str]):
        """Fix constraint violations by removing excess cards."""
        theme_config = ALL_THEMES[theme_name]
        is_mono = len(theme_config['colors']) == 1
        max_lands = self.constraints.get_max_lands(is_mono)
        
        if deck_state.land_count > max_lands:
            # Remove excess lands (remove last added ones)
            land_indices_to_remove = []
            for i, card_idx in enumerate(reversed(deck_state.cards)):
                card = self.oracle_df.iloc[card_idx]
                if is_land_card(card) and len(land_indices_to_remove) < (deck_state.land_count - max_lands):
                    land_indices_to_remove.append(len(deck_state.cards) - 1 - i)
            
            # Remove in reverse order to maintain indices
            for idx in sorted(land_indices_to_remove, reverse=True):
                card_idx = deck_state.cards.pop(idx)
                card = self.oracle_df.iloc[card_idx]
                deck_state.land_count -= 1
                deck_state.land_names.discard(card['name'])
                self.selector.mark_unused(card_idx)
                print(f"    🔧 Removed excess land: {card['name']}")
    
    def _convert_to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert deck states to DataFrames."""
        deck_dataframes = {}
        
        print(f"\n📋 DECK CONSTRUCTION SUMMARY")
        print("=" * 50)
        
        complete_decks = 0
        total_cards_used = 0
        
        for theme_name, deck_state in self.decks.items():
            if deck_state.size == 0:
                deck_dataframes[theme_name] = pd.DataFrame()
                print(f"{theme_name:20}: 0 cards ❌")
                continue
            
            # Create DataFrame
            deck_df = self.oracle_df.iloc[deck_state.cards].copy()
            deck_df['theme'] = theme_name
            deck_dataframes[theme_name] = deck_df
            
            # Update counters
            total_cards_used += deck_state.size
            if deck_state.size == self.constraints.target_deck_size:
                complete_decks += 1
                status = "✅"
            else:
                status = "⚠️"
            
            print(f"{theme_name:20}: {deck_state.size:2d} cards {status} "
                  f"(C:{deck_state.creature_count} L:{deck_state.land_count})")
        
        print(f"\n🎯 CONSTRUCTION RESULTS:")
        print(f"✅ Complete decks: {complete_decks}/{len(ALL_THEMES)}")
        print(f"📊 Total cards used: {total_cards_used}/{len(self.oracle_df)}")
        
        if complete_decks == len(ALL_THEMES):
            print(f"\n🎉 SUCCESS! All {len(ALL_THEMES)} jumpstart decks completed!")
        
        return deck_dataframes
    
    def _attempt_reorganization(self, deck_dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Attempt to reorganize cards between decks to complete incomplete decks."""
        print("\n🔄 REORGANIZATION PHASE")
        print("=" * 40)
        
        # Find incomplete decks
        incomplete_themes = [
            name for name, df in deck_dataframes.items() 
            if len(df) < self.constraints.target_deck_size
        ]
        
        if not incomplete_themes:
            return deck_dataframes
        
        # Get unassigned cards
        used_card_names = set()
        for df in deck_dataframes.values():
            if not df.empty:
                used_card_names.update(df['name'].tolist())
        
        unassigned_cards = self.oracle_df[~self.oracle_df['name'].isin(used_card_names)]
        
        reorganizations_made = 0
        
        for theme_name in incomplete_themes:
            current_deck = deck_dataframes[theme_name]
            cards_needed = self.constraints.target_deck_size - len(current_deck)
            theme_config = ALL_THEMES[theme_name]
            theme_colors = set(theme_config['colors'])
            
            print(f"\n🎯 Completing {theme_name} (needs {cards_needed} cards)")
            
            # Try to find compatible unassigned cards
            compatible_cards = []
            for _, card in unassigned_cards.iterrows():
                card_colors = set(get_card_colors(card))
                
                # Basic color compatibility
                if card_colors and not card_colors.issubset(theme_colors):
                    continue
                
                # Check constraints
                current_creatures = len(current_deck[current_deck['Type'].str.contains('Creature', case=False, na=False)])
                current_lands = current_deck[current_deck['Type'].str.contains('Land', case=False, na=False)]
                current_land_names = set(current_lands['name'].tolist()) if not current_lands.empty else set()
                
                if is_creature_card(card) and current_creatures >= self.constraints.max_creatures:
                    continue
                
                if is_land_card(card):
                    is_mono = len(theme_colors) == 1
                    max_lands = self.constraints.get_max_lands(is_mono)
                    if len(current_land_names) >= max_lands:
                        continue
                    if card['name'] in current_land_names:
                        continue
                    # For dual-color themes, ensure lands can produce both colors
                    if not is_mono and not can_land_produce_colors(card, theme_colors):
                        continue
                
                # Score the card
                score = score_card_for_theme(card, theme_config)
                if score >= 0.1:  # Very permissive threshold
                    compatible_cards.append((card, score))
            
            # Sort by score and add best cards
            compatible_cards.sort(key=lambda x: x[1], reverse=True)
            
            added_cards = []
            for card, score in compatible_cards[:cards_needed]:
                added_cards.append(card)
                print(f"   + {card['name']} (Score: {score:.1f})")
            
            if added_cards:
                # Update deck
                new_cards_df = pd.DataFrame(added_cards)
                if not current_deck.empty:
                    updated_deck = pd.concat([current_deck, new_cards_df], ignore_index=True)
                else:
                    updated_deck = new_cards_df
                
                updated_deck['theme'] = theme_name
                deck_dataframes[theme_name] = updated_deck
                
                # Remove from unassigned pool
                added_names = [card['name'] for card in added_cards]
                unassigned_cards = unassigned_cards[~unassigned_cards['name'].isin(added_names)]
                
                reorganizations_made += 1
                print(f"   ✅ Completed: {len(current_deck)} → {len(updated_deck)} cards")
                
                if len(updated_deck) == self.constraints.target_deck_size:
                    print(f"   🎉 {theme_name} is now complete!")
            else:
                print(f"   ❌ No compatible cards found for {theme_name}")
        
        print(f"\n📊 REORGANIZATION SUMMARY:")
        print(f"🔄 Themes helped: {reorganizations_made}")
        
        # Final summary
        final_complete = sum(1 for df in deck_dataframes.values() 
                           if len(df) == self.constraints.target_deck_size)
        final_incomplete = len(ALL_THEMES) - final_complete
        
        print(f"✅ Final complete decks: {final_complete}/{len(ALL_THEMES)}")
        if final_incomplete > 0:
            print(f"⚠️  Remaining incomplete: {final_incomplete}")
            print("   Consider adjusting theme requirements or adding more compatible cards")
        else:
            print(f"\n🎉 SUCCESS! All decks completed through reorganization!")
        
        return deck_dataframes


# Utility functions (copied from original construct module to avoid dependency issues)

def score_card_for_theme(card: pd.Series, theme_config: dict) -> float:
    """Score a card based on how well it fits a theme."""
    keywords = theme_config['keywords']
    score = 0.0
    
    # Get card properties
    cmc = card.get('CMC', 0) if pd.notna(card.get('CMC', 0)) else 0
    power = card.get('Power', 0) if pd.notna(card.get('Power', 0)) else 0
    archetype = theme_config.get('archetype', '')
    
    # Get text fields for searching
    oracle_text = str(card['Oracle Text']).lower() if pd.notna(card['Oracle Text']) else ""
    card_type = str(card['Type']).lower() if pd.notna(card['Type']) else ""
    card_name = str(card['name']).lower() if pd.notna(card['name']) else ""
    
    # Combine all text for searching
    searchable_text = f"{oracle_text} {card_type} {card_name}"
    
    # Score based on keyword matches
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in searchable_text:
            # Use regex for precise word boundary matching
            if re.search(r'\b' + re.escape(keyword_lower) + r'\b', searchable_text):
                score += 1.0
            elif keyword_lower in searchable_text:
                score += 0.5
    
    # A. ADD MANA CURVE SCORING: Bonus points for cards matching theme strategy
    if archetype == 'Aggro':
        if cmc == 1:
            score += 2.0  # Big bonus for 1-drops in aggro themes
        elif cmc == 2:
            score += 1.0  # Good bonus for 2-drops in aggro themes
        elif cmc >= 4:
            score -= 1.0  # Penalty for expensive cards in aggro themes
    elif archetype == 'Control':
        if cmc >= 4:
            score += 0.5  # Bonus for expensive cards in control themes
        elif cmc == 1:
            score -= 0.5  # Small penalty for 1-drops in control (unless utility)
    
    # B. IMPROVE KEYWORD MATCHING: Add CMC-specific keyword matching
    # Special handling for cost-related keywords
    if 'cheap' in keywords and cmc <= 2:
        score += 1.0  # Bonus for actually cheap cards
    
    if 'efficient' in keywords:
        # Bonus for good power/CMC ratio (creatures only)
        if 'creature' in card_type and power > 0 and cmc > 0:
            if power >= cmc:  # Power >= CMC is efficient
                score += 1.0
            elif power >= cmc - 1:  # Almost efficient
                score += 0.5
    
    if 'low cost' in keywords and cmc <= 2:
        score += 1.0  # Bonus for actually low cost cards
        
    if 'small' in keywords and 'creature' in card_type:
        if power <= 2:  # Small creatures typically have low power
            score += 0.5
    
    # Bonus scoring based on card type and theme strategy
    if 'creature' in card_type:
        # Bonus for creatures in creature-focused themes
        if any(kw in theme_config['keywords'] for kw in ['creature', 'tribal', 'aggressive']):
            score += 0.3
    
    if 'instant' in card_type or 'sorcery' in card_type:
        # Bonus for spells in spell-focused themes
        if any(kw in theme_config['keywords'] for kw in ['instant', 'sorcery', 'spells', 'burn', 'counter']):
            score += 0.3
    
    if 'artifact' in card_type:
        # Bonus for artifacts in artifact themes
        if any(kw in theme_config['keywords'] for kw in ['artifact', 'equipment', 'metalcraft']):
            score += 0.5
    
    return score


def is_land_card(card: pd.Series) -> bool:
    """Check if a card is a land."""
    card_type = str(card['Type']).lower() if pd.notna(card['Type']) else ""
    return 'land' in card_type


def is_creature_card(card: pd.Series) -> bool:
    """Check if a card is a creature."""
    card_type = str(card['Type']).lower() if pd.notna(card['Type']) else ""
    return 'creature' in card_type


def get_card_colors(card: pd.Series) -> List[str]:
    """Get the colors of a card."""
    color = str(card['Color']) if pd.notna(card['Color']) else ""
    if not color or color == 'C':  # Colorless
        return []
    return list(color)


def can_land_produce_colors(land_card: pd.Series, required_colors: set) -> bool:
    """
    Check if a land can produce all the required colors for a dual-color theme.
    This function checks for DIRECT mana production, not fetch/cycling abilities.
    """
    if not is_land_card(land_card):
        return False
    
    oracle_text = str(land_card.get('Oracle Text', '')).lower()
    
    # Get the land's color identity first
    land_colors = set(get_card_colors(land_card))
    
    # Check for direct mana production in oracle text
    directly_producible = set()
    
    # Look for mana production patterns like "{T}: Add {U}" or "{T}: Add {U} or {B}"
    if '{t}: add' in oracle_text:
        for color in ['W', 'U', 'B', 'R', 'G']:
            color_symbol = '{' + color.lower() + '}'
            # Check if this color appears in a mana production ability (not cycling cost)
            if color_symbol in oracle_text:
                # Make sure it's in a mana production line, not a cycling cost
                lines = oracle_text.split('|')
                for line in lines:
                    line = line.strip()
                    if '{t}: add' in line and color_symbol in line:
                        directly_producible.add(color)
                        break
    
    # If land has color identity, it can produce those colors
    if land_colors:
        directly_producible.update(land_colors)
    
    # For basic lands, add their inherent color
    basic_land_types = {
        'plains': 'W', 'island': 'U', 'swamp': 'B', 
        'mountain': 'R', 'forest': 'G'
    }
    
    for basic_type, color in basic_land_types.items():
        if basic_type in oracle_text and f'basic {basic_type}' in oracle_text:
            directly_producible.add(color)
    
    # Check if this land can directly produce all required colors
    return required_colors.issubset(directly_producible)


def score_land_for_dual_colors(land_card: pd.Series, required_colors: set) -> float:
    """
    Score a land based on how well it supports a dual-color theme.
    Higher scores are given to lands that can produce both colors.
    """
    if not is_land_card(land_card):
        return 0.0
    
    if len(required_colors) == 1:
        # For mono-color themes, any land that produces the color is good
        if can_land_produce_colors(land_card, required_colors):
            return 1.0
        return 0.0
    
    # For dual-color themes, prioritize lands that can produce both colors
    if not can_land_produce_colors(land_card, required_colors):
        return 0.0  # Can't produce both colors
    
    oracle_text = str(land_card.get('Oracle Text', '')).lower()
    
    # Check for DIRECT mana production (not just fetchable)
    directly_producible_colors = set()
    
    # Look for explicit mana symbols in the oracle text (e.g., {U}, {B})
    for color in ['W', 'U', 'B', 'R', 'G']:
        color_symbol = '{' + color.lower() + '}'
        if color_symbol in oracle_text:
            directly_producible_colors.add(color)
    
    # Check for color identity from the card's colors
    land_colors = set(get_card_colors(land_card))
    if land_colors:
        directly_producible_colors.update(land_colors)
    
    # IMPORTANT: Don't count lands that only fetch basics as direct producers
    if not directly_producible_colors:
        # This is likely a utility land (cycling, fetch, etc.)
        if '{c}' in oracle_text or 'add {c}' in oracle_text:
            return 0.1  # Minimal score for utility
    
    # Score based on direct color production efficiency
    if not required_colors.issubset(directly_producible_colors):
        # Check if it's a fetch/utility land that can get the colors
        can_fetch_both = True
        for color in required_colors:
            color_names = {
                'W': 'plains', 'U': 'island', 'B': 'swamp', 
                'R': 'mountain', 'G': 'forest'
            }
            if color in color_names and color_names[color] not in oracle_text:
                can_fetch_both = False
                break
        
        if can_fetch_both and ('search' in oracle_text or 'cycling' in oracle_text):
            return 0.3  # Low score for utility lands
        else:
            return 0.0  # Can't help with mana fixing
    
    # Land can directly produce both colors - calculate score
    score = 2.0  # Base score for direct dual-color production
    
    # Bonus for perfect dual land match
    if directly_producible_colors == required_colors:
        score += 2.0  # Exactly the colors we need
    elif len(directly_producible_colors) <= 3:
        score += 1.0  # Good but not perfect
    else:
        score += 0.5  # Many colors (less focused)
    
    # Penalty for enters-tapped lands (slower)
    if 'enters tapped' in oracle_text or 'enters the battlefield tapped' in oracle_text:
        score -= 0.3  # Small penalty for being slow
    
    # Bonus for utility abilities
    if 'cycling' in oracle_text:
        score += 0.2
    if 'draw a card' in oracle_text:
        score += 0.1
    
    return score


def construct_jumpstart_decks(oracle_df: pd.DataFrame, target_deck_size: int = 13) -> Dict[str, pd.DataFrame]:
    """
    Refactored version of construct_jumpstart_decks with cleaner architecture.
    
    This version separates concerns into focused classes:
    - CardSelector: Handles card selection and scoring
    - DeckState: Tracks deck building state
    - DeckBuilder: Orchestrates the building process
    - CardConstraints: Encapsulates deck rules
    
    Args:
        oracle_df: DataFrame with all available cards
        target_deck_size: Target number of cards per deck (default 13)
        
    Returns:
        Dictionary mapping theme names to their constructed decks (DataFrames)
    """
    constraints = CardConstraints(target_deck_size=target_deck_size)
    builder = DeckBuilder(oracle_df, constraints)
    return builder.build_all_decks()


def analyze_deck_composition(deck_df: pd.DataFrame, theme_name: str) -> Dict:
    """
    Analyze the composition of a constructed deck.
    
    Args:
        deck_df: DataFrame containing the deck cards
        theme_name: Name of the theme
        
    Returns:
        Dictionary with analysis results
    """
    if deck_df.empty:
        return {
            'theme': theme_name,
            'total_cards': 0,
            'creatures': 0,
            'lands': 0,
            'spells': 0,
            'avg_cmc': 0,
            'color_distribution': {},
            'type_breakdown': {}
        }
    
    # Count card types
    creatures = deck_df[deck_df['Type'].str.contains('Creature', case=False, na=False)]
    lands = deck_df[deck_df['Type'].str.contains('Land', case=False, na=False)]
    instants = deck_df[deck_df['Type'].str.contains('Instant', case=False, na=False)]
    sorceries = deck_df[deck_df['Type'].str.contains('Sorcery', case=False, na=False)]
    artifacts = deck_df[deck_df['Type'].str.contains('Artifact', case=False, na=False)]
    enchantments = deck_df[deck_df['Type'].str.contains('Enchantment', case=False, na=False)]
    
    # Calculate average CMC (excluding lands)
    non_lands = deck_df[~deck_df['Type'].str.contains('Land', case=False, na=False)]
    avg_cmc = non_lands['CMC'].mean() if not non_lands.empty and 'CMC' in non_lands.columns else 0
    
    # Color distribution
    color_counts = deck_df['Color'].value_counts().to_dict() if 'Color' in deck_df.columns else {}
    
    # Type breakdown
    type_breakdown = {
        'Creatures': len(creatures),
        'Lands': len(lands),
        'Instants': len(instants),
        'Sorceries': len(sorceries),
        'Artifacts': len(artifacts),
        'Enchantments': len(enchantments),
        'Other': len(deck_df) - sum([len(creatures), len(lands), len(instants), 
                                   len(sorceries), len(artifacts), len(enchantments)])
    }
    
    return {
        'theme': theme_name,
        'total_cards': len(deck_df),
        'creatures': len(creatures),
        'lands': len(lands),
        'spells': len(instants) + len(sorceries),
        'avg_cmc': avg_cmc,
        'color_distribution': color_counts,
        'type_breakdown': type_breakdown,
        'creature_list': creatures['name'].tolist() if not creatures.empty else [],
        'land_list': lands['name'].tolist() if not lands.empty else []
    }


def print_detailed_deck_analysis(deck_dataframes: Dict[str, pd.DataFrame]):
    """
    Print a detailed analysis of all constructed decks.
    
    Args:
        deck_dataframes: Dictionary of theme name -> deck DataFrame
    """
    print("\n📊 DETAILED DECK ANALYSIS")
    print("=" * 60)
    
    for theme_name, deck_df in deck_dataframes.items():
        analysis = analyze_deck_composition(deck_df, theme_name)
        
        if analysis['total_cards'] == 0:
            print(f"\n❌ {theme_name}: No cards")
            continue
        
        print(f"\n✅ {theme_name} ({analysis['total_cards']} cards)")
        print(f"   🧙 Creatures: {analysis['creatures']}")
        print(f"   🏞️  Lands: {analysis['lands']}")
        print(f"   ⚡ Spells: {analysis['spells']}")
        print(f"   💎 Avg CMC: {analysis['avg_cmc']:.1f}")
        
        if analysis['color_distribution']:
            colors_str = ', '.join([f"{color}: {count}" 
                                  for color, count in sorted(analysis['color_distribution'].items())])
            print(f"   🎨 Colors: {colors_str}")
        
        # Show constraint compliance
        theme_config = ALL_THEMES.get(theme_name, {})
        if theme_config:
            colors = theme_config.get('colors', [])
            is_mono = len(colors) == 1
            max_lands = 1 if is_mono else 3
            
            constraint_issues = []
            if analysis['creatures'] > 9:
                constraint_issues.append(f"Too many creatures ({analysis['creatures']}/9)")
            if analysis['lands'] > max_lands:
                constraint_issues.append(f"Too many lands ({analysis['lands']}/{max_lands})")
            
            if constraint_issues:
                print(f"   ⚠️  Issues: {', '.join(constraint_issues)}")
            else:
                print(f"   ✅ All constraints satisfied")
