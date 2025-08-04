# Jumpstart Cube Themes Configuration

from typing import Set, List, Dict

# Import enums from separate module
from .enums import Archetype, MagicColor

# Import scorer factory functions
from .scorer import (
    create_default_scorer, create_tribal_scorer, create_equipment_scorer,
    create_aggressive_scorer, create_stompy_scorer, create_artifact_scorer,
    create_control_scorer
)

# Mono-color themes (4 per color)
MONO_COLOR_THEMES = {
    # White themes
    'White Soldiers': {
        'colors': [MagicColor.WHITE.value],
        'strategy': 'Aggressive tribal deck focused on soldier creatures with anthem effects',
        'keywords': ['soldier', 'tribal', 'anthem', 'pump', 'attack', 'vigilance', 'first strike'],
        'archetype': Archetype.AGGRO,
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'White Equipment': {
        'colors': [MagicColor.WHITE.value],
        'strategy': 'Equipment-based deck with efficient creatures and powerful gear',
        'keywords': ['equipment', 'attach', 'equipped', 'equip', 'metalcraft', 'artifact', 'power', 'toughness', 
                    'sword', 'blade', 'equipped creature', 'gets +', 'artifact creature', 'living weapon', 'armor'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_equipment_scorer,
        'core_card_count': 5
    },
    'White Angels': {
        'colors': [MagicColor.WHITE.value],
        'strategy': 'Mid-to-late game deck with powerful flying angels and protection',
        'keywords': ['angel', 'flying', 'vigilance', 'lifelink', 'protection', 'expensive'],
        'archetype': Archetype.CONTROL,
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    'White Vanguard': {
        'colors': [MagicColor.WHITE.value],
        'strategy': 'Aggressive low-cost creatures with efficient stats and combat abilities',
        'keywords': ['creature', 'cheap', 'aggressive', 'power', 'attack', 'first strike', 'vigilance', 'efficient', 'low cost', 'small'],
        'archetype': Archetype.AGGRO,
        'scorer': create_aggressive_scorer,
        'core_card_count': 3
    },
    
    # Blue themes
    'Blue Flying': {
        'colors': [MagicColor.BLUE.value],
        'strategy': 'Evasive creatures with flying and tempo spells',
        'keywords': ['flying', 'bird', 'drake', 'spirit', 'bounce', 'counter', 'draw'],
        'archetype': Archetype.TEMPO,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    'Blue Wizards': {
        'colors': [MagicColor.BLUE.value],
        'strategy': 'Wizard tribal with spell-based synergies and card advantage',
        'keywords': ['wizard', 'instant', 'sorcery', 'prowess', 'draw', 'counter', 'tribal'],
        'archetype': Archetype.CONTROL,
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Blue Card Draw': {
        'colors': [MagicColor.BLUE.value],
        'strategy': 'Card advantage engine with draw spells and library manipulation',
        'keywords': ['draw', 'card', 'scry', 'look', 'library', 'hand', 'cycling'],
        'archetype': Archetype.CONTROL,
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    'Blue Tempo': {
        'colors': [MagicColor.BLUE.value],
        'strategy': 'Efficient creatures with evasion and tempo spells for board control',
        'keywords': ['bounce', 'return', 'counter', 'flying', 'flash', 'prowess', 'tempo', 'efficient', 'evasion'],
        'archetype': Archetype.TEMPO,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Black themes
    'Black Zombies': {
        'colors': [MagicColor.BLACK.value],
        'strategy': 'Zombie tribal with graveyard recursion and sacrifice synergies',
        'keywords': ['zombie', 'tribal', 'graveyard', 'return', 'sacrifice', 'dies'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Black Graveyard': {
        'colors': [MagicColor.BLACK.value],
        'strategy': 'Graveyard-based value engine with recursion and reanimation',
        'keywords': ['graveyard', 'return', 'mill', 'flashback', 'unearth', 'threshold'],
        'archetype': Archetype.CONTROL,
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    'Black Sacrifice': {
        'colors': [MagicColor.BLACK.value],
        'strategy': 'Sacrifice-based deck with death triggers and value generation',
        'keywords': ['sacrifice', 'dies', 'death', 'aristocrats', 'token', 'whenever'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    'Black Control': {
        'colors': [MagicColor.BLACK.value],
        'strategy': 'Control deck with removal spells and efficient creatures for board control',
        'keywords': ['destroy', 'remove', 'target', 'exile', 'control', 'doom blade', 'murder', 'kill', 'discard', 'draw'],
        'archetype': Archetype.CONTROL,
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    
    # Red themes
    'Red Goblins': {
        'colors': [MagicColor.RED.value],
        'strategy': 'Fast goblin tribal with haste and explosive plays',
        'keywords': ['goblin', 'tribal', 'haste', 'sacrifice', 'token', 'aggressive'],
        'archetype': Archetype.AGGRO,
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Red Burn': {
        'colors': [MagicColor.RED.value],
        'strategy': 'Direct damage spells and hasty creatures for quick wins',
        'keywords': ['damage', 'burn', 'lightning', 'shock', 'direct', 'haste', 'instant'],
        'archetype': Archetype.AGGRO,
        'scorer': create_aggressive_scorer,
        'core_card_count': 4
    },
    'Red Inferno': {
        'colors': [MagicColor.RED.value],
        'strategy': 'Expensive dragons with powerful effects and flying',
        'keywords': ['dragon', 'flying', 'expensive', 'power', 'trample', 'haste'],
        'archetype': Archetype.RAMP,
        'scorer': create_tribal_scorer,
        'core_card_count': 3
    },
    'Red Artifacts': {
        'colors': [MagicColor.RED.value],
        'strategy': 'Artifact-based deck with improvise and metalcraft synergies',
        'keywords': ['artifact', 'improvise', 'metalcraft', 'construct', 'servo', 'energy', 
                    'equipment', 'enters', 'tap', 'sacrifice', 'colorless', 'cost', 'thopter'],
        'archetype': Archetype.ARTIFACTS,
        'scorer': create_artifact_scorer,
        'core_card_count': 4
    },
    
    # Green themes
    'Green Elves': {
        'colors': [MagicColor.GREEN.value],
        'strategy': 'Elf tribal with mana acceleration and creature synergies',
        'keywords': ['elf', 'tribal', 'mana', 'tap', 'forest', 'counter', 'token', 'druid', 
                    'shaman', 'ranger', 'creature', 'add', 'produces', 'enters', 'lord', 
                    'gets +', 'elves you control', 'elf creature'],
        'archetype': Archetype.TRIBAL,
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Green Ramp': {
        'colors': [MagicColor.GREEN.value],
        'strategy': 'Mana acceleration into large threats and expensive spells',
        'keywords': ['mana', 'land', 'search', 'expensive', 'big', 'ritual', 'forest'],
        'archetype': Archetype.RAMP,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    'Green Stompy': {
        'colors': [MagicColor.GREEN.value],
        'strategy': 'Large creatures with trample and pump effects',
        'keywords': ['trample', 'power', 'toughness', 'pump', 'overrun', 'fight', 'big', 'large', 
                    'creature', 'beast', 'giant', 'wurm', 'elemental', '4/4', '5/5', '6/6', 
                    'expensive', 'high power', 'stats'],
        'archetype': Archetype.STOMPY,  # Custom archetype instead of generic Aggro
        'scorer': create_aggressive_scorer,
        'core_card_count': 3
    },
    'Green Beasts': {
        'colors': [MagicColor.GREEN.value],
        'strategy': 'Large beast creatures with powerful abilities',
        'keywords': ['beast', 'tribal', 'power', 'toughness', 'enters', 'expensive', 'bear', 
                    'wolf', 'elephant', 'rhino', 'boar', 'ape', 'creature', 'large', 'big', 
                    'trample', 'fight', 'lord', 'gets +', 'beasts you control'],
        'archetype': Archetype.TRIBAL,
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    }
}

# Dual-color themes (2-color combinations)
DUAL_COLOR_THEMES = {
    # White-Blue (Azorius)
    'Azorius Control': {
        'colors': [MagicColor.WHITE.value, MagicColor.BLUE.value],
        'strategy': 'Control deck with counterspells, removal, card draw, and efficient win conditions',
        'keywords': [
            # Core control spells
            'counter target', 'negate', 'cancel', 'dispel', 'counter target spell',
            'destroy target', 'exile target', 'oblivion ring', 'path to exile',
            'return target', 'bounce', 'unsummon',
            # Card advantage
            'draw a card', 'draw two', 'scry', 'divination',
            # Board control
            'tap target', 'detain', 'prevent damage', 'wrath', 'board wipe',
            # Azorius identity
            'white and blue', 'azorius', 'flying', 'vigilance', 'lifelink',
            # Control timing
            'flash', 'instant speed', 'end of turn', 'during upkeep'
        ],
        'archetype': Archetype.CONTROL,
        'color_priority': 'strict',  # Prioritize true WU cards
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    
    # Blue-Black (Dimir)
    'Dimir Mill': {
        'colors': [MagicColor.BLUE.value, MagicColor.BLACK.value],
        'strategy': 'Mill-based strategy with graveyard interaction and card advantage',
        'keywords': ['mill', 'graveyard', 'library', 'flashback', 'threshold', 'draw'],
        'archetype': Archetype.CONTROL,
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    
    # Black-Red (Rakdos)
    'Rakdos Aggro': {
        'colors': [MagicColor.BLACK.value, MagicColor.RED.value],
        'strategy': 'Aggressive deck with efficient creatures and direct damage',
        'keywords': ['haste', 'damage', 'aggressive', 'sacrifice', 'burn', 'power'],
        'archetype': Archetype.AGGRO,
        'scorer': create_aggressive_scorer,
        'core_card_count': 3
    },
    
    # Red-Green (Gruul)
    'Gruul Midrange': {
        'colors': [MagicColor.RED.value, MagicColor.GREEN.value],
        'strategy': 'Efficient midrange creatures with aggressive abilities and versatile spells',
        'keywords': ['haste', 'trample', 'efficient', 'versatile', 'combat', 'removal', 
                    'creature', 'aggressive', 'power', 'damage', 'burn', 'fight', 
                    'enters', 'whenever', 'attack', 'deal damage', 'direct'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Green-White (Selesnya)
    'Selesnya Value': {
        'colors': [MagicColor.GREEN.value, MagicColor.WHITE.value],
        'strategy': 'Incremental advantage through efficient creatures, removal, and versatile utility spells',
        'keywords': ['efficient', 'creature', 'removal', 'destroy', 'exile', 'enchantment', 
                    'versatile', 'value', 'enters', 'lifegain', 'vigilance', 'flying', 
                    'combat tricks', 'instant', 'sorcery', 'token', 'utility', 'aura'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # White-Black (Orzhov)
    'Orzhov Lifegain Value': {
        'colors': [MagicColor.WHITE.value, MagicColor.BLACK.value],
        'strategy': 'Incremental advantage through lifegain and card quality',
        'keywords': ['lifelink', 'lifegain', 'card advantage', 'value', 'ETB effects', 'versatile threats'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Blue-Red (Izzet)
    'Izzet Spells Matter': {
        'colors': [MagicColor.BLUE.value, MagicColor.RED.value],
        'strategy': 'Instant and sorcery synergies with prowess and spell-based creatures',
        'keywords': ['instant', 'sorcery', 'prowess', 'spells', 'trigger', 'burn'],
        'archetype': Archetype.TEMPO,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Black-Green (Golgari)
    'Golgari Graveyard Value': {
        'colors': [MagicColor.BLACK.value, MagicColor.GREEN.value],
        'strategy': 'Graveyard-based value engine with recursion and sacrifice',
        'keywords': ['graveyard', 'sacrifice', 'return', 'dredge', 'undergrowth', 'dies'],
        'archetype': Archetype.MIDRANGE,
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Red-White (Boros)
    'Boros Aggro': {
        'colors': [MagicColor.RED.value, MagicColor.WHITE.value],
        'strategy': 'Aggressive red and white creatures, combat tricks, and burn spells',
        'keywords': [
            'haste', 'first strike', 'double strike', 'menace', 'pump', 'attack', 'combat', 'burn', 'damage', 'aggressive', 'removal', 'strike', 'rush', 'charge'
        ],
        'archetype': Archetype.AGGRO,
        'scorer': create_aggressive_scorer,
        'core_card_count': 5,
        'color_priority': 'strict'
    },
    
    # Green-Blue (Simic)
    'Simic Ramp Control': {
        'colors': [MagicColor.GREEN.value, MagicColor.BLUE.value],
        'strategy': 'Ramp into large threats with card draw and protection',
        'keywords': ['ramp', 'mana', 'draw', 'expensive', 'evolve', 'counter', 'adapt'],
        'archetype': Archetype.RAMP,
        'scorer': create_control_scorer,
        'core_card_count': 4
    }
}

# All themes combined for easy access
ALL_THEMES = {**MONO_COLOR_THEMES, **DUAL_COLOR_THEMES}

# Theme categories for organization
THEME_CATEGORIES = {
    Archetype.AGGRO.value: ['White Soldiers', 'Red Goblins', 'Red Burn', 'White Vanguard', 'Rakdos Aggro', 'Boros Aggro'],
    Archetype.MIDRANGE.value: ['White Equipment', 'Black Zombies', 'Black Sacrifice', 'Gruul Midrange', 'Selesnya Value', 'Orzhov Lifegain Value', 'Golgari Graveyard Value'],
    Archetype.CONTROL.value: ['White Angels', 'Blue Wizards', 'Blue Card Draw', 'Black Graveyard', 'Black Control', 'Azorius Control', 'Dimir Mill'],
    Archetype.RAMP.value: ['Red Inferno', 'Green Ramp', 'Simic Ramp Control'],
    Archetype.TEMPO.value: ['Blue Flying', 'Blue Tempo', 'Izzet Spells Matter'],
    Archetype.TRIBAL.value: ['Green Elves', 'Green Beasts'],
    Archetype.ARTIFACTS.value: ['Red Artifacts'],
    Archetype.STOMPY.value: ['Green Stompy']
}

# Color identity mapping for validation
COLOR_IDENTITY_MAP = {
    MagicColor.WHITE.value: 'White',
    MagicColor.BLUE.value: 'Blue', 
    MagicColor.BLACK.value: 'Black',
    MagicColor.RED.value: 'Red',
    MagicColor.GREEN.value: 'Green'
}
