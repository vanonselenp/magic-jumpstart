from src.coherence import analyze_deck_theme_coherence_enhanced
from src.deck import display_card_details
from src.improve import apply_swap, display_swap_recommendations, find_best_card_swaps_for_deck

# Global variable to track recent swaps to prevent oscillation
_recent_swaps = []
_max_swap_history = 20  # Remember last 20 swaps (increased from 10)
_min_improvement_threshold = 0.1  # Minimum improvement required for a swap

def _is_swap_recently_reversed(deck_name, remove_cards, add_cards):
    """Check if this swap would reverse a recent swap or if these cards were recently swapped"""
    for recent_swap in _recent_swaps:
        # Check for exact reversal (what we're adding was recently removed, what we're removing was recently added)
        if (recent_swap['deck'] == deck_name and 
            set(recent_swap['removed']) == set(add_cards) and  
            set(recent_swap['added']) == set(remove_cards)):   
            return True
            
        # Also check if the same cards have been involved in recent swaps between ANY decks
        # This prevents cards from bouncing between similar decks
        if (set(recent_swap['removed']) == set(remove_cards) or 
            set(recent_swap['added']) == set(add_cards)):
            return True
            
    return False

def _add_swap_to_history(deck_name, remove_cards, add_cards):
    """Add a swap to the history"""
    global _recent_swaps
    swap_record = {
        'deck': deck_name,
        'removed': remove_cards,
        'added': add_cards
    }
    _recent_swaps.append(swap_record)
    
    # Keep only the most recent swaps
    if len(_recent_swaps) > _max_swap_history:
        _recent_swaps = _recent_swaps[-_max_swap_history:]

def optimize_deck_coherence(
    cube_df, 
    oracle_df, 
    deck_name=None
):
    """
    Optimize the coherence of a specific deck by finding and applying the best card swaps.
    
    Args:
        cube_df: Current jumpstart cube dataframe
        oracle_df: Oracle data with all available cards
        deck_name: Name of the specific deck to optimize. If None, optimizes the worst performing deck.
    
    Returns:
        Updated cube dataframe with optimizations applied
    """
    coherence_results = analyze_deck_theme_coherence_enhanced(cube_df, oracle_df)

    # If no specific deck provided, find the worst performing deck
    if deck_name is None:
        worst_deck = min(coherence_results.items(), key=lambda x: x[1]['overall_coherence'])
        specific_deck = worst_deck[0]
        print(f"No deck specified. Optimizing worst performing deck: {specific_deck}")
    else:
        specific_deck = deck_name
        print(f"Optimizing specified deck: {specific_deck}")
    
    if specific_deck not in coherence_results:
        print(f"Deck '{specific_deck}' not found. Available decks:")
        for deck in sorted(coherence_results.keys()):
            score = coherence_results[deck]['overall_coherence']
            print(f"  {deck}: {score:.1f}")
        return cube_df  # Return original cube if specific deck not found
    
    original_coherence = float(coherence_results[specific_deck]['overall_coherence'])
    
    # Get swap recommendations for this specific deck
    specific_swaps = find_best_card_swaps_for_deck(
        specific_deck, 
        cube_df, 
        oracle_df, 
        coherence_results, 
        num_swaps=2
    )
    
    # Display the recommendations
    display_swap_recommendations(specific_swaps)

    # Check if there was an error or no swaps found
    if 'error' in specific_swaps:
        print(f"No swaps available for {specific_deck}: {specific_swaps['error']}")
        return cube_df

    # Check if there are any swaps to apply and they haven't been recently reversed
    if 'best_swaps' in specific_swaps and specific_swaps['best_swaps']:
        remove_cards = specific_swaps['best_swaps']['remove']
        add_cards = specific_swaps['best_swaps']['add']
        
        # Check if this swap would reverse a recent swap
        if _is_swap_recently_reversed(specific_deck, remove_cards, add_cards):
            print(f"Skipping swap for {specific_deck} - would reverse a recent swap (preventing oscillation)")
            return cube_df
        
        updated_cube = apply_swap(
            cube_df, 
            specific_deck,
            remove_cards=remove_cards,
            add_cards=add_cards,
            oracle_df=oracle_df
        )
        
        # Track this swap
        _add_swap_to_history(specific_deck, remove_cards, add_cards)
    else:
        print("No available swaps to apply for this deck.")
        display_card_details(specific_deck, cube_df, coherence_results, oracle_df)
        updated_cube = cube_df

    updated_coherence_results = analyze_deck_theme_coherence_enhanced(updated_cube, oracle_df)
    new_coherence = updated_coherence_results[specific_deck]['overall_coherence']
    improvement = new_coherence - original_coherence
    
    print(f"Coherence change: {original_coherence:.2f} → {new_coherence:.2f} (improvement: {improvement:.2f})")
    
    if improvement > 0:
        print(f"✅ Improved {specific_deck} coherence from {original_coherence:.1f} to {new_coherence:.1f}")
        return updated_cube
    else:
        print(f"❌ No improvement achieved")
        return cube_df  # Return original cube if no improvements were made

def clear_swap_history():
    """Clear the swap history - useful when starting a fresh optimization run"""
    global _recent_swaps
    _recent_swaps = []
    print("Swap history cleared")