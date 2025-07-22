TOTAL_CARDS = 13

# Define theme keywords and strategies for different deck archetypes
theme_keywords = { 
    'Aggro': ['haste', 'attack', 'damage', 'creature', 'power', 'quick', 'rush', 'fast'],
    'Control': ['counter', 'destroy', 'exile', 'draw', 'instant', 'sorcery', 'tap', 'return'],
    'Midrange': ['creature', 'value', 'versatile', 'balanced', 'enters', 'when', 'draw', 'search', '+1/+1', 'counter', 'sacrifice', 'dies', 'token', 'adapt', 'evolve', 'outlast', 'kicker', 'vigilance', 'trample', 'treasure', 'mana'],
    'Ramp': ['mana', 'land', 'search', 'big', 'expensive', 'cost', 'ritual', 'add', 'basic', 'battlefield', 'enters', 'when', 'sacrifice', 'dies', 'treasure', 'create', 'library', 'put', 'token', 'tap', 'channel'],
    'Tempo': ['bounce', 'counter', 'flying', 'cheap', 'efficient', 'flash', 'tap', 'return', 'untap', 'scry', 'cycling', 'ninjutsu', 'draw', 'when', 'enters', 'kicker'],
    'Graveyard': ['graveyard', 'discard', 'mill', 'milling', 'return', 'flashback', 'delve', 'unearth', 'threshold', 'delirium', 'undergrowth', 'escape', 'embalm', 'eternalize', 'reanimator', 'necromancy', 'from.*graveyard', 'to.*graveyard', 'exile.*graveyard', 'creature.*graveyard', 'zombie', 'horror', 'skeleton', 'spirit', 'dies', 'when.*enters', 'sacrifice'],
    'Sacrifice': ['sacrifice', 'dies', 'death', 'token', 'creature', 'enters'],
    'Tokens': ['token', 'create', 'populate', 'convoke', '1/1', 'creature'],
    'Equipment': ['equipment', 'attach', 'equipped', 'artifact', '+1/+1', 'power'],
    'Flying': ['flying', 'fly', 'air', 'evasion', 'bird', 'spirit'],
    'Burn': ['damage', 'burn', 'lightning', 'shock', 'fire', 'direct', 'any target', 'bolt', 'deals', 'each', 'enters', 'flashback', 'haste', 'instant', 'kicker', 'sacrifice', 'suspend', 'tap'],
    'Artifacts': ['artifact', 'colorless', 'construct', 'equipment', 'vehicle'],
    'Red Artifacts': ['artifact', 'energy', 'servo', 'golem', 'sacrifice an artifact', 'unearth', 'improvise', 'metalcraft', 'treasure', 'scrap', 'gremlin', 'artificer', 'construct'],
    'Big Creatures': ['power', 'toughness', '5', '6', '7', 'large', 'trample'],
    'Small Creatures': ['1', '2', '3', 'haste', 'prowess', 'menace', 'first strike', 'double strike', 'deathtouch', 'lifelink', 'vigilance', 'reach', 'flash', 'goblin', 'human', 'soldier', 'warrior', 'rogue', 'monk', 'scout', 'enters the battlefield', 'when', 'etb'],
    'Card Draw': ['draw', 'card', 'hand', 'library', 'cantrip', 'scry'],
    'Stompy': ['trample', 'power', 'force', 'creature', 'big', 'green'],
    'Beatdown': ['attack', 'damage', 'creature', 'aggressive', 'power']
}

# Color identity synergies
color_synergies = {
    'W': ['vigilance', 'lifelink', 'protection', 'prevent', 'equipment', 'soldier', 'knight'],
    'U': ['draw', 'counter', 'flying', 'scry', 'bounce', 'wizard', 'merfolk'],
    'B': ['destroy', 'discard', 'graveyard', 'sacrifice', 'zombie', 'vampire'],
    'R': ['damage', 'haste', 'sacrifice', 'goblin', 'warrior', 'burn'],
    'G': ['mana', 'ramp', 'trample', 'elf', 'beast', 'large']
}

# Comprehensive theme criteria for creature evaluation
# Note: 'keywords' field references theme_keywords to avoid duplication
theme_criteria = {
    'Graveyard': {
        'keywords': theme_keywords['Graveyard'],
        'abilities': ['enters', 'when', 'whenever', 'triggered abilities'],
        'stats_matter': False,  # Power/toughness is less important than abilities
        'utility_bonus': 2.0,   # High bonus for utility creatures
        'evasion_bonus': 0.5    # Small bonus for evasion
    },
    'Aggro': {
        'keywords': theme_keywords['Aggro'],
        'abilities': ['power', 'attack'],
        'stats_matter': True,   # Power matters a lot
        'utility_bonus': 0.5,   # Small bonus for utility
        'evasion_bonus': 1.5,   # High bonus for evasion
        'power_threshold': 2    # Want creatures with 2+ power
    },
    'Beatdown': {
        'keywords': theme_keywords['Beatdown'],
        'abilities': ['power', 'attack'],
        'stats_matter': True,   # Power matters a lot
        'utility_bonus': 0.5,   # Small bonus for utility
        'evasion_bonus': 1.5,   # High bonus for evasion
        'power_threshold': 2    # Want creatures with 2+ power
    },
    'Control': {
        'keywords': theme_keywords['Control'],
        'abilities': ['enters', 'when', 'draw', 'search', 'bounce', 'removal'],
        'stats_matter': False,  # Stats less important than utility
        'utility_bonus': 2.0,   # High value on utility
        'evasion_bonus': 1.0    # Moderate evasion value
    },
    'Flying': {
        'keywords': theme_keywords['Flying'],
        'abilities': ['air', 'wing'],
        'stats_matter': True,   # Both stats and flying matter
        'utility_bonus': 1.0,
        'evasion_bonus': 3.0,   # Flying is the main theme
        'required_ability': 'flying'  # Must have flying for high score
    },
    'Big Creatures': {
        'keywords': theme_keywords['Big Creatures'],
        'abilities': ['power', 'toughness'],
        'stats_matter': True,   # Power/toughness is primary
        'utility_bonus': 0.5,
        'evasion_bonus': 1.0,
        'power_threshold': 4,   # Want 4+ power creatures
        'size_bonus_multiplier': 0.2  # Bonus scales with size
    },
    'Stompy': {
        'keywords': theme_keywords['Stompy'],
        'abilities': ['power', 'toughness'],
        'stats_matter': True,   # Power/toughness is primary
        'utility_bonus': 0.5,
        'evasion_bonus': 1.0,
        'power_threshold': 4,   # Want 4+ power creatures
        'size_bonus_multiplier': 0.2  # Bonus scales with size
    },
    'Tokens': {
        'keywords': theme_keywords['Tokens'],
        'abilities': ['enters', 'when', 'dies', 'sacrifice'],
        'stats_matter': False,  # Utility over stats
        'utility_bonus': 2.0,
        'evasion_bonus': 1.0,
        'token_maker_bonus': 3.0  # High value for token generators
    },
    'Artifacts': {
        'keywords': theme_keywords['Artifacts'],
        'abilities': ['enters', 'when', 'sacrifice'],
        'stats_matter': False,
        'utility_bonus': 1.5,
        'evasion_bonus': 1.0,
        'artifact_bonus': 2.0  # Bonus for being an artifact creature
    },
    'Red Artifacts': {
        'keywords': theme_keywords['Red Artifacts'],
        'abilities': ['enters', 'when', 'sacrifice'],
        'stats_matter': False,
        'utility_bonus': 1.5,
        'evasion_bonus': 1.0,
        'artifact_bonus': 2.0  # Bonus for being an artifact creature
    },
    'Sacrifice': {
        'keywords': theme_keywords['Sacrifice'],
        'abilities': ['enters', 'when', 'create', 'dies'],
        'stats_matter': False,
        'utility_bonus': 2.0,
        'evasion_bonus': 0.5,
        'sacrifice_outlet_bonus': 2.5,  # High value for sac outlets
        'death_trigger_bonus': 2.0      # High value for death triggers
    },
    'Equipment': {
        'keywords': theme_keywords['Equipment'],
        'abilities': ['enters', 'when', 'attach', 'equipped', 'living weapon'],
        'stats_matter': True,   # Equipment wants creatures that can use the gear effectively
        'utility_bonus': 1.0,   # Moderate utility value
        'evasion_bonus': 1.5,   # Equipment often grants evasion
        'power_threshold': 1,   # Even small creatures can be good with equipment
        'equipment_synergy_bonus': 2.0  # High bonus for creatures that synergize with equipment
    },
    'Small Creatures': {
        'keywords': theme_keywords['Small Creatures'],
        'abilities': ['haste', 'menace', 'first strike', 'double strike', 'dash'],
        'stats_matter': True,   # Efficient stats matter for aggro
        'power_threshold': 1,   # Want creatures with 1+ power
        'max_power': 3,         # Cap for 'small' creatures
        'utility_bonus': 1.0,   # Moderate utility value
        'evasion_bonus': 2.0,   # High value on evasion for aggro
        'haste_bonus': 2.5,     # Haste is crucial for small aggro
        'efficient_stats_bonus': 1.5  # Bonus for power >= CMC
    }
}

# Also check for guild names and convert to strategies
guild_themes = {
    'azorius': ['Control', 'Flying'],
    'dimir': ['Control', 'Graveyard'],
    'rakdos': ['Aggro', 'Sacrifice'],
    'gruul': ['Aggro', 'Big Creatures'],
    'selesnya': ['Tokens', 'Midrange'],
    'orzhov': ['Control', 'Sacrifice'],
    'izzet': ['Control', 'Burn'],
    'golgari': ['Graveyard', 'Sacrifice'],
    'boros': ['Aggro', 'Equipment'],
    'simic': ['Ramp', 'Card Draw']
}