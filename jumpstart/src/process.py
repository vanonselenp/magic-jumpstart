from src.coherence import analyze_deck_theme_coherence_enhanced
from src.deck import display_card_details
from src.improve import apply_swap, display_swap_recommendations, find_best_card_swaps_for_deck

# Global variable to track recent swaps to prevent oscillation
_recent_swaps = []
_max_swap_history = 10  # Remember last 10 swaps

def _is_swap_recently_reversed(deck_name, remove_cards, add_cards):
    """Check if this swap would reverse a recent swap"""
    for recent_swap in _recent_swaps:
        if (recent_swap['deck'] == deck_name and 
            set(recent_swap['removed']) == set(add_cards) and  # What we're adding was recently removed
            set(recent_swap['added']) == set(remove_cards)):   # What we're removing was recently added
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
):
    coherence_results = analyze_deck_theme_coherence_enhanced(cube_df, oracle_df)

    worst_deck = min(coherence_results.items(), key=lambda x: x[1]['overall_coherence'])
    specific_deck = worst_deck[0]
    original_coherence = float(coherence_results[specific_deck]['overall_coherence'])

    if specific_deck in coherence_results:
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
        print(updated_coherence_results[specific_deck]['overall_coherence'])
        print(updated_coherence_results[specific_deck])

        if updated_coherence_results[specific_deck]['overall_coherence'] > original_coherence:
            print(f"Improved {specific_deck} coherence from {original_coherence:.1f} to {updated_coherence_results[specific_deck]['overall_coherence']:.1f}")
            return updated_cube
        
        return cube_df  # Return original cube if no improvements were made

    else:
        print(f"Deck '{specific_deck}' not found. Available decks:")
        for deck in sorted(coherence_results.keys()):
            score = coherence_results[deck]['overall_coherence']
        return cube_df  # Return original cube if specific deck not found


def clear_swap_history():
    """Clear the swap history - useful when starting a fresh optimization run"""
    global _recent_swaps
    _recent_swaps = []
    print("Swap history cleared")