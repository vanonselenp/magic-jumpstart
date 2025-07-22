"""
Jumpstart Cube Deck Construction

This module handles the construction of jumpstart decks from the oracle card pool
based on the themes defined in consts.py.
"""

import pandas as pd
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from .consts import ALL_THEMES, MONO_COLOR_THEMES, DUAL_COLOR_THEMES


def score_card_for_theme(card: pd.Series, theme_config: dict) -> float:
    """
    Score a card based on how well it fits a theme.
    
    Args:
        card: Card data from oracle_df
        theme_config: Theme configuration from consts.py
        
    Returns:
        Score (higher = better fit)
    """
    keywords = theme_config['keywords']
    score = 0.0
    
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
    
    Args:
        land_card: The land card to check
        required_colors: Set of colors that must be producible (e.g., {'W', 'U'})
        
    Returns:
        True if the land can directly produce all required colors
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
    
    Args:
        land_card: The land card to score
        required_colors: Set of colors needed (e.g., {'W', 'U'})
        
    Returns:
        Land quality score (higher = better for dual-color deck)
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
    # Cycling lands and fetch lands are utility, not direct mana production
    if not directly_producible_colors:
        # This is likely a utility land (cycling, fetch, etc.)
        # Check if it only produces {C} or similar
        if '{c}' in oracle_text or 'add {c}' in oracle_text:
            # This land only produces colorless - very low priority for dual-color
            return 0.1  # Minimal score for utility
    
    # Score based on direct color production efficiency
    if not required_colors.issubset(directly_producible_colors):
        # Can't directly produce both required colors
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
    Construct jumpstart decks for all themes using a practical three-phase approach.
    
    Args:
        oracle_df: DataFrame with all available cards
        target_deck_size: Target number of cards per deck (default 13)
        
    Returns:
        Dictionary mapping theme names to their constructed decks (DataFrames)
    """
    
    # Initialize deck storage
    decks = {}
    used_cards = set()  # Track which cards have been assigned
    
    print("🏗️ CONSTRUCTING JUMPSTART DECKS")
    print("=" * 50)
    
    # Phase 1: Assign dual-color cards to dual-color themes
    print("\n📦 Phase 1: Assigning dual-color cards to dual-color themes")
    
    for theme_name, theme_config in DUAL_COLOR_THEMES.items():
        theme_colors = set(theme_config['colors'])
        decks[theme_name] = []
        
        print(f"\n🎯 Building {theme_name} deck ({'/'.join(theme_config['colors'])})")
        
        # Find cards that match exactly the theme colors (multicolor cards and appropriate lands)
        multicolor_candidates = []
        
        for idx, card in oracle_df.iterrows():
            if idx in used_cards:
                continue
                
            card_colors = set(get_card_colors(card))
            is_land = is_land_card(card)
            
            # For lands, check if they can produce both colors and score them
            if is_land:
                if not can_land_produce_colors(card, theme_colors):
                    continue  # Skip lands that can't produce both colors
                
                # Use specialized land scoring for dual-color themes
                land_score = score_land_for_dual_colors(card, theme_colors)
                theme_score = score_card_for_theme(card, theme_config)
                
                # Combine land quality and theme synergy scores
                combined_score = land_score + (theme_score * 0.3)  # Prioritize land quality
                
                if combined_score >= 0.5:  # Higher threshold for better land selection
                    multicolor_candidates.append((idx, card, combined_score))
            else:
                # For non-lands, check color compatibility
                if not card_colors or not card_colors.issubset(theme_colors):
                    continue
                
                # Must be multicolor (have more than one color) for this phase, or be colorless
                if card_colors and len(card_colors) < 2:
                    continue
                    
                score = score_card_for_theme(card, theme_config)
                if score >= 0.3:  # More permissive threshold
                    multicolor_candidates.append((idx, card, score))
        
        # Sort by score and add best multicolor cards with constraint enforcement
        multicolor_candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Track constraints for Phase 1
        creature_count = 0
        land_count = 0
        current_lands = set()
        max_lands = 1 if len(theme_colors) == 1 else 3
        max_creatures = 9
        
        for idx, card, score in multicolor_candidates:
            if len(decks[theme_name]) >= target_deck_size:
                break
                
            # Check constraints before adding
            is_creature = is_creature_card(card)
            is_land = is_land_card(card)
            
            if is_creature and creature_count >= max_creatures:
                continue
                
            if is_land:
                if land_count >= max_lands:
                    continue
                if card['name'] in current_lands:  # No duplicate lands
                    continue
            
            # Add the card
            decks[theme_name].append(idx)
            used_cards.add(idx)
            
            # Update counters
            if is_creature:
                creature_count += 1
            elif is_land:
                land_count += 1
                current_lands.add(card['name'])
                
            print(f"  ✅ Added: {card['name']} (Score: {score:.1f}) [{card['Type'].split(' - ')[0]}]")
        
        print(f"  📊 Phase 1 complete: {len(decks[theme_name])}/{target_deck_size} cards (C:{creature_count} L:{land_count})")
    
    # Phase 2: Fill remaining slots using keyword-matched cards
    print(f"\n📦 Phase 2: Filling slots with keyword-matched cards")
    
    for theme_name, theme_config in ALL_THEMES.items():
        if theme_name not in decks:
            decks[theme_name] = []
        
        theme_colors = set(theme_config['colors'])
        current_deck_size = len(decks[theme_name])
        
        if current_deck_size >= target_deck_size:
            continue
            
        print(f"\n🎯 Completing {theme_name} deck ({current_deck_size}/{target_deck_size} cards)")
        
        # Count current card types in deck
        creature_count = 0
        land_count = 0
        current_lands = set()
        
        for card_idx in decks[theme_name]:
            card = oracle_df.iloc[card_idx]
            if is_creature_card(card):
                creature_count += 1
            elif is_land_card(card):
                land_count += 1
                current_lands.add(card['name'])
        
        # Set land limits
        is_mono_color = len(theme_colors) == 1
        max_lands = 1 if is_mono_color else 3
        max_creatures = 9
        
        # Find candidate cards with keyword matching
        candidates = []
        
        for idx, card in oracle_df.iterrows():
            if idx in used_cards:
                continue
                
            card_colors = set(get_card_colors(card))
            
            # Check color compatibility (include colorless cards)
            if card_colors and not card_colors.issubset(theme_colors):
                continue
            
            # Apply card type limits
            if is_creature_card(card) and creature_count >= max_creatures:
                continue
                
            if is_land_card(card):
                if land_count >= max_lands:
                    continue
                if card['name'] in current_lands:  # No duplicate lands
                    continue
                
                # For dual-color themes, ensure lands can produce both colors
                if not is_mono_color and not can_land_produce_colors(card, theme_colors):
                    continue
                
                # Use specialized land scoring for dual-color themes
                if is_mono_color:
                    score = score_card_for_theme(card, theme_config)
                else:
                    land_score = score_land_for_dual_colors(card, theme_colors)
                    theme_score = score_card_for_theme(card, theme_config)
                    score = land_score + (theme_score * 0.3)  # Prioritize dual-color capability
            else:
                score = score_card_for_theme(card, theme_config)
                
            if score >= 0.2:  # Lower threshold for filling decks
                candidates.append((idx, card, score))
        
        # Sort candidates by score
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Add cards to complete the deck
        cards_needed = target_deck_size - current_deck_size
        added_count = 0
        
        for idx, card, score in candidates:
            if added_count >= cards_needed:
                break
                
            # Double-check limits before adding
            if is_creature_card(card) and creature_count >= max_creatures:
                continue
            if is_land_card(card) and (land_count >= max_lands or card['name'] in current_lands):
                continue
                
            decks[theme_name].append(idx)
            used_cards.add(idx)
            
            if is_creature_card(card):
                creature_count += 1
            elif is_land_card(card):
                land_count += 1
                current_lands.add(card['name'])
                
            added_count += 1
            print(f"  ✅ Added: {card['name']} (Score: {score:.1f}) [{card['Type']}]")
        
        final_size = len(decks[theme_name])
        print(f"  📊 Phase 2 complete: {final_size}/{target_deck_size} cards")
        
        # Validate constraints after Phase 2
        if final_size > 0:
            deck_creatures = sum(1 for idx in decks[theme_name] if is_creature_card(oracle_df.iloc[idx]))
            deck_lands = sum(1 for idx in decks[theme_name] if is_land_card(oracle_df.iloc[idx]))
            deck_land_names = {oracle_df.iloc[idx]['name'] for idx in decks[theme_name] if is_land_card(oracle_df.iloc[idx])}
            
            # Check for violations
            if deck_creatures > max_creatures:
                print(f"  ⚠️  CONSTRAINT VIOLATION: {deck_creatures} creatures (max {max_creatures})")
            if len(deck_land_names) > max_lands:
                print(f"  ⚠️  CONSTRAINT VIOLATION: {len(deck_land_names)} unique lands (max {max_lands})")
    
    # Phase 2.5: Constraint validation and correction
    print(f"\n📦 Phase 2.5: Constraint validation and correction")
    
    violations_found = 0
    for theme_name, card_indices in decks.items():
        if not card_indices:
            continue
            
        theme_config = ALL_THEMES[theme_name]
        theme_colors = set(theme_config['colors'])
        is_mono_color = len(theme_colors) == 1
        max_lands = 1 if is_mono_color else 3
        max_creatures = 9
        
        # Count actual types
        deck_creatures = [idx for idx in card_indices if is_creature_card(oracle_df.iloc[idx])]
        deck_lands = [idx for idx in card_indices if is_land_card(oracle_df.iloc[idx])]
        deck_land_names = {oracle_df.iloc[idx]['name'] for idx in deck_lands}
        
        violations = []
        if len(deck_creatures) > max_creatures:
            violations.append(f"creatures: {len(deck_creatures)}/{max_creatures}")
        if len(deck_land_names) > max_lands:
            violations.append(f"lands: {len(deck_land_names)}/{max_lands}")
        
        if violations:
            violations_found += 1
            print(f"  ⚠️  {theme_name}: VIOLATION - {', '.join(violations)}")
            
            # Auto-fix land violations by removing excess lands
            if len(deck_land_names) > max_lands:
                excess_lands = len(deck_land_names) - max_lands
                lands_to_remove = deck_lands[-excess_lands:]  # Remove last added lands
                
                for land_idx in lands_to_remove:
                    land_card = oracle_df.iloc[land_idx]
                    decks[theme_name].remove(land_idx)
                    used_cards.discard(land_idx)
                    print(f"    🔧 Removed excess land: {land_card['name']}")
                
                print(f"    ✅ Land violation fixed: {len(deck_land_names)} → {max_lands} lands")
    
    if violations_found == 0:
        print(f"  ✅ No constraint violations found - all decks properly constructed")
    else:
        print(f"  🔧 Fixed {violations_found} constraint violations")
    
    # Phase 3: Practical completion for remaining incomplete decks
    print(f"\n📦 Phase 3: Practical completion for incomplete decks")
    
    # Find incomplete decks and sort by completion percentage
    incomplete_decks = [(name, len(deck_cards)) for name, deck_cards in decks.items() 
                       if len(deck_cards) < target_deck_size]
    incomplete_decks.sort(key=lambda x: x[1], reverse=True)  # Most complete first
    
    for theme_name, current_size in incomplete_decks:
        theme_config = ALL_THEMES[theme_name]
        theme_colors = set(theme_config['colors'])
        cards_needed = target_deck_size - current_size
        
        print(f"\n🔧 Practical completion: {theme_name} (needs {cards_needed} cards)")
        
        # Current deck analysis
        creature_count = 0
        land_count = 0
        current_lands = set()
        
        for card_idx in decks[theme_name]:
            card = oracle_df.iloc[card_idx]
            if is_creature_card(card):
                creature_count += 1
            elif is_land_card(card):
                land_count += 1
                current_lands.add(card['name'])
        
        # Set limits
        is_mono_color = len(theme_colors) == 1
        max_lands = 1 if is_mono_color else 3
        max_creatures = 9
        
        creatures_can_add = max_creatures - creature_count
        lands_can_add = max_lands - land_count
        
        # Find color-appropriate cards (relaxed scoring)
        practical_candidates = []
        
        for idx, card in oracle_df.iterrows():
            if idx in used_cards:
                continue
                
            card_colors = set(get_card_colors(card))
            
            # Check color compatibility (be permissive with colorless)
            if card_colors and not card_colors.issubset(theme_colors):
                continue
            
            is_creature = is_creature_card(card)
            is_land = is_land_card(card)
            
            # Check constraints
            if is_creature and creatures_can_add <= 0:
                continue
            if is_land and lands_can_add <= 0:
                continue
            if is_land and card['name'] in current_lands:
                continue
            
            # For dual-color themes, ensure lands can produce both colors
            if is_land and not is_mono_color and not can_land_produce_colors(card, theme_colors):
                continue
            
            # Relaxed scoring - prioritize color compatibility over perfect keyword match
            score = 0.0
            
            # Keyword matching (reduced weight)
            theme_score = score_card_for_theme(card, theme_config)
            score += theme_score * 0.7
            
            # Color preference bonus
            if card_colors == theme_colors:
                score += 0.5  # Perfect color match
            elif card_colors and card_colors.issubset(theme_colors):
                score += 0.3  # Compatible colors
            elif not card_colors:  # Colorless
                score += 0.1
            
            # Accept any card with reasonable color compatibility
            if score >= 0.1 or not card_colors:  # Very permissive
                practical_candidates.append((idx, card, score, is_creature, is_land))
        
        # Sort by score and fill deck
        practical_candidates.sort(key=lambda x: x[2], reverse=True)
        
        creatures_added = 0
        lands_added = 0
        
        for idx, card, score, is_creature, is_land in practical_candidates:
            if len(decks[theme_name]) >= target_deck_size:
                break
                
            if is_creature and creatures_added >= creatures_can_add:
                continue
            if is_land and lands_added >= lands_can_add:
                continue
                
            decks[theme_name].append(idx)
            used_cards.add(idx)
            
            if is_creature:
                creatures_added += 1
            elif is_land:
                lands_added += 1
                
            print(f"  ✅ Added: {card['name']} (Score: {score:.1f}) [{card['Type']}]")
        
        final_size = len(decks[theme_name])
        print(f"  📊 Final size: {final_size}/{target_deck_size} cards")
        
        if final_size < target_deck_size:
            print(f"  ⚠️  Still incomplete ({target_deck_size - final_size} cards short)")
    
    # Convert to DataFrames and add deck analysis
    deck_dataframes = {}
    
    print(f"\n📋 DECK CONSTRUCTION SUMMARY")
    print("=" * 50)
    
    complete_decks = 0
    incomplete_decks = 0
    total_cards_used = 0
    
    for theme_name, card_indices in decks.items():
        if not card_indices:
            deck_dataframes[theme_name] = pd.DataFrame()
            print(f"{theme_name:20}: 0 cards ❌")
            continue
            
        deck_df = oracle_df.iloc[card_indices].copy()
        deck_df['theme'] = theme_name
        deck_dataframes[theme_name] = deck_df
        
        # Analyze deck composition
        creatures = deck_df[deck_df['Type'].str.contains('Creature', case=False, na=False)]
        lands = deck_df[deck_df['Type'].str.contains('Land', case=False, na=False)]
        other = deck_df[~deck_df['Type'].str.contains('Creature|Land', case=False, na=False)]
        
        deck_size = len(deck_df)
        total_cards_used += deck_size
        
        if deck_size == target_deck_size:
            complete_decks += 1
            status = "✅"
        elif deck_size > 0:
            incomplete_decks += 1
            status = "⚠️"
        else:
            status = "❌"
            
        print(f"{theme_name:20}: {deck_size:2d} cards {status} "
              f"(C:{len(creatures)} L:{len(lands)} O:{len(other)})")
    
    print(f"\n🎯 CONSTRUCTION RESULTS:")
    print(f"✅ Complete decks: {complete_decks}/{len(ALL_THEMES)}")
    print(f"⚠️  Incomplete decks: {incomplete_decks}")
    print(f"📊 Total cards used: {total_cards_used}/{len(oracle_df)}")
    print(f"🔄 Cards remaining: {len(oracle_df) - total_cards_used}")
    
    if complete_decks == len(ALL_THEMES):
        print(f"\n🎉 SUCCESS! All {len(ALL_THEMES)} jumpstart decks completed!")
    elif incomplete_decks > 0:
        print(f"\n� Phase 4: Attempting deck reorganization for {incomplete_decks} incomplete decks")
        deck_dataframes = reorganize_incomplete_decks(deck_dataframes, oracle_df, target_deck_size)
        
        # Recount after reorganization
        complete_after_reorg = sum(1 for deck_df in deck_dataframes.values() if len(deck_df) == target_deck_size)
        incomplete_after_reorg = len(ALL_THEMES) - complete_after_reorg
        
        print(f"\n📊 REORGANIZATION RESULTS:")
        print(f"✅ Complete decks: {complete_after_reorg}/{len(ALL_THEMES)} (was {complete_decks})")
        print(f"⚠️  Remaining incomplete: {incomplete_after_reorg} (was {incomplete_decks})")
        
        if complete_after_reorg == len(ALL_THEMES):
            print(f"\n🎉 SUCCESS! All decks completed through reorganization!")
        elif incomplete_after_reorg < incomplete_decks:
            print(f"\n💡 Reorganization helped! Reduced incomplete decks from {incomplete_decks} to {incomplete_after_reorg}")
            if incomplete_after_reorg > 0:
                print(f"   Consider manual completion for remaining {incomplete_after_reorg} decks")
        else:
            print(f"\n⚠️  Reorganization couldn't help. Consider:")
            print(f"   - Running the practical completion analysis")
            print(f"   - Adjusting theme requirements for incomplete decks")
            print(f"   - Using remaining {len(oracle_df) - total_cards_used} cards for completion")
    
    return deck_dataframes


def complete_incomplete_decks(deck_dataframes: Dict[str, pd.DataFrame], oracle_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Complete any incomplete decks using a practical approach that prioritizes
    color compatibility over perfect keyword matching.
    
    Args:
        deck_dataframes: Current deck DataFrames (some may be incomplete)
        oracle_df: Full oracle DataFrame with all available cards
        
    Returns:
        Updated deck DataFrames with completed decks
    """
    
    print("🔧 COMPLETING INCOMPLETE DECKS")
    print("=" * 40)
    
    # Get used cards
    used_cards = set()
    for deck_df in deck_dataframes.values():
        if not deck_df.empty:
            used_cards.update(deck_df['name'].tolist())
    
    # Get unassigned cards
    unassigned_cards = oracle_df[~oracle_df['name'].isin(used_cards)].copy()
    available_cards = unassigned_cards.copy()
    
    # Find incomplete decks
    incomplete_decks = [(name, df) for name, df in deck_dataframes.items() if len(df) < 13]
    incomplete_decks.sort(key=lambda x: len(x[1]), reverse=True)  # Most complete first
    
    updated_decks = deck_dataframes.copy()
    completion_assignments = {}
    
    for theme_name, current_deck in incomplete_decks:
        cards_needed = 13 - len(current_deck)
        theme_config = ALL_THEMES[theme_name]
        theme_colors = set(theme_config['colors'])
        
        print(f"\n🎯 {theme_name}: needs {cards_needed} cards")
        
        # Analyze current deck
        current_creatures = current_deck[current_deck['Type'].str.contains('Creature', case=False, na=False)]
        current_lands = current_deck[current_deck['Type'].str.contains('Land', case=False, na=False)]
        
        creatures_can_add = 9 - len(current_creatures)
        is_mono = len(theme_colors) == 1
        max_lands = 1 if is_mono else 3
        lands_can_add = max_lands - current_lands['name'].nunique()
        
        # Find compatible cards
        compatible_candidates = []
        
        for _, card in available_cards.iterrows():
            # Color compatibility
            card_colors = set(str(card['Color'])) if pd.notna(card['Color']) and str(card['Color']) != 'nan' else set()
            if card_colors and not card_colors.issubset(theme_colors):
                continue
            
            # Type constraints
            is_creature = 'creature' in str(card['Type']).lower()
            is_land = 'land' in str(card['Type']).lower()
            
            if is_creature and creatures_can_add <= 0:
                continue
            if is_land and lands_can_add <= 0:
                continue
            if is_land and card['name'] in current_lands['name'].values:
                continue
            
            # For dual-color themes, ensure lands can produce both colors
            if is_land and len(theme_colors) > 1 and not can_land_produce_colors(card, theme_colors):
                continue
            
            # Score for appropriateness
            score = 0.0
            
            # Keyword matching
            oracle_text = str(card['Oracle Text']).lower() if pd.notna(card['Oracle Text']) else ""
            card_type = str(card['Type']).lower()
            card_name = str(card['name']).lower()
            searchable_text = f"{oracle_text} {card_type} {card_name}"
            
            for keyword in theme_config['keywords']:
                if keyword.lower() in searchable_text:
                    score += 1.0
            
            # Color match bonus
            if card_colors == theme_colors:
                score += 0.5
            elif card_colors and card_colors.issubset(theme_colors):
                score += 0.3
            elif not card_colors:  # Colorless
                score += 0.1
            
            compatible_candidates.append((card, score, is_creature, is_land))
        
        # Sort and select best cards
        compatible_candidates.sort(key=lambda x: x[1], reverse=True)
        selected_cards = []
        creatures_added = 0
        lands_added = 0
        
        for card, score, is_creature, is_land in compatible_candidates:
            if len(selected_cards) >= cards_needed:
                break
            
            if is_creature and creatures_added >= creatures_can_add:
                continue
            if is_land and lands_added >= lands_can_add:
                continue
            
            selected_cards.append(card)
            if is_creature:
                creatures_added += 1
            elif is_land:
                lands_added += 1
            
            print(f"   + {card['name']} (Score: {score:.1f})")
        
        # Update deck
        if selected_cards:
            cards_df = pd.DataFrame(selected_cards)
            updated_deck = pd.concat([current_deck, cards_df], ignore_index=True)
            updated_deck['theme'] = theme_name
            updated_decks[theme_name] = updated_deck
            
            # Remove from available pool
            selected_names = [card['name'] for card in selected_cards]
            available_cards = available_cards[~available_cards['name'].isin(selected_names)]
            
            completion_assignments[theme_name] = selected_cards
            print(f"   ✅ Completed: {len(current_deck)} → {len(updated_deck)} cards")
        else:
            print(f"   ❌ No compatible cards found")
    
    return updated_decks


def reorganize_incomplete_decks(deck_dataframes: Dict[str, pd.DataFrame], oracle_df: pd.DataFrame, target_deck_size: int = 13) -> Dict[str, pd.DataFrame]:
    """
    Attempt to complete incomplete decks through reorganization of cards between decks.
    This function handles edge cases where simple completion fails due to lack of suitable cards.
    
    Args:
        deck_dataframes: Current deck DataFrames (some may be incomplete)
        oracle_df: Full oracle DataFrame with all available cards
        target_deck_size: Target cards per deck (default 13)
        
    Returns:
        Updated deck DataFrames after reorganization attempts
    """
    
    print(f"🔄 REORGANIZING CARDS BETWEEN DECKS")
    print("=" * 50)
    
    # Get used cards and unassigned cards
    used_cards = set()
    for deck_df in deck_dataframes.values():
        if not deck_df.empty:
            used_cards.update(deck_df['name'].tolist())
    
    unassigned_cards = oracle_df[~oracle_df['name'].isin(used_cards)].copy()
    
    # Find incomplete decks that need completion
    incomplete_decks = []
    for theme_name, deck_df in deck_dataframes.items():
        if len(deck_df) < target_deck_size:
            cards_needed = target_deck_size - len(deck_df)
            theme_config = ALL_THEMES[theme_name]
            incomplete_decks.append((theme_name, deck_df, cards_needed, theme_config))
    
    # Sort by cards needed (fewest first - easier to complete)
    incomplete_decks.sort(key=lambda x: x[2])
    
    updated_decks = deck_dataframes.copy()
    reorganizations_made = 0
    
    for theme_name, current_deck, cards_needed, theme_config in incomplete_decks:
        theme_colors = set(theme_config['colors'])
        
        print(f"\n🎯 Attempting to complete {theme_name} (needs {cards_needed} cards)")
        print(f"   Colors: {'/'.join(sorted(theme_colors))}")
        
        # Analyze what types of cards this deck can accept
        current_creatures = current_deck[current_deck['Type'].str.contains('Creature', case=False, na=False)]
        current_lands = current_deck[current_deck['Type'].str.contains('Land', case=False, na=False)]
        
        creatures_can_add = 9 - len(current_creatures)
        is_mono = len(theme_colors) == 1
        max_lands = 1 if is_mono else 3
        lands_can_add = max_lands - current_lands['name'].nunique()
        spells_needed = cards_needed - min(creatures_can_add, cards_needed) - min(lands_can_add, cards_needed)
        
        print(f"   Can accept: {creatures_can_add} creatures, {lands_can_add} lands, need {spells_needed} spells")
        
        # First, try to use unassigned cards
        suitable_unassigned = []
        for _, card in unassigned_cards.iterrows():
            card_colors = set(str(card['Color'])) if pd.notna(card['Color']) and str(card['Color']) != 'nan' else set()
            
            # Check color compatibility
            if card_colors and not card_colors.issubset(theme_colors):
                continue
            
            # Check type constraints
            is_creature = 'creature' in str(card['Type']).lower()
            is_land = 'land' in str(card['Type']).lower()
            
            if is_creature and creatures_can_add <= 0:
                continue
            if is_land and lands_can_add <= 0:
                continue
            if is_land and card['name'] in current_lands['name'].values:
                continue
            if is_land and len(theme_colors) > 1 and not can_land_produce_colors(card, theme_colors):
                continue
                
            suitable_unassigned.append(card)
        
        if len(suitable_unassigned) >= cards_needed:
            print(f"   ✅ Can complete using {len(suitable_unassigned)} unassigned cards")
            # Use the existing completion logic
            continue
        
        print(f"   ⚠️  Only {len(suitable_unassigned)} suitable unassigned cards, need {cards_needed}")
        print(f"   🔄 Searching for reorganization opportunities...")
        
        # Look for potential donor decks that can spare cards and accept unassigned cards
        reorganization_opportunities = []
        
        for donor_theme, donor_deck in updated_decks.items():
            if len(donor_deck) != target_deck_size:  # Only reorganize with complete decks
                continue
                
            donor_config = ALL_THEMES[donor_theme]
            donor_colors = set(donor_config['colors'])
            
            # Check if donor can accept unassigned cards (specifically creatures from unassigned)
            unassigned_creatures = unassigned_cards[
                unassigned_cards['Type'].str.contains('Creature', case=False, na=False)
            ]
            
            compatible_creatures_for_donor = []
            for _, creature in unassigned_creatures.iterrows():
                creature_colors = set(str(creature['Color'])) if pd.notna(creature['Color']) and str(creature['Color']) != 'nan' else set()
                if not creature_colors or creature_colors.issubset(donor_colors):
                    compatible_creatures_for_donor.append(creature)
            
            if not compatible_creatures_for_donor:
                continue
                
            # Check if donor has room for creatures
            donor_creatures = donor_deck[donor_deck['Type'].str.contains('Creature', case=False, na=False)]
            if len(donor_creatures) >= 9:
                continue
                
            # Check if donor has spare spells
            donor_spells = donor_deck[~donor_deck['Type'].str.contains('Creature|Land', case=False, na=False)]
            if len(donor_spells) <= 2:  # Need at least 3 spells to spare one
                continue
                
            # This donor could potentially help
            reorganization_opportunities.append({
                'donor_theme': donor_theme,
                'donor_deck': donor_deck,
                'spare_spells': donor_spells,
                'creatures_room': 9 - len(donor_creatures),
                'compatible_creatures': compatible_creatures_for_donor[:1]  # Just take one
            })
        
        # Try the best reorganization opportunity
        if reorganization_opportunities:
            # Sort by number of spare spells (prefer decks with more spare spells)
            reorganization_opportunities.sort(key=lambda x: len(x['spare_spells']), reverse=True)
            
            best_opportunity = reorganization_opportunities[0]
            donor_theme = best_opportunity['donor_theme']
            donor_deck = best_opportunity['donor_deck']
            spare_spells = best_opportunity['spare_spells']
            compatible_creatures = best_opportunity['compatible_creatures']
            
            print(f"   🔄 Reorganization found: {donor_theme} ↔ unassigned cards")
            
            # Take one spell from donor
            spell_to_take = spare_spells.iloc[0]
            print(f"      Moving '{spell_to_take['name']}' from {donor_theme} to {theme_name}")
            
            # Give one creature to donor
            if compatible_creatures:
                creature_to_give = compatible_creatures[0]
                print(f"      Moving '{creature_to_give['name']}' from unassigned to {donor_theme}")
                
                # Execute the reorganization
                # Remove spell from donor deck
                updated_donor = donor_deck[donor_deck['name'] != spell_to_take['name']].copy()
                
                # Add creature to donor deck
                creature_df = pd.DataFrame([creature_to_give])
                creature_df['theme'] = donor_theme
                updated_donor = pd.concat([updated_donor, creature_df], ignore_index=True)
                updated_decks[donor_theme] = updated_donor
                
                # Add spell to incomplete deck
                spell_df = pd.DataFrame([spell_to_take])
                spell_df['theme'] = theme_name
                updated_incomplete = pd.concat([current_deck, spell_df], ignore_index=True)
                updated_decks[theme_name] = updated_incomplete
                
                # Remove creature from unassigned
                unassigned_cards = unassigned_cards[unassigned_cards['name'] != creature_to_give['name']]
                
                reorganizations_made += 1
                
                new_incomplete_size = len(updated_incomplete)
                print(f"      ✅ {theme_name}: {len(current_deck)} → {new_incomplete_size} cards")
                print(f"      ✅ {donor_theme}: still {len(updated_donor)} cards")
                
                if new_incomplete_size == target_deck_size:
                    print(f"      🎉 {theme_name} is now complete!")
        
        if not reorganization_opportunities:
            print(f"   ❌ No reorganization opportunities found for {theme_name}")
    
    print(f"\n📊 REORGANIZATION SUMMARY:")
    print(f"🔄 Reorganizations performed: {reorganizations_made}")
    
    if reorganizations_made > 0:
        print(f"✅ Successfully reorganized cards between decks")
    else:
        print(f"⚠️  No beneficial reorganizations were possible")
    
    return updated_decks


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
            'artifacts': 0,
            'avg_cmc': 0,
            'color_distribution': {},
            'type_distribution': {}
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
    avg_cmc = non_lands['CMC'].mean() if not non_lands.empty else 0
    
    # Color distribution
    color_counts = deck_df['Color'].value_counts().to_dict()
    
    # Type distribution
    type_distribution = {
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
        'artifacts': len(artifacts),
        'avg_cmc': avg_cmc,
        'color_distribution': color_counts,
        'type_distribution': type_distribution,
        'creature_list': creatures['name'].tolist() if not creatures.empty else [],
        'land_list': lands['name'].tolist() if not lands.empty else []
    }


def print_deck_summary(deck_dataframes: Dict[str, pd.DataFrame]):
    """
    Print a comprehensive summary of all constructed decks.
    
    Args:
        deck_dataframes: Dictionary of theme name -> deck DataFrame
    """
    
    print("\n🎯 JUMPSTART CUBE CONSTRUCTION COMPLETE")
    print("=" * 60)
    
    successful_decks = 0
    incomplete_decks = 0
    total_cards_used = 0
    
    for theme_name, deck_df in deck_dataframes.items():
        analysis = analyze_deck_composition(deck_df, theme_name)
        
        if analysis['total_cards'] == 13:
            successful_decks += 1
        elif analysis['total_cards'] > 0:
            incomplete_decks += 1
            
        total_cards_used += analysis['total_cards']
    
    print(f"✅ Successfully built decks: {successful_decks}")
    print(f"⚠️  Incomplete decks: {incomplete_decks}")
    print(f"📊 Total cards used: {total_cards_used}")
    print(f"🎲 Total themes: {len(deck_dataframes)}")
    
    if incomplete_decks > 0:
        print(f"\n⚠️  INCOMPLETE DECKS:")
        for theme_name, deck_df in deck_dataframes.items():
            if 0 < len(deck_df) < 13:
                shortage = 13 - len(deck_df)
                print(f"   {theme_name}: {len(deck_df)}/13 cards ({shortage} short)")
