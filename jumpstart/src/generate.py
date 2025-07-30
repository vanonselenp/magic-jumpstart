# Image Generation Prompt Creator for Magic: The Gathering Themes
import textwrap

def generate_image_prompt(theme_name):
    """
    Generate a ChatGPT prompt for creating a Magic: The Gathering theme image.
    
    Args:
        theme_name (str): Name of the theme (e.g., "Selesnya Value", "Rakdos Aggro")
                         Must exist in MONO_COLOR_THEMES or DUAL_COLOR_THEMES
    
    Returns:
        str: Formatted prompt for image generation
    
    Raises:
        ValueError: If theme_name is not found in the theme dictionaries
    """
    
    # Import theme data
    try:
        from .consts import MONO_COLOR_THEMES, DUAL_COLOR_THEMES
    except ImportError:
        try:
            from consts import MONO_COLOR_THEMES, DUAL_COLOR_THEMES
        except ImportError:
            raise ImportError("Could not import theme constants from consts.py")
    
    # Look up theme in dictionaries
    theme_info = None
    if theme_name in MONO_COLOR_THEMES:
        theme_info = MONO_COLOR_THEMES[theme_name]
    elif theme_name in DUAL_COLOR_THEMES:
        theme_info = DUAL_COLOR_THEMES[theme_name]
    else:
        available_themes = list(MONO_COLOR_THEMES.keys()) + list(DUAL_COLOR_THEMES.keys())
        raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available_themes}")
    
    # Extract theme properties
    colors = theme_info['colors']
    strategy = theme_info['strategy']
    keywords = theme_info['keywords']
    archetype = theme_info['archetype']
    
    # Color mapping for visual descriptions
    color_descriptions = {
        'W': {
            'name': 'White',
            'elements': ['holy light', 'marble temples', 'angelic wings', 'pristine armor', 'golden halos'],
            'atmosphere': 'radiant, pure, orderly',
            'palette': 'bright whites, warm golds, soft yellows'
        },
        'U': {
            'name': 'Blue', 
            'elements': ['swirling waters', 'floating islands', 'arcane symbols', 'crystal formations', 'mystical energy'],
            'atmosphere': 'mysterious, intellectual, flowing',
            'palette': 'deep blues, silver, cyan, ethereal purples'
        },
        'B': {
            'name': 'Black',
            'elements': ['shadowy figures', 'bone structures', 'dark rituals', 'withering decay', 'ominous mist'],
            'atmosphere': 'dark, foreboding, powerful',
            'palette': 'deep blacks, blood reds, sickly greens, bone whites'
        },
        'R': {
            'name': 'Red',
            'elements': ['roaring flames', 'jagged mountains', 'lightning strikes', 'molten lava', 'fierce dragons'],
            'atmosphere': 'chaotic, explosive, passionate',
            'palette': 'bright reds, orange flames, volcanic blacks, electric yellows'
        },
        'G': {
            'name': 'Green',
            'elements': ['ancient forests', 'massive trees', 'verdant growth', 'wild beasts', 'natural magic'],
            'atmosphere': 'organic, primal, abundant',
            'palette': 'rich greens, earth browns, nature golds, forest shadows'
        }
    }
    
    # Archetype-based visual themes
    archetype_themes = {
        'Aggro': {
            'mood': 'dynamic action, speed, aggression',
            'composition': 'diagonal lines, motion blur, charging forward',
            'lighting': 'dramatic, high contrast, intense'
        },
        'Midrange': {
            'mood': 'balanced power, strategic positioning, versatility',
            'composition': 'stable triangular forms, layered depth, organized chaos',
            'lighting': 'balanced, natural, clear visibility'
        },
        'Control': {
            'mood': 'patient power, defensive strength, calculated dominance',
            'composition': 'symmetrical, fortress-like, imposing structures',
            'lighting': 'cool, controlled, strategic shadows'
        },
        'Ramp': {
            'mood': 'building power, escalating threat, monumental scale',
            'composition': 'vertical emphasis, towering elements, progression',
            'lighting': 'growing intensity, building to climax'
        },
        'Tempo': {
            'mood': 'swift precision, tactical advantage, fluid motion',
            'composition': 'flowing curves, spirals, interconnected elements',
            'lighting': 'quick flashes, stroboscopic, rhythmic'
        },
        'Tribal': {
            'mood': 'unity, shared purpose, collective strength',
            'composition': 'grouped elements, patterns, repetitive motifs',
            'lighting': 'communal warmth, shared illumination'
        },
        'Artifacts': {
            'mood': 'mechanical precision, technological power, constructed reality',
            'composition': 'geometric shapes, interlocking gears, precise angles',
            'lighting': 'metallic gleams, electric blue, industrial'
        },
        'Stompy': {
            'mood': 'overwhelming force, raw power, crushing dominance',
            'composition': 'massive scale, ground-shaking impact, towering presence',
            'lighting': 'earth-shaking shadows, primal intensity'
        }
    }
    
    # Build color palette and elements
    color_names = [color_descriptions[c]['name'] for c in colors]
    color_elements = []
    color_atmospheres = []
    color_palettes = []
    
    for color in colors:
        color_elements.extend(color_descriptions[color]['elements'][:2])  # Take top 2 elements
        color_atmospheres.append(color_descriptions[color]['atmosphere'])
        color_palettes.append(color_descriptions[color]['palette'])
    
    # Get archetype information
    archetype_info = archetype_themes.get(archetype, archetype_themes['Midrange'])
    
    # Extract key thematic elements from keywords
    creature_types = [kw for kw in keywords if kw in ['soldier', 'zombie', 'goblin', 'elf', 'dragon', 'angel', 'wizard', 'beast']]
    abilities = [kw for kw in keywords if kw in ['flying', 'haste', 'trample', 'lifelink', 'vigilance', 'first strike']]
    spell_types = [kw for kw in keywords if kw in ['instant', 'sorcery', 'enchantment', 'artifact', 'equipment']]
    
    # Construct the prompt
    prompt = f"""Create a fantasy art image for a Magic: The Gathering theme called "{theme_name}". 

**Image Specifications:**
- Dimensions: 100mm × 78mm aspect ratio (landscape orientation)
- High resolution, suitable for card art or promotional material
- Fantasy art style reminiscent of Magic: The Gathering illustrations

**Theme Details:**
- Colors: {' and '.join(color_names)} magic
- Strategy: {strategy}
- Archetype: {archetype}

**Visual Elements to Include:**
- Color Palette: {', '.join(color_palettes)}
- Atmospheric Elements: {', '.join(color_elements)}
- Mood: {archetype_info['mood']}
- Composition: {archetype_info['composition']}
- Lighting: {archetype_info['lighting']}"""

    # Add creature-specific elements
    if creature_types:
        prompt += f"\n- Creature Focus: Feature {', '.join(creature_types)} prominently in the scene"
    
    # Add ability-based visual cues
    if abilities:
        ability_visuals = {
            'flying': 'aerial perspective with creatures soaring',
            'haste': 'motion lines and speed effects',
            'trample': 'ground-shaking impact and debris',
            'lifelink': 'healing light and vital energy flows',
            'vigilance': 'alert postures and watchful eyes',
            'first strike': 'weapons gleaming with readiness'
        }
        relevant_visuals = [ability_visuals.get(ability, ability) for ability in abilities]
        prompt += f"\n- Combat Abilities: Show {', '.join(relevant_visuals)}"
    
    # Add spell-type elements
    if spell_types:
        spell_visuals = {
            'instant': 'magical energy crackling in the air',
            'sorcery': 'complex magical rituals and spell circles',
            'enchantment': 'persistent magical auras and glowing effects',
            'artifact': 'mechanical/constructed elements integrated',
            'equipment': 'prominent weapons and armor pieces'
        }
        relevant_spell_visuals = [spell_visuals.get(spell, spell) for spell in spell_types]
        prompt += f"\n- Magical Elements: Include {', '.join(relevant_spell_visuals)}"

    prompt += f"""

**Style Guidelines:**
- Atmospheric perspective: {', '.join(color_atmospheres)}
- Detailed fantasy illustration with rich textures
- Dynamic composition that conveys the theme's strategic identity
- Professional Magic: The Gathering card art quality
- Avoid text or symbols, focus on pure visual storytelling

**Additional Context:**
The image should immediately convey the essence of a {archetype.lower()} strategy in Magic: The Gathering, representing the {' and '.join(color_names)} color combination through both literal color palette and thematic elements that players would associate with this playstyle."""

    return prompt


def generate_theme_image_prompts(theme_names=None):
    """
    Generate image prompts for multiple themes.
    
    Args:
        theme_names (list, optional): List of theme names to generate prompts for.
                                    If None, generates for all available themes.
        
    Returns:
        dict: Dictionary mapping theme names to their image generation prompts
    """
    # Import theme data
    try:
        from .consts import MONO_COLOR_THEMES, DUAL_COLOR_THEMES
    except ImportError:
        try:
            from consts import MONO_COLOR_THEMES, DUAL_COLOR_THEMES
        except ImportError:
            raise ImportError("Could not import theme constants from consts.py")
    
    # If no specific themes requested, use all themes
    if theme_names is None:
        theme_names = list(MONO_COLOR_THEMES.keys()) + list(DUAL_COLOR_THEMES.keys())
    
    prompts = {}
    
    for theme_name in theme_names:
        try:
            prompts[theme_name] = generate_image_prompt(theme_name)
        except ValueError as e:
            print(f"Warning: Skipping theme '{theme_name}': {e}")
    
    return prompts


def save_prompts_to_file(prompts_dict, filename="theme_image_prompts.txt"):
    """
    Save generated prompts to a text file for easy use with ChatGPT/DALL-E.
    
    Args:
        prompts_dict (dict): Dictionary of theme names to prompts
        filename (str): Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for theme_name, prompt in prompts_dict.items():
            f.write(f"{'='*60}\n")
            f.write(f"THEME: {theme_name}\n")
            f.write(f"{'='*60}\n\n")
            f.write(prompt)
            f.write("\n\n" + "-"*80 + "\n\n")
    
    print(f"Prompts saved to {filename}")


def generate_deck_divider(theme_name, deck_dataframe):
    """
    Generate a printable divider card for physical deck storage.
    
    Args:
        theme_name (str): Name of the theme
        deck_dataframe (pd.DataFrame): DataFrame containing the deck's cards
        
    Returns:
        str: Formatted divider card text ready for printing
    """
    # Import theme data
    try:
        from .consts import MONO_COLOR_THEMES, DUAL_COLOR_THEMES
    except ImportError:
        try:
            from consts import MONO_COLOR_THEMES, DUAL_COLOR_THEMES
        except ImportError:
            raise ImportError("Could not import theme constants from consts.py")
    
    # Look up theme info
    theme_info = None
    if theme_name in MONO_COLOR_THEMES:
        theme_info = MONO_COLOR_THEMES[theme_name]
    elif theme_name in DUAL_COLOR_THEMES:
        theme_info = DUAL_COLOR_THEMES[theme_name]
    else:
        # Fallback if theme not found
        theme_info = {
            'strategy': 'Strategy not found in theme definitions',
            'colors': ['?'],
            'archetype': 'Unknown'
        }

    # Helper to wrap text to 50 chars
    def wrap_text(text, width=50):
        return '\n'.join(textwrap.wrap(text, width=width))

    # Get card list in alphabetical order
    card_names = []
    for idx, card in deck_dataframe.iterrows():
        card_name = card.get('name', 'Unknown Card')
        card_names.append(card_name)

    card_names.sort()  # Alphabetical order

    # Format the divider card
    divider = f"""{'='*50}
{theme_name.upper().center(50)}
{'='*50}

STRATEGY:
{wrap_text(theme_info['strategy'])}

COLORS: {' + '.join(theme_info['colors'])}
ARCHETYPE: {theme_info['archetype']}
CARDS: {len(card_names)}

{'─'*50}
DECK LIST (Alphabetical):
{'─'*50}"""

    # Add cards in two columns for better space usage
    for i in range(0, len(card_names), 2):
        left_card = card_names[i]
        right_card = card_names[i + 1] if i + 1 < len(card_names) else ""
        # Format with proper spacing (25 chars per column)
        divider += f"\n{left_card:<25} {right_card}"

    divider += f"\n\n{'='*50}"

    return divider


def generate_all_deck_dividers(deck_dataframes, filename="deck_dividers.txt"):
    """
    Generate printable dividers for all decks in the collection.
    
    Args:
        deck_dataframes (dict): Dictionary mapping theme names to DataFrames
        filename (str): Output filename for the dividers
        
    Returns:
        dict: Dictionary mapping theme names to their divider text
    """
    dividers = {}
    
    # Generate divider for each deck
    for theme_name, deck_df in deck_dataframes.items():
        try:
            dividers[theme_name] = generate_deck_divider(theme_name, deck_df)
        except Exception as e:
            print(f"Warning: Could not generate divider for {theme_name}: {e}")
            # Create a basic divider as fallback
            card_names = sorted([card.get('name', 'Unknown') for _, card in deck_df.iterrows()])
            basic_divider = f"""{'='*50}
{theme_name.upper().center(50)}
{'='*50}

CARDS: {len(card_names)}

{'─'*50}
DECK LIST (Alphabetical):
{'─'*50}"""
            for i in range(0, len(card_names), 2):
                left_card = card_names[i]
                right_card = card_names[i + 1] if i + 1 < len(card_names) else ""
                basic_divider += f"\n{left_card:<25} {right_card}"
            basic_divider += f"\n\n{'='*50}"
            dividers[theme_name] = basic_divider
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        # Sort themes alphabetically for consistent ordering
        sorted_themes = sorted(dividers.keys())
        
        for i, theme_name in enumerate(sorted_themes):
            f.write(dividers[theme_name])
            
            # Add page break between dividers (except for last one)
            if i < len(sorted_themes) - 1:
                f.write("\n\n" + "┄" * 50 + " PAGE BREAK " + "┄" * 50 + "\n\n")
    
    print(f"Deck dividers saved to {filename}")
    print(f"Generated {len(dividers)} divider cards")
    
    return dividers


def print_single_divider(theme_name, deck_dataframe):
    """
    Print a single divider to console for immediate viewing.
    
    Args:
        theme_name (str): Name of the theme
        deck_dataframe (pd.DataFrame): DataFrame containing the deck's cards
    """
    divider = generate_deck_divider(theme_name, deck_dataframe)
    print(divider)


# Example usage function
def generate_all_theme_prompts():
    """
    Generate prompts for all themes defined in consts.py
    """
    try:
        prompts = generate_theme_image_prompts()
        save_prompts_to_file(prompts)
        return prompts
    except ImportError as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # Example usage for image prompts
    try:
        example_prompt = generate_image_prompt("Selesnya Value")
        
        print("Example Prompt for Selesnya Value:")
        print("=" * 50)
        print(example_prompt)
    except (ValueError, ImportError) as e:
        print(f"Error generating example prompt: {e}")
        
        # Fallback example showing the expected interface
        print("\nExpected usage:")
        print("generate_image_prompt('Selesnya Value')")
        print("generate_image_prompt('Rakdos Aggro')")
        print("generate_image_prompt('White Soldiers')")
        print("\nAvailable themes should be defined in consts.py")
    
    print("\n" + "="*60)
    print("DIVIDER CARD FUNCTIONALITY")
    print("="*60)
    print("\nTo generate deck dividers:")
    print("generate_all_deck_dividers(deck_dataframes)")
    print("print_single_divider('Selesnya Value', deck_dataframe)")
    print("\nDividers include:")
    print("- Theme name as header")
    print("- Strategy description")
    print("- Color/archetype info")
    print("- Alphabetical card list in two columns")
    print("- Formatted for easy printing and physical storage")
