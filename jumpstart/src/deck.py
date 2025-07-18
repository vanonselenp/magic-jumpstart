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
    """Check if a card can be played in the given color identity based on mana requirements"""
    if not deck_colors:
        return True
    
    card_color = card.get('Color', '')
    card_category = card.get('Color Category', '')
    card_type = str(card.get('Type', '')).lower()
    oracle_text = str(card.get('Oracle Text', '')).lower()
    
    # Handle truly colorless cards (artifacts, lands, etc.) that don't require colored mana
    if card_category in ['Colorless', 'Artifacts', 'Lands']:
        return True
    
    # Handle cards with NaN color but have a color category (like Scrapwork Mutt)
    if pd.isna(card_color) and card_category:
        # Use color category to determine mana requirements
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
            # For multicolored cards, check if deck supports multiple colors
            if isinstance(deck_colors, str):
                return len(deck_colors) > 1  # Multi-character means multicolored
            elif isinstance(deck_colors, list):
                return len(deck_colors) > 1  # Multiple colors in list
            return False
        else:
            # Truly colorless cards (no color category or colorless category)
            return True
        
        # Check if the required color matches deck colors
        if isinstance(deck_colors, str):
            return effective_color in deck_colors
        elif isinstance(deck_colors, list):
            return effective_color in deck_colors
        return False
    
    # Handle normal colored cards - check if card colors fit deck colors
    if isinstance(card_color, str) and isinstance(deck_colors, str):
        card_color_set = set(card_color)
        deck_color_set = set(deck_colors)
        return card_color_set.issubset(deck_color_set)
    
    # Default case for any other situations
    return False

def display_card_details(specific_deck, cube_df, coherence_results, oracle_df):
    current_deck = cube_df[cube_df['Tags'] == specific_deck]
    for card in current_deck['Name']:
        expected_themes = coherence_results[specific_deck]['expected_themes']
        current_card = oracle_df[oracle_df['name'] == card].iloc[0]  # Get the first row for the card
        score, themes = calculate_card_theme_score(current_card, expected_themes)
        print(f"Card: {card}, Score: {score}, Themes: {themes}")

def calculate_card_theme_score(card, expected_themes):
    """Enhanced version of theme score calculation with theme-specific penalties"""
    if not expected_themes or expected_themes == ['Unknown']:
        return 0.0, []
    
    oracle_text = str(card.get('Oracle Text', '')).lower()
    card_type = str(card.get('Type', '')).lower()
    card_name = str(card.get('name', '')).lower() or str(card.get('Name', '')).lower()
    cmc = card.get('CMC', 0)
    
    try:
        cmc = float(cmc) if not pd.isna(cmc) else 0
    except:
        cmc = 0
    
    total_score = 0
    matching_themes = []
    
    for theme in expected_themes:
        if theme in theme_keywords:
            theme_words = theme_keywords[theme]
            # Count matches in oracle text, type, and name
            base_matches = sum(1 for word in theme_words if word in oracle_text or word in card_type or word in card_name)
            theme_score = base_matches
            
            # Apply theme-specific scoring adjustments
            if theme == "Ramp":
                # Ramp cards should prioritize mana acceleration and expensive payoffs
                if 'land' in oracle_text or 'mana' in oracle_text:
                    theme_score += 2  # High bonus for mana acceleration
                if cmc >= 6:  # Expensive cards are good ramp payoffs
                    theme_score += 2
                elif cmc >= 4:
                    theme_score += 1
                # Penalty for cheap creatures without ramp effects (more midrange-y)
                if 'creature' in card_type and cmc <= 3 and not any(word in oracle_text for word in ['mana', 'land', 'search']):
                    theme_score -= 1
                    
            elif theme == "Midrange":
                # Midrange should prioritize efficient creatures and versatile spells
                if 'creature' in card_type:
                    # Bonus for creatures in the 2-5 CMC sweet spot
                    if 2 <= cmc <= 5:
                        theme_score += 2
                    elif cmc == 1 or cmc == 6:
                        theme_score += 1
                    # Penalty for very expensive creatures (more ramp-y)
                    elif cmc >= 7:
                        theme_score -= 1
                # Bonus for versatile non-creature spells
                if 'instant' in card_type or 'sorcery' in card_type:
                    if 1 <= cmc <= 4:  # Efficient spells
                        theme_score += 1
                # Penalty for pure mana acceleration (more ramp-y)
                if any(word in oracle_text for word in ['add mana', 'search.*land', 'basic land']):
                    theme_score -= 1
            
            total_score += max(0, theme_score)  # Don't allow negative theme scores
            if theme_score > 0:
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
