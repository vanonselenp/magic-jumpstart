"""
Main deck building orchestrator for Jumpstart cube construction.
"""

import pandas as pd
from typing import Dict, List
from ..consts import ALL_THEMES, MONO_COLOR_THEMES, DUAL_COLOR_THEMES
from .core import CardConstraints, DeckState
from .selector import CardSelector
from .utils import is_creature_card, is_land_card, can_land_produce_colors, get_card_type_display


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
        
        # Phase 0: Core card reservation for theme coherence
        self._build_core_card_reservation_phase()
        
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
            
            # Phase 6: Re-validate constraints after reorganization
            print(f"\n🔍 Re-validating constraints after reorganization...")
            result = self._validate_dataframe_constraints(result)
        
        return result
    
    def _initialize_decks(self):
        """Initialize empty deck states for all themes."""
        for theme_name in ALL_THEMES:
            self.decks[theme_name] = DeckState(cards=[])
    
    def _build_core_card_reservation_phase(self):
        """Phase 0: Reserve core theme-defining cards to ensure theme coherence."""
        print("\n🔒 Phase 0: Core card reservation")
        print("Ensuring each theme gets its defining cards before general competition...")
        
        for theme_name, theme_config in ALL_THEMES.items():
            self._reserve_core_cards_for_theme(theme_name, theme_config)
    
    def _reserve_core_cards_for_theme(self, theme_name: str, theme_config: dict):
        """Reserve top core cards for a specific theme."""
        # Get appropriate scorer and count
        scorer, core_count = self.selector._get_specialized_scorer_and_count(theme_name, theme_config)
        
        # Find top scoring cards for this theme
        deck_state = self.decks[theme_name]
        theme_colors = set(theme_config['colors'])
        is_mono = len(theme_colors) == 1
        core_candidates = []
        
        for idx, card in self.oracle_df.iterrows():
            if idx in self.selector.used_cards:
                continue
            
            # Check basic color compatibility
            if not self.selector._is_color_compatible(card, theme_colors, "core"):
                continue
            
            # Check constraints
            if not self.selector._check_constraints(card, deck_state, self.constraints, is_mono, theme_colors):
                continue
            
            # Score with specialized scorer
            score_breakdown = scorer.score_with_breakdown(card, theme_config)
            
            # Collect all valid candidates (no minimum score threshold)
            core_candidates.append((idx, card, score_breakdown.total_score))
        
        # Sort by score and take top core_count
        core_candidates.sort(key=lambda x: x[2], reverse=True)
        reserved_count = 0
        
        print(f"\n🎯 {theme_name}: Reserving core cards")
        
        for card_idx, card, score in core_candidates[:core_count]:
            if reserved_count >= core_count:
                break
            
            # Double-check we can still add this card
            if not self.selector._check_constraints(card, deck_state, self.constraints, is_mono, theme_colors):
                continue
            
            deck_state.add_card(card_idx, card)
            self.selector.mark_used(card_idx)
            reserved_count += 1
            
            card_type = card['Type'][:20] + "..." if len(card['Type']) > 20 else card['Type']
            print(f"  ✅ {card['name']:<25} | {score:5.1f} pts | {card_type}")
        
        if reserved_count == 0:
            print(f"  ⚠️  No core cards could be reserved (no valid candidates found)")
        else:
            print(f"  📦 Reserved {reserved_count} core cards")
    
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
        
        # Log if below minimum creatures
        if deck_state.needs_more_creatures(self.constraints):
            creatures_needed = self.constraints.min_creatures - deck_state.creature_count
            print(f"  ⚠️  Below minimum creatures: {deck_state.creature_count}/{self.constraints.min_creatures} (need {creatures_needed} more)")

        candidates = self.selector.get_candidates_for_theme(
            theme_name, theme_config, deck_state, self.constraints, phase
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
            
            print(f"  ✅ Added: {card['name']} (Score: {score:.1f}) [{get_card_type_display(card)}]")
        
        print(f"  📊 {phase.title()} complete: {deck_state.size}/{self.constraints.target_deck_size} cards")
    
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
            if deck_state.creature_count < self.constraints.min_creatures:
                violations.append(f"min creatures: {deck_state.creature_count}/{self.constraints.min_creatures}")
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
        
        # Fix creature violations first (most critical)
        if deck_state.creature_count > self.constraints.max_creatures:
            excess_creatures = deck_state.creature_count - self.constraints.max_creatures
            print(f"    🚫 Removing {excess_creatures} excess creatures...")
            
            # Find creature indices to remove (remove from the end, last added first)
            creature_indices_to_remove = []
            for i, card_idx in enumerate(reversed(deck_state.cards)):
                card = self.oracle_df.iloc[card_idx]
                if is_creature_card(card) and len(creature_indices_to_remove) < excess_creatures:
                    creature_indices_to_remove.append(len(deck_state.cards) - 1 - i)
            
            # Remove creatures in reverse order to maintain indices
            for idx in sorted(creature_indices_to_remove, reverse=True):
                card_idx = deck_state.cards.pop(idx)
                card = self.oracle_df.iloc[card_idx]
                deck_state.creature_count -= 1
                
                # Update CMC tracking for removed non-land cards
                if not is_land_card(card):
                    card_cmc = int(card['CMC'])
                    deck_state.total_cmc -= card_cmc
                    
                    # Update CMC distribution counts
                    if card_cmc <= 2:
                        deck_state.cmc_counts['low'] -= 1
                    elif card_cmc <= 4:
                        deck_state.cmc_counts['med'] -= 1
                    else:
                        deck_state.cmc_counts['high'] -= 1
                
                self.selector.mark_unused(card_idx)
                print(f"    🔧 Removed excess creature: {card['name']}")
        
        # Fix land violations
        if deck_state.land_count > max_lands:
            excess_lands = deck_state.land_count - max_lands
            print(f"    🚫 Removing {excess_lands} excess lands...")
            
            # Remove excess lands (remove last added ones)
            land_indices_to_remove = []
            for i, card_idx in enumerate(reversed(deck_state.cards)):
                card = self.oracle_df.iloc[card_idx]
                if is_land_card(card) and len(land_indices_to_remove) < excess_lands:
                    land_indices_to_remove.append(len(deck_state.cards) - 1 - i)
            
            # Remove in reverse order to maintain indices
            for idx in sorted(land_indices_to_remove, reverse=True):
                card_idx = deck_state.cards.pop(idx)
                card = self.oracle_df.iloc[card_idx]
                deck_state.land_count -= 1
                deck_state.land_names.discard(card['name'])
                self.selector.mark_unused(card_idx)
                print(f"    🔧 Removed excess land: {card['name']}")
        
        # Fix minimum creature violations by adding more creatures if available
        if deck_state.creature_count < self.constraints.min_creatures:
            creatures_needed = self.constraints.min_creatures - deck_state.creature_count
            print(f"    ➕ Need {creatures_needed} more creatures to meet minimum...")
            
            # Try to find available creatures
            theme_colors = set(theme_config['colors'])
            for idx, card in self.oracle_df.iterrows():
                if (idx not in self.selector.used_cards and 
                    is_creature_card(card) and 
                    self.selector._is_color_compatible(card, theme_colors, "completion") and
                    creatures_needed > 0 and
                    deck_state.size < self.constraints.target_deck_size):
                    
                    deck_state.add_card(idx, card)
                    self.selector.mark_used(idx)
                    creatures_needed -= 1
                    print(f"    ✅ Added creature to meet minimum: {card['name']}")
                    
                    if creatures_needed == 0:
                        break
    
    def _validate_dataframe_constraints(self, deck_dataframes: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Validate and fix constraint violations in deck DataFrames after reorganization."""
        violations_found = 0
        
        for theme_name, deck_df in deck_dataframes.items():
            if deck_df.empty:
                continue
            
            theme_config = ALL_THEMES[theme_name]
            is_mono = len(theme_config['colors']) == 1
            max_lands = self.constraints.get_max_lands(is_mono)
            
            # Count current creatures and lands
            creature_count = len(deck_df[deck_df['Type'].str.contains('Creature', case=False, na=False)])
            land_count = len(deck_df[deck_df['Type'].str.contains('Land', case=False, na=False)])
            
            violations = []
            if creature_count > self.constraints.max_creatures:
                violations.append(f"creatures: {creature_count}/{self.constraints.max_creatures}")
            if creature_count < self.constraints.min_creatures:
                violations.append(f"min creatures: {creature_count}/{self.constraints.min_creatures}")
            if land_count > max_lands:
                violations.append(f"lands: {land_count}/{max_lands}")
            
            if violations:
                violations_found += 1
                print(f"  ⚠️  {theme_name}: VIOLATION - {', '.join(violations)}")
                deck_dataframes[theme_name] = self._fix_dataframe_constraint_violations(
                    theme_name, deck_df, violations
                )
        
        if violations_found == 0:
            print("  ✅ No constraint violations found after reorganization")
        else:
            print(f"  🔧 Fixed {violations_found} constraint violations after reorganization")
        
        return deck_dataframes
    
    def _fix_dataframe_constraint_violations(self, theme_name: str, deck_df: pd.DataFrame, 
                                           violations: List[str]) -> pd.DataFrame:
        """Fix constraint violations in a deck DataFrame."""
        theme_config = ALL_THEMES[theme_name]
        is_mono = len(theme_config['colors']) == 1
        max_lands = self.constraints.get_max_lands(is_mono)
        
        # Fix creature violations first (most critical)
        creature_count = len(deck_df[deck_df['Type'].str.contains('Creature', case=False, na=False)])
        if creature_count > self.constraints.max_creatures:
            excess_creatures = creature_count - self.constraints.max_creatures
            print(f"    🚫 Removing {excess_creatures} excess creatures from DataFrame...")
            
            # Get creature rows
            creature_mask = deck_df['Type'].str.contains('Creature', case=False, na=False)
            creature_indices = deck_df[creature_mask].index.tolist()
            
            # Remove excess creatures from the end (last added first)
            creatures_to_remove = creature_indices[-excess_creatures:]
            
            # Get names before dropping (for logging)
            removed_names = []
            for idx in creatures_to_remove:
                removed_names.append(deck_df.loc[idx, 'name'])
            
            deck_df = deck_df.drop(creatures_to_remove)
            
            # Log removed creatures
            for name in removed_names:
                print(f"    🔧 Removed excess creature: {name}")
        
        # Fix land violations
        land_count = len(deck_df[deck_df['Type'].str.contains('Land', case=False, na=False)])
        if land_count > max_lands:
            excess_lands = land_count - max_lands
            print(f"    🚫 Removing {excess_lands} excess lands from DataFrame...")
            
            # Get land rows
            land_mask = deck_df['Type'].str.contains('Land', case=False, na=False)
            land_indices = deck_df[land_mask].index.tolist()
            
            # Remove excess lands from the end
            lands_to_remove = land_indices[-excess_lands:]
            
            # Get names before dropping (for logging)
            removed_names = []
            for idx in lands_to_remove:
                removed_names.append(deck_df.loc[idx, 'name'])
            
            deck_df = deck_df.drop(lands_to_remove)
            
            # Log removed lands
            for name in removed_names:
                print(f"    🔧 Removed excess land: {name}")
        
        return deck_df
    
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
                from .utils import get_card_colors
                card_colors = set(get_card_colors(card))
                
                # Basic color compatibility
                if card_colors and not card_colors.issubset(theme_colors):
                    continue
                
                # Check constraints
                current_creatures = len(current_deck[current_deck['Type'].str.contains('Creature', case=False, na=False)])
                current_lands = current_deck[current_deck['Type'].str.contains('Land', case=False, na=False)]
                current_land_names = set(current_lands['name'].tolist()) if not current_lands.empty else set()
                current_non_lands = len(current_deck) - len(current_lands)
                
                if is_creature_card(card) and current_creatures >= self.constraints.max_creatures:
                    continue
                
                # Check total non-land constraint
                if not is_land_card(card) and current_non_lands >= self.constraints.total_non_land:
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
                from ..scorer import score_card_for_theme
                score = score_card_for_theme(card, theme_config)
                
                # Creature prioritization boost when below minimum
                if is_creature_card(card) and current_creatures < self.constraints.min_creatures:
                    score += 2.0  # Significant boost to prioritize creatures when below minimum
                    print(f"  🎯 Prioritizing creature {card['name']} (below min: {current_creatures}/{self.constraints.min_creatures})")
                
                # Special case: if deck needs exactly 1 land and this is a land, accept ANY land
                needs_land_to_complete = (
                    cards_needed == 1 and 
                    current_non_lands >= self.constraints.total_non_land and 
                    is_land_card(card)
                )
                
                if needs_land_to_complete:
                    # For completion lands, accept any land regardless of score
                    compatible_cards.append((card, max(score, 0.1)))  # Ensure positive score for sorting
                elif score >= 0.1:  # Normal threshold for other cards
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
