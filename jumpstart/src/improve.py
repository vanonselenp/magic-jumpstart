from IPython.display import Markdown, display
import pandas as pd

from src.deck import calculate_card_theme_score, is_card_playable_in_colors


def find_best_card_swaps_for_deck(deck_name, cube_df, oracle_df, coherence_results, num_swaps=2):
    """
    Find the best card swaps to improve a deck's coherence.
    
    Args:
        deck_name: Name of the deck to improve
        cube_df: Current jumpstart cube dataframe
        oracle_df: Oracle data with all available cards
        coherence_results: Results from analyze_deck_theme_coherence_enhanced
        num_swaps: Number of cards to swap (default: 2)
    
    Returns:
        Dictionary with swap recommendations including before/after coherence scores
    """
    
    if deck_name not in coherence_results:
        return {'error': f"Deck '{deck_name}' not found in coherence results"}
    
    # Get current deck data
    current_deck_cards = cube_df[cube_df['Tags'] == deck_name].copy()
    deck_analysis = coherence_results[deck_name]
    current_coherence = deck_analysis['overall_coherence']
    expected_themes = deck_analysis['expected_themes']
    deck_colors = deck_analysis['deck_colors']
    
    display(Markdown(f"Analyzing deck: {deck_name}"))
    display(Markdown(f"Current coherence: {current_coherence:.1f}"))
    display(Markdown(f"Expected themes: {', '.join(expected_themes)}"))
    display(Markdown(f"Deck colors: {deck_colors}"))
    
    # Get potential candidate cards
    candidates = get_candidate_cards_for_swap(deck_name, cube_df, oracle_df, deck_colors, expected_themes)
    
    display(Markdown(f"Found {len(candidates)} candidate cards to consider"))
    
    if len(candidates) < num_swaps:
        return {
            'error': f"Not enough candidate cards found. Need {num_swaps}, found {len(candidates)}",
            'candidates_found': len(candidates)
        }
    
    # Find worst performing cards in current deck to consider removing
    worst_cards = find_worst_cards_in_deck(current_deck_cards, oracle_df, expected_themes, deck_colors)
    
    display(Markdown(f"Identified {len(worst_cards)} cards as potential removal candidates"))
    
    # Try different swap combinations
    best_swaps = find_optimal_swaps(
        current_deck_cards, candidates, worst_cards, 
        oracle_df, expected_themes, deck_colors, 
        num_swaps, current_coherence
    )
    
    return {
        'deck_name': deck_name,
        'current_coherence': current_coherence,
        'expected_themes': expected_themes,
        'best_swaps': best_swaps,
        'total_candidates': len(candidates),
        'removal_candidates': len(worst_cards)
    }


def get_candidate_cards_for_swap(deck_name, cube_df, oracle_df, deck_colors, expected_themes):
    """Get all cards that could potentially be good additions to this deck"""
    
    # Get cards already in the cube
    assigned_cards = set(cube_df['Name'].tolist())
    
    # Get cards from other decks that could be swapped
    other_deck_cards = cube_df[cube_df['Tags'] != deck_name]
    
    # Get unassigned cards from oracle
    candidates = []
    
    # Add unassigned cards from oracle that fit color identity and themes
    for _, card in oracle_df.iterrows():
        card_name = card['name']
        
        # Skip if already assigned to current deck
        if card_name in assigned_cards:
            continue
            
        # Skip land cards
        card_type = str(card.get('Type', '')).lower()
        if 'land' in card_type:
            continue
            
        # Check color compatibility
        if not is_card_playable_in_colors(card, deck_colors):
            continue
            
        # Calculate theme score for this card
        theme_score, _ = calculate_card_theme_score(card, expected_themes)
        
        # Only consider cards with some theme relevance
        if theme_score > 0:
            candidates.append({
                'card': card,
                'theme_score': theme_score,
                'source': 'unassigned',
                'current_deck': None
            })
    
    # Add cards from other decks that might fit better here
    for _, other_card in other_deck_cards.iterrows():
        oracle_card = oracle_df[oracle_df['name'] == other_card['Name']]
        if oracle_card.empty:
            continue
            
        card = oracle_card.iloc[0]
        
        # Skip land cards
        card_type = str(card.get('Type', '')).lower()
        if 'land' in card_type:
            continue
        
        # Check color compatibility
        if not is_card_playable_in_colors(card, deck_colors):
            continue
            
        # Calculate theme score
        theme_score, _ = calculate_card_theme_score(card, expected_themes)
        
        # Only consider if theme score is decent
        if theme_score > 0:
            candidates.append({
                'card': card,
                'theme_score': theme_score,
                'source': 'other_deck',
                'current_deck': other_card['Tags']
            })
    
    # Sort by theme score
    candidates.sort(key=lambda x: x['theme_score'], reverse=True)
    
    return candidates


def find_worst_cards_in_deck(deck_cards, oracle_df, expected_themes, deck_colors):
    """Identify the worst performing cards in the current deck for potential removal"""
    
    card_scores = []
    
    for _, card_row in deck_cards.iterrows():
        card_name = card_row['Name']
        oracle_card = oracle_df[oracle_df['name'] == card_name]
        
        if oracle_card.empty:
            # Card not found in oracle - definitely a removal candidate
            card_scores.append({
                'name': card_name,
                'score': -1,
                'reason': 'Not found in oracle data'
            })
            continue
        
        card = oracle_card.iloc[0]
        
        # Calculate various scores
        theme_score, _ = calculate_card_theme_score(card, expected_themes)
        color_score = 1.0 if is_card_playable_in_colors(card, deck_colors) else 0.0
        
        # Check mana cost efficiency
        cmc = card.get('CMC', 0)
        try:
            cmc = float(cmc) if not pd.isna(cmc) else 0
        except:
            cmc = 0
        
        mana_score = 1.0
        if cmc > 6:  # Very expensive cards
            mana_score = 0.5
        elif cmc > 4:  # Moderately expensive
            mana_score = 0.8
        
        # Combine scores
        overall_score = (theme_score * 0.6) + (color_score * 0.3) + (mana_score * 0.1)
        
        card_scores.append({
            'name': card_name,
            'score': overall_score,
            'theme_score': theme_score,
            'color_score': color_score,
            'mana_score': mana_score,
            'cmc': cmc
        })
    
    # Sort by score (worst first)
    card_scores.sort(key=lambda x: x['score'])
    
    return card_scores


def find_optimal_swaps(current_deck_cards, candidates, worst_cards, oracle_df, expected_themes, deck_colors, num_swaps, current_coherence):
    """Find the optimal combination of swaps to maximize coherence improvement"""
    
    from itertools import combinations
    
    best_improvement = 0
    best_swaps = []
    
    # Try combinations of cards to remove
    for cards_to_remove in combinations(worst_cards[:min(len(worst_cards), 5)], num_swaps):
        # Try combinations of cards to add
        for cards_to_add in combinations(candidates[:min(len(candidates), 10)], num_swaps):
            
            # Calculate the potential improvement
            improvement = calculate_swap_improvement(
                current_deck_cards, cards_to_remove, cards_to_add, 
                oracle_df, expected_themes, deck_colors
            )
            
            if improvement > best_improvement:
                best_improvement = improvement
                best_swaps = {
                    'remove': [card['name'] for card in cards_to_remove],
                    'add': [candidate['card']['name'] for candidate in cards_to_add],
                    'improvement': improvement,
                    'new_coherence': current_coherence + improvement,
                    'details': {
                        'removed_cards': cards_to_remove,
                        'added_cards': cards_to_add
                    }
                }
    
    return best_swaps


def calculate_swap_improvement(current_deck_cards, cards_to_remove, cards_to_add, oracle_df, expected_themes, deck_colors):
    """Calculate the coherence improvement from a specific swap"""
    
    # Calculate current theme contribution of cards being removed
    removed_theme_score = 0
    for card_info in cards_to_remove:
        removed_theme_score += card_info['theme_score']
    
    # Calculate theme contribution of cards being added
    added_theme_score = 0
    for candidate in cards_to_add:
        added_theme_score += candidate['theme_score']
    
    # Simple improvement calculation (this could be made more sophisticated)
    theme_improvement = added_theme_score - removed_theme_score
    
    # Scale to coherence points (rough approximation)
    coherence_improvement = theme_improvement * 5  # Adjust multiplier as needed
    
    return coherence_improvement


def display_swap_recommendations(swap_results):
    """Display the swap recommendations in a nice format"""
    
    if 'error' in swap_results:
        display(Markdown(f"❌ **Error:** {swap_results['error']}"))
        return
    
    deck_name = swap_results['deck_name']
    current_coherence = swap_results['current_coherence']
    best_swaps = swap_results['best_swaps']
    
    display(Markdown(f"# 🔄 Swap Recommendations for {deck_name}"))
    
    if not best_swaps:
        display(Markdown("❌ **No beneficial swaps found.** The deck may already be well-optimized, or there may not be suitable replacement cards available."))
        return
    
    display(Markdown(f"**Projected New Coherence:** {best_swaps['new_coherence']:.1f}/100 (+{best_swaps['improvement']:.1f})"))
    
    display(Markdown("### Cards to Remove:"))
    for card in best_swaps['remove']:
        # Find the card info for context
        removed_details = next((c for c in best_swaps['details']['removed_cards'] if c['name'] == card), None)
        if removed_details:
            display(Markdown(f"- **{card}** (Theme Score: {removed_details['theme_score']:.1f}, CMC: {removed_details.get('cmc', 'N/A')})"))
        else:
            display(Markdown(f"- **{card}**"))
    
    display(Markdown("### Cards to Add:"))
    for i, card in enumerate(best_swaps['add']):
        # Find the card info for context
        added_details = best_swaps['details']['added_cards'][i]
        source = added_details['source']
        current_deck = added_details.get('current_deck', '')
        source_text = f"from {current_deck}" if source == 'other_deck' else "from oracle pool"
        
        display(Markdown(f"- **{card}** (Theme Score: {added_details['theme_score']:.1f}) - {source_text}"))
    

def apply_swap(cube_df, deck_name, remove_cards, add_cards, oracle_df):
    """
    Function to execute a card swap with color validation and automatic replacement.
    
    Args:
        cube_df: Current jumpstart cube dataframe
        deck_name: Name of the deck to modify
        remove_cards: List of card names to remove from the deck
        add_cards: List of card names to add to the deck
        oracle_df: Oracle data for new cards
    
    Returns:
        Updated cube dataframe
    """
    from src.deck import get_deck_colour, extract_theme_from_deck_name
    
    updated_df = cube_df.copy()
    
    # Get target deck colors for validation
    target_deck_colors = get_deck_colour(deck_name)
    
    # Track which cards came from which decks for proper swapping
    cards_to_swap_back = []
    source_deck_colors = []
    
    # Add cards first and track where they came from
    for card_name in add_cards:
        # Check if card exists in another deck (move it)
        existing_mask = updated_df['Name'] == card_name
        if existing_mask.any():
            # Get the source deck before we change it
            source_deck = updated_df.loc[existing_mask, 'Tags'].iloc[0]
            source_colors = get_deck_colour(source_deck)
            cards_to_swap_back.append(source_deck)
            source_deck_colors.append(source_colors)
            
            # Move the card to target deck
            updated_df.loc[existing_mask, 'Tags'] = deck_name
        else:
            # Add from oracle
            oracle_card = oracle_df[oracle_df['name'] == card_name]
            if not oracle_card.empty:
                # Match the exact structure of JumpstartCube CSV
                new_row = {
                    'Name': card_name,
                    'Set': 'Mixed',  # Default value used in your cube
                    'Collector Number': '',  # Empty as in your cube
                    'Rarity': 'common',  # Default value used in your cube
                    'Color Identity': oracle_card.iloc[0].get('Color', ''),
                    'Type': oracle_card.iloc[0].get('Type', ''),
                    'Mana Cost': '',  # Empty as in your cube
                    'CMC': oracle_card.iloc[0].get('CMC', 0),
                    'Power': '',  # Empty as in your cube
                    'Toughness': '',  # Empty as in your cube
                    'Tags': deck_name
                }
                updated_df = pd.concat([updated_df, pd.DataFrame([new_row])], ignore_index=True)
            cards_to_swap_back.append(None)  # No deck to swap back to
            source_deck_colors.append(None)
    
    # Remove cards from target deck and place them in source decks (with color validation)
    for i, card_name in enumerate(remove_cards):
        # Create fresh mask each time since DataFrame may have changed
        mask = (updated_df['Name'] == card_name) & (updated_df['Tags'] == deck_name)
        if mask.any():
            source_deck = cards_to_swap_back[i] if i < len(cards_to_swap_back) else None
            source_colors = source_deck_colors[i] if i < len(source_deck_colors) else None
            
            if source_deck and source_colors:
                # Validate color compatibility before moving the card
                oracle_card = oracle_df[oracle_df['name'] == card_name]
                if not oracle_card.empty:
                    card_data = oracle_card.iloc[0]
                    if is_card_playable_in_colors(card_data, source_colors):
                        # Move the removed card to the source deck
                        updated_df.loc[mask, 'Tags'] = source_deck
                    else:
                        # Card doesn't fit color-wise in source deck, find replacement
                        print(f"Card {card_name} not color-compatible with {source_deck}, finding replacement...")
                        replacement_card = find_replacement_card(oracle_df, updated_df, source_deck, source_colors)
                        
                        if replacement_card is not None:
                            # Add replacement card to source deck
                            new_row = {
                                'Name': replacement_card['name'],
                                'Set': 'Mixed',
                                'Collector Number': '',
                                'Rarity': 'common',
                                'Color Identity': replacement_card.get('Color', ''),
                                'Type': replacement_card.get('Type', ''),
                                'Mana Cost': '',
                                'CMC': replacement_card.get('CMC', 0),
                                'Power': '',
                                'Toughness': '',
                                'Tags': source_deck
                            }
                            updated_df = pd.concat([updated_df, pd.DataFrame([new_row])], ignore_index=True)
                            print(f"Added {replacement_card['name']} to {source_deck} as replacement")
                        else:
                            print(f"No suitable replacement found for {source_deck}")
                        
                        # Remove the incompatible card (create fresh mask)
                        fresh_mask = (updated_df['Name'] == card_name) & (updated_df['Tags'] == deck_name)
                        updated_df = updated_df.drop(updated_df[fresh_mask].index)
                else:
                    # Card not found in oracle, just remove it (create fresh mask)
                    fresh_mask = (updated_df['Name'] == card_name) & (updated_df['Tags'] == deck_name)
                    updated_df = updated_df.drop(updated_df[fresh_mask].index)
            else:
                # No source deck to swap to, just remove the card (create fresh mask)
                fresh_mask = (updated_df['Name'] == card_name) & (updated_df['Tags'] == deck_name)
                updated_df = updated_df.drop(updated_df[fresh_mask].index)
    
    return updated_df


def find_replacement_card(oracle_df, current_cube_df, deck_name, deck_colors):
    """
    Find the best unassigned card to replace a card that can't be moved to a deck.
    
    Args:
        oracle_df: Oracle data with all available cards
        current_cube_df: Current state of the cube
        deck_name: Name of the deck needing a replacement
        deck_colors: Color identity of the deck
    
    Returns:
        Best replacement card data or None if no suitable card found
    """
    from src.deck import extract_theme_from_deck_name
    
    # Get cards already in the cube
    assigned_cards = set(current_cube_df['Name'].tolist())
    
    # Get expected themes for this deck
    expected_themes = extract_theme_from_deck_name(deck_name)
    
    # Find unassigned cards that fit
    candidates = []
    
    for _, card in oracle_df.iterrows():
        card_name = card['name']
        
        # Skip if already assigned
        if card_name in assigned_cards:
            continue
            
        # Skip land cards
        card_type = str(card.get('Type', '')).lower()
        if 'land' in card_type:
            continue
            
        # Check color compatibility
        if not is_card_playable_in_colors(card, deck_colors):
            continue
            
        # Calculate theme score
        theme_score, _ = calculate_card_theme_score(card, expected_themes)
        
        # Only consider cards with some theme relevance
        if theme_score > 0:
            candidates.append((card, theme_score))
    
    # Sort by theme score and return the best one
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]  # Return the card data
    
    return None