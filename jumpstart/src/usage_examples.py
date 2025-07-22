"""
Example usage of the refactored jumpstart deck construction.

This file demonstrates how to use the new, cleaner architecture.
"""

# Example usage (this would go in your notebook or main script):

# Method 1: Use the refactored version directly
from src.construct_refactored import construct_jumpstart_decks_refactored, print_detailed_deck_analysis

def build_jumpstart_cube_refactored(oracle_df):
    """Build jumpstart cube using the refactored, cleaner method."""
    
    # Build all decks using the refactored architecture
    deck_dataframes = construct_jumpstart_decks_refactored(oracle_df)
    
    # Optional: Print detailed analysis
    print_detailed_deck_analysis(deck_dataframes)
    
    return deck_dataframes

# Method 2: Compare both versions (for validation)
from src.construct_refactored import compare_deck_construction_methods

def validate_refactored_version(oracle_df):
    """Validate the refactored version against the original."""
    return compare_deck_construction_methods(oracle_df)

# Method 3: Use individual components for custom workflows
from src.construct_refactored import DeckBuilder, CardConstraints, analyze_deck_composition

def custom_deck_building_workflow(oracle_df):
    """Example of using individual components for custom workflows."""
    
    # Create custom constraints
    custom_constraints = CardConstraints(
        max_creatures=8,      # Reduce creature count
        max_lands_dual=4,     # Allow more lands for dual-color
        target_deck_size=15   # Larger decks
    )
    
    # Build with custom constraints
    builder = DeckBuilder(oracle_df, custom_constraints)
    deck_dataframes = builder.build_all_decks()
    
    # Analyze specific decks
    for theme_name, deck_df in deck_dataframes.items():
        if len(deck_df) > 0:
            analysis = analyze_deck_composition(deck_df, theme_name)
            print(f"{theme_name}: {analysis['total_cards']} cards, "
                  f"C:{analysis['creatures']} L:{analysis['lands']}")
    
    return deck_dataframes

# Migration guide:
"""
MIGRATION FROM ORIGINAL TO REFACTORED VERSION:

OLD CODE:
    from src.construct import construct_jumpstart_decks
    decks = construct_jumpstart_decks(oracle_df)

NEW CODE:
    from src.construct_refactored import construct_jumpstart_decks_refactored
    decks = construct_jumpstart_decks_refactored(oracle_df)

OR (for easy side-by-side testing):
    from src.construct_refactored import construct_jumpstart_decks_v2
    decks = construct_jumpstart_decks_v2(oracle_df)

BENEFITS OF REFACTORED VERSION:
✅ Cleaner, more maintainable code
✅ Better separation of concerns  
✅ Easier to test individual components
✅ More flexible constraint system
✅ Better error handling and debugging
✅ Same functionality with improved architecture
"""
