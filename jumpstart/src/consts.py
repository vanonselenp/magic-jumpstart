# Jumpstart Cube Themes Configuration

# Mono-color themes (4 per color)
MONO_COLOR_THEMES = {
    # White themes
    'White Soldiers': {
        'colors': ['W'],
        'strategy': 'Aggressive tribal deck focused on soldier creatures with anthem effects',
        'keywords': ['soldier', 'tribal', 'anthem', 'pump', 'attack', 'vigilance', 'first strike'],
        'archetype': 'Aggro'
    },
    'White Equipment': {
        'colors': ['W'],
        'strategy': 'Equipment-based deck with efficient creatures and powerful gear',
        'keywords': ['equipment', 'attach', 'equipped', 'equip', 'metalcraft', 'artifact', 'power', 'toughness', 
                    'sword', 'blade', 'equipped creature', 'gets +', 'artifact creature', 'living weapon', 'armor'],
        'archetype': 'Midrange'
    },
    'White Angels': {
        'colors': ['W'],
        'strategy': 'Mid-to-late game deck with powerful flying angels and protection',
        'keywords': ['angel', 'flying', 'vigilance', 'lifelink', 'protection', 'expensive'],
        'archetype': 'Control'
    },
    'White Weenies': {
        'colors': ['W'],
        'strategy': 'Aggressive low-cost creatures with efficient stats and combat abilities',
        'keywords': ['creature', 'cheap', 'aggressive', 'power', 'attack', 'first strike', 'vigilance', 'efficient', 'low cost', 'small'],
        'archetype': 'Aggro'
    },
    
    # Blue themes
    'Blue Flying': {
        'colors': ['U'],
        'strategy': 'Evasive creatures with flying and tempo spells',
        'keywords': ['flying', 'bird', 'drake', 'spirit', 'bounce', 'counter', 'draw'],
        'archetype': 'Tempo'
    },
    'Blue Wizards': {
        'colors': ['U'],
        'strategy': 'Wizard tribal with spell-based synergies and card advantage',
        'keywords': ['wizard', 'instant', 'sorcery', 'prowess', 'draw', 'counter', 'tribal'],
        'archetype': 'Control'
    },
    'Blue Card Draw': {
        'colors': ['U'],
        'strategy': 'Card advantage engine with draw spells and library manipulation',
        'keywords': ['draw', 'card', 'scry', 'look', 'library', 'hand', 'cycling'],
        'archetype': 'Control'
    },
    'Blue Merfolk': {
        'colors': ['U'],
        'strategy': 'Aggressive merfolk tribal with evasion and tribal synergies',
        'keywords': ['merfolk', 'tribal', 'islandwalk', 'counter', 'tap', 'untap'],
        'archetype': 'Aggro'
    },
    
    # Black themes
    'Black Zombies': {
        'colors': ['B'],
        'strategy': 'Zombie tribal with graveyard recursion and sacrifice synergies',
        'keywords': ['zombie', 'tribal', 'graveyard', 'return', 'sacrifice', 'dies'],
        'archetype': 'Midrange'
    },
    'Black Graveyard': {
        'colors': ['B'],
        'strategy': 'Graveyard-based value engine with recursion and reanimation',
        'keywords': ['graveyard', 'return', 'mill', 'flashback', 'unearth', 'threshold'],
        'archetype': 'Control'
    },
    'Black Sacrifice': {
        'colors': ['B'],
        'strategy': 'Sacrifice-based deck with death triggers and value generation',
        'keywords': ['sacrifice', 'dies', 'death', 'aristocrats', 'token', 'whenever'],
        'archetype': 'Midrange'
    },
    'Black Vampires': {
        'colors': ['B'],
        'strategy': 'Aggressive vampire tribal with lifedrain and +1/+1 counters',
        'keywords': ['vampire', 'tribal', 'lifelink', 'counter', 'drain', 'aggressive'],
        'archetype': 'Aggro'
    },
    
    # Red themes
    'Red Goblins': {
        'colors': ['R'],
        'strategy': 'Fast goblin tribal with haste and explosive plays',
        'keywords': ['goblin', 'tribal', 'haste', 'sacrifice', 'token', 'aggressive'],
        'archetype': 'Aggro'
    },
    'Red Burn': {
        'colors': ['R'],
        'strategy': 'Direct damage spells and hasty creatures for quick wins',
        'keywords': ['damage', 'burn', 'lightning', 'shock', 'direct', 'haste', 'instant'],
        'archetype': 'Aggro'
    },
    'Red Dragons': {
        'colors': ['R'],
        'strategy': 'Expensive dragons with powerful effects and flying',
        'keywords': ['dragon', 'flying', 'expensive', 'power', 'trample', 'haste'],
        'archetype': 'Ramp'
    },
    'Red Artifacts': {
        'colors': ['R'],
        'strategy': 'Artifact-based deck with improvise and metalcraft synergies',
        'keywords': ['artifact', 'improvise', 'metalcraft', 'construct', 'servo', 'energy', 
                    'equipment', 'enters', 'tap', 'sacrifice', 'colorless', 'cost', 'thopter'],
        'archetype': 'Artifacts'
    },
    
    # Green themes
    'Green Elves': {
        'colors': ['G'],
        'strategy': 'Elf tribal with mana acceleration and creature synergies',
        'keywords': ['elf', 'tribal', 'mana', 'tap', 'forest', 'counter', 'token', 'druid', 
                    'shaman', 'ranger', 'creature', 'add', 'produces', 'enters', 'lord', 
                    'gets +', 'elves you control', 'elf creature'],
        'archetype': 'Tribal'
    },
    'Green Ramp': {
        'colors': ['G'],
        'strategy': 'Mana acceleration into large threats and expensive spells',
        'keywords': ['mana', 'land', 'search', 'expensive', 'big', 'ritual', 'forest'],
        'archetype': 'Ramp'
    },
    'Green Stompy': {
        'colors': ['G'],
        'strategy': 'Large creatures with trample and pump effects',
        'keywords': ['trample', 'power', 'toughness', 'pump', 'overrun', 'fight', 'big', 'large', 
                    'creature', 'beast', 'giant', 'wurm', 'elemental', '4/4', '5/5', '6/6', 
                    'expensive', 'high power', 'stats'],
        'archetype': 'Stompy'  # Custom archetype instead of generic Aggro
    },
    'Green Beasts': {
        'colors': ['G'],
        'strategy': 'Large beast creatures with powerful abilities',
        'keywords': ['beast', 'tribal', 'power', 'toughness', 'enters', 'expensive', 'bear', 
                    'wolf', 'elephant', 'rhino', 'boar', 'ape', 'creature', 'large', 'big', 
                    'trample', 'fight', 'lord', 'gets +', 'beasts you control'],
        'archetype': 'Tribal'
    }
}

# Dual-color themes (2-color combinations)
DUAL_COLOR_THEMES = {
    # White-Blue (Azorius)
    'Azorius Control': {
        'colors': ['W', 'U'],
        'strategy': 'Classic control deck with counterspells, removal, and card draw',
        'keywords': ['counter', 'destroy', 'exile', 'draw', 'instant', 'sorcery', 'board wipe'],
        'archetype': 'Control'
    },
    
    # Blue-Black (Dimir)
    'Dimir Mill': {
        'colors': ['U', 'B'],
        'strategy': 'Mill-based strategy with graveyard interaction and card advantage',
        'keywords': ['mill', 'graveyard', 'library', 'flashback', 'threshold', 'draw'],
        'archetype': 'Control'
    },
    
    # Black-Red (Rakdos)
    'Rakdos Aggro': {
        'colors': ['B', 'R'],
        'strategy': 'Aggressive deck with efficient creatures and direct damage',
        'keywords': ['haste', 'damage', 'aggressive', 'sacrifice', 'burn', 'power'],
        'archetype': 'Aggro'
    },
    
    # Red-Green (Gruul)
    'Gruul Big Creatures': {
        'colors': ['R', 'G'],
        'strategy': 'Large creatures with haste and trample effects',
        'keywords': ['power', 'toughness', 'haste', 'trample', 'big', 'expensive', 'ramp'],
        'archetype': 'Midrange'
    },
    
    # Green-White (Selesnya)
    'Selesnya Tokens': {
        'colors': ['G', 'W'],
        'strategy': 'Token generation with anthem effects and populate mechanics',
        'keywords': ['token', 'create', 'populate', 'convoke', 'anthem', 'pump'],
        'archetype': 'Midrange'
    },
    
    # White-Black (Orzhov)
    'Orzhov Lifedrain': {
        'colors': ['W', 'B'],
        'strategy': 'Life manipulation with drain effects and powerful creatures',
        'keywords': ['lifegain', 'drain', 'life', 'extort', 'lifelink', 'aristocrats'],
        'archetype': 'Midrange'
    },
    
    # Blue-Red (Izzet)
    'Izzet Spells Matter': {
        'colors': ['U', 'R'],
        'strategy': 'Instant and sorcery synergies with prowess and spell-based creatures',
        'keywords': ['instant', 'sorcery', 'prowess', 'spells', 'trigger', 'burn'],
        'archetype': 'Tempo'
    },
    
    # Black-Green (Golgari)
    'Golgari Graveyard Value': {
        'colors': ['B', 'G'],
        'strategy': 'Graveyard-based value engine with recursion and sacrifice',
        'keywords': ['graveyard', 'sacrifice', 'return', 'dredge', 'undergrowth', 'dies'],
        'archetype': 'Midrange'
    },
    
    # Red-White (Boros)
    'Boros Equipment Aggro': {
        'colors': ['R', 'W'],
        'strategy': 'Aggressive creatures with equipment support and combat tricks',
        'keywords': ['equipment', 'haste', 'first strike', 'attack', 'combat', 'pump', 'equip', 'equipped',
                    'sword', 'blade', 'artifact', 'gets +', 'equipped creature', 'attach', 'living weapon'],
        'archetype': 'Aggro'
    },
    
    # Green-Blue (Simic)
    'Simic Ramp Control': {
        'colors': ['G', 'U'],
        'strategy': 'Ramp into large threats with card draw and protection',
        'keywords': ['ramp', 'mana', 'draw', 'expensive', 'evolve', 'counter', 'adapt'],
        'archetype': 'Ramp'
    }
}

# All themes combined for easy access
ALL_THEMES = {**MONO_COLOR_THEMES, **DUAL_COLOR_THEMES}

# Theme categories for organization
THEME_CATEGORIES = {
    'Aggressive': ['White Soldiers', 'Blue Merfolk', 'Black Vampires', 'Red Goblins', 'Red Burn', 'Green Stompy', 'White Weenies', 'Rakdos Aggro', 'Boros Equipment Aggro'],
    'Midrange': ['White Equipment', 'Black Zombies', 'Black Sacrifice', 'Red Artifacts', 'Green Beasts', 'Gruul Big Creatures', 'Selesnya Tokens', 'Orzhov Lifedrain', 'Golgari Graveyard Value'],
    'Control': ['White Angels', 'Blue Wizards', 'Blue Card Draw', 'Black Graveyard', 'Azorius Control', 'Dimir Mill'],
    'Ramp': ['Red Dragons', 'Green Elves', 'Green Ramp', 'Simic Ramp Control'],
    'Tempo': ['Blue Flying', 'Izzet Spells Matter']
}

# Color identity mapping for validation
COLOR_IDENTITY_MAP = {
    'W': 'White',
    'U': 'Blue', 
    'B': 'Black',
    'R': 'Red',
    'G': 'Green'
}
