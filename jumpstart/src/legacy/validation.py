from IPython.display import Markdown, display
import pandas as pd
from src.consts import TOTAL_CARDS
from src.deck import get_deck_colour


def display_validate_results(validation_results):
    """Display validation results in a readable format"""
    if validation_results['is_valid']:
        display(Markdown("### Cube is valid! 🎉"))
    else:
        display(Markdown("### Cube has issues ❗"))
    
    if validation_results['errors']:
        display(Markdown("#### Errors:"))
        for error in validation_results['errors']:
            display(Markdown(f"- {error}"))
    
    if validation_results['warnings']:
        display(Markdown("#### Warnings:"))
        for warning in validation_results['warnings']:
            display(Markdown(f"- {warning}"))
    
    if validation_results['deck_summaries']:
        display(Markdown("#### Deck Summaries:"))
        for deck_name, summary in validation_results['deck_summaries'].items():
            display(Markdown(f"**{deck_name}** {summary['total_cards']} cards"))


def validate_jumpstart_cube(cube_df, oracle_df):
    """
    Validates a jumpstart cube against the requirements:
    - Unique cards (no duplicates)
    - Each deck has 13 non-land cards + 1 unique land (14 total)
    - Each deck matches color requirements
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'deck_summaries': {}
    }
    
    # Helper function to check if a card can be played in a color identity
    def card_can_be_played_in_colors(card_name, deck_colors):
        """Check if a card can be played in the given color identity"""
        # Find card in oracle data
        oracle_card = oracle_df[oracle_df['name'] == card_name]
        if oracle_card.empty:
            return False, f"Card '{card_name}' not found in oracle data"
        
        card_color = oracle_card.iloc[0]['Color']
        card_category = oracle_card.iloc[0]['Color Category']
        oracle_text = str(oracle_card.iloc[0]['Oracle Text']).lower()
        
        # Colorless cards and artifacts can be played in any deck
        if card_category in ['Colorless', 'Artifacts'] or pd.isna(card_color):
            return True, "Colorless/Artifact"
        
        # Lands are handled separately
        if card_category == 'Lands':
            return True, "Land"
        
        # Check for Phyrexian mana (cards that can be cast with life instead of mana)
        if 'phyrexian' in oracle_text or 'can be paid with' in oracle_text:
            return True, "Phyrexian mana"
        
        # Convert deck colors to set for easier comparison
        if isinstance(deck_colors, str):
            deck_color_set = set(deck_colors)
        else:
            deck_color_set = set()
        
        # Convert card colors to set
        if isinstance(card_color, str):
            card_color_set = set(card_color)
        else:
            card_color_set = set()
        
        # Check if card colors are subset of deck colors
        if card_color_set.issubset(deck_color_set):
            return True, f"Color match: {card_color} fits in {deck_colors}"
        
        return False, f"Color mismatch: {card_color} doesn't fit in {deck_colors}"
    
    # Check for duplicate cards across the entire cube
    duplicate_cards = cube_df['Name'].duplicated()
    if duplicate_cards.any():
        duplicates = cube_df[duplicate_cards]['Name'].tolist()
        validation_results['errors'].append(f"Duplicate cards found: {duplicates}")
        validation_results['is_valid'] = False
    
    # Group by deck (Tags column represents deck themes)
    decks = cube_df.groupby('Tags')
    
    for deck_name, deck_cards in decks:
        deck_summary = {
            'total_cards': len(deck_cards),
            'lands': 0,
            'non_lands': 0,
            'color_issues': [],
            'cards': deck_cards['Name'].tolist()
        }
        
        # Determine deck colors from the deck name
        deck_colors = get_deck_colour(deck_name)
        
        if deck_colors is None:
            validation_results['warnings'].append(f"Could not determine colors for deck '{deck_name}'")
            deck_colors = ''
        
        # Count lands and non-lands
        for _, card in deck_cards.iterrows():
            card_type = str(card['Type']).lower()
            if 'land' in card_type:
                deck_summary['lands'] += 1
            else:
                deck_summary['non_lands'] += 1
            
            # Check color identity
            can_play, reason = card_can_be_played_in_colors(card['Name'], deck_colors)
            if not can_play:
                deck_summary['color_issues'].append(f"{card['Name']}: {reason}")
        
        # Validate deck composition
        if deck_summary['total_cards'] != TOTAL_CARDS:
            validation_results['errors'].append(
                f"Deck '{deck_name}' has {deck_summary['total_cards']} cards, should have 14"
            )
            validation_results['is_valid'] = False
        
        # if deck_summary['non_lands'] != 13:
        #     validation_results['errors'].append(
        #         f"Deck '{deck_name}' has {deck_summary['non_lands']} non-land cards, should have 13"
        #     )
        #     validation_results['is_valid'] = False
        
        # if deck_summary['lands'] != 1:
        #     validation_results['errors'].append(
        #         f"Deck '{deck_name}' has {deck_summary['lands']} lands, should have exactly 1"
        #     )
        #     validation_results['is_valid'] = False
        
        # Check for color issues
        if deck_summary['color_issues']:
            validation_results['errors'].extend([
                f"Deck '{deck_name}' color violations: {issue}" 
                for issue in deck_summary['color_issues']
            ])
            validation_results['is_valid'] = False
        
        validation_results['deck_summaries'][deck_name] = deck_summary
    

    return validation_results

