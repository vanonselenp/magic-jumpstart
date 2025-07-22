from src.coherence import analyze_deck_theme_coherence_enhanced
from src.deck import display_card_details
from src.improve import apply_swap, display_swap_recommendations, find_best_card_swaps_for_deck


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

        # Check if there are any swaps to apply
        if specific_swaps['best_swaps']:
            updated_cube = apply_swap(
                cube_df, 
                specific_deck,
                remove_cards=specific_swaps['best_swaps']['remove'],
                add_cards=specific_swaps['best_swaps']['add'],
                oracle_df=oracle_df
            )
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