import pandas as pd
from src.consts import theme_keywords, guild_themes

def extract_theme_from_deck_name(deck_name):
    """Extract the main theme from deck name"""
    deck_lower = deck_name.lower()
    themes = []
    
    for theme in theme_keywords.keys():
        if theme.lower() in deck_lower:
            themes.append(theme)
    
    for guild, guild_themes_list in guild_themes.items():
        if guild in deck_lower:
            themes.extend(guild_themes_list)
    
    return list(set(themes)) if themes else ['Unknown']

def get_deck_colour(deck_name):
    deck_colors = None
    if any(combo in deck_name for combo in ['Azorius', 'WU']):
        deck_colors = 'WU'
    elif any(combo in deck_name for combo in ['Dimir', 'UB']):
        deck_colors = 'UB'
    elif any(combo in deck_name for combo in ['Rakdos', 'BR']):
        deck_colors = 'BR'
    elif any(combo in deck_name for combo in ['Gruul', 'RG']):
        deck_colors = 'RG'
    elif any(combo in deck_name for combo in ['Selesnya', 'GW']):
        deck_colors = 'GW'
    elif any(combo in deck_name for combo in ['Orzhov', 'WB']):
        deck_colors = 'WB'
    elif any(combo in deck_name for combo in ['Izzet', 'UR']):
        deck_colors = 'UR'
    elif any(combo in deck_name for combo in ['Golgari', 'BG']):
        deck_colors = 'BG'
    elif any(combo in deck_name for combo in ['Boros', 'RW']):
        deck_colors = 'RW'
    elif any(combo in deck_name for combo in ['Simic', 'UG']):
        deck_colors = 'UG'
    elif 'White' in deck_name:
        deck_colors = 'W'
    elif 'Blue' in deck_name:
        deck_colors = 'U'
    elif 'Black' in deck_name:
        deck_colors = 'B'
    elif 'Red' in deck_name:
        deck_colors = 'R'
    elif 'Green' in deck_name:
        deck_colors = 'G'
    return deck_colors

def get_available_cards_for_deck(deck_name, cube_df, oracle_df, deck_colors):
    """Find all cards that could potentially be added to this deck"""
    
    # Get all cards currently assigned to other decks or unassigned
    assigned_cards = set(cube_df['Name'].tolist())
    
    # Get all cards from oracle that fit the color identity
    available_cards = []
    
    for _, card in oracle_df.iterrows():
        card_name = card['name']
        
        # Skip if already in cube
        if card_name in assigned_cards:
            continue
            
        # Check color compatibility
        if is_card_playable_in_colors(card, deck_colors):
            available_cards.append(card)
    
    # Also include unassigned cards from cube (if any)
    unassigned_cube_cards = cube_df[cube_df['Tags'].isna() | (cube_df['Tags'] == '')]
    for _, card in unassigned_cube_cards.iterrows():
        oracle_card = oracle_df[oracle_df['name'] == card['Name']]
        if not oracle_card.empty:
            available_cards.append(oracle_card.iloc[0])
    
    return available_cards

def is_card_playable_in_colors(card, deck_colors):
    """Check if a card can be played in the given color identity"""
    if not deck_colors:
        return True
    
    card_color = card.get('Color', '')
    card_category = card.get('Color Category', '')
    
    # Handle truly colorless cards (artifacts, lands, etc.)
    if card_category in ['Colorless', 'Artifacts', 'Lands']:
        return True
    
    # Handle devoid cards - they are colorless but should respect their color category
    if pd.isna(card_color):
        # For devoid cards, use color category to determine color identity
        if card_category == 'Green':
            effective_color = 'G'
        elif card_category == 'Blue':
            effective_color = 'U'
        elif card_category == 'Black':
            effective_color = 'B'
        elif card_category == 'Red':
            effective_color = 'R'
        elif card_category == 'White':
            effective_color = 'W'
        elif card_category == 'Multicolored':
            # For multicolored devoid cards, we need to be more careful
            # For now, allow them in multicolored decks only
            if isinstance(deck_colors, str):
                return len(deck_colors) > 1  # Multi-character means multicolored
            elif isinstance(deck_colors, list):
                return len(deck_colors) > 1  # Multiple colors in list
            return False
        else:
            # Truly colorless cards (no color category match)
            return True
        
        # Check if the effective color matches deck colors
        if isinstance(deck_colors, str):
            return effective_color in deck_colors
        elif isinstance(deck_colors, list):
            return effective_color in deck_colors
    
    # Check if card colors fit deck colors (normal colored cards)
    if isinstance(card_color, str) and isinstance(deck_colors, str):
        card_color_set = set(card_color)
        deck_color_set = set(deck_colors)
        return card_color_set.issubset(deck_color_set)
    
    return False

def display_card_details(specific_deck, cube_df, coherence_results, oracle_df):
    current_deck = cube_df[cube_df['Tags'] == specific_deck]
    for card in current_deck['Name']:
        expected_themes = coherence_results[specific_deck]['expected_themes']
        current_card = oracle_df[oracle_df['name'] == card].iloc[0]  # Get the first row for the card
        score, themes = calculate_card_theme_score(current_card, expected_themes)
        print(f"Card: {card}, Score: {score}, Themes: {themes}")

def calculate_card_theme_score(card, expected_themes):
    """Enhanced version of theme score calculation"""
    if not expected_themes or expected_themes == ['Unknown']:
        return 0.0, []
    
    oracle_text = str(card.get('Oracle Text', '')).lower()
    card_type = str(card.get('Type', '')).lower()
    card_name = str(card.get('name', '')).lower() or str(card.get('Name', '')).lower()
    
    total_score = 0
    matching_themes = []
    
    for theme in expected_themes:
        if theme in theme_keywords:
            theme_words = theme_keywords[theme]
            # Count matches in oracle text, type, and name
            matches = sum(1 for word in theme_words if word in oracle_text or word in card_type or word in card_name)
            total_score += matches
            matching_themes.append(theme)
        
        # Special handling for Big Creatures theme
        if theme == "Big Creatures" and 'creature' in card_type:
            power = card.get('Power', 0)
            toughness = card.get('Toughness', 0)
            
            try:
                power = float(power) if not pd.isna(power) else 0
                toughness = float(toughness) if not pd.isna(toughness) else 0
                
                if power >= 5 or toughness >= 5:
                    total_score += 2  # Bonus for big creatures
                    matching_themes.append(f"{theme}(5+ power/toughness)")
                elif power >= 4 or toughness >= 4:
                    total_score += 1  # Smaller bonus for medium creatures
                    matching_themes.append(f"{theme}(4+ power/toughness)")
            except:
                pass

    return total_score, matching_themes
