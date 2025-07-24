# Jumpstart Cube Themes Configuration

from enum import Enum
from typing import Set, List, Dict

class MagicColor(Enum):
    """Magic: The Gathering color constants."""
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'
    COLORLESS = 'C'
    
    @classmethod
    def all_colors(cls) -> List[str]:
        """Get all color values as a list."""
        return [color.value for color in cls if color != cls.COLORLESS]
    
    @classmethod
    def all_colors_including_colorless(cls) -> List[str]:
        """Get all color values including colorless as a list."""
        return [color.value for color in cls]
    
    @classmethod
    def color_names(cls) -> Dict[str, str]:
        """Get mapping of color abbreviations to full names."""
        return {
            cls.WHITE.value: 'White',
            cls.BLUE.value: 'Blue', 
            cls.BLACK.value: 'Black',
            cls.RED.value: 'Red',
            cls.GREEN.value: 'Green',
            cls.COLORLESS.value: 'Colorless'
        }
    
    @classmethod
    def basic_land_names(cls) -> Dict[str, str]:
        """Get mapping of colors to basic land type names."""
        return {
            cls.WHITE.value: 'plains',
            cls.BLUE.value: 'island',
            cls.BLACK.value: 'swamp', 
            cls.RED.value: 'mountain',
            cls.GREEN.value: 'forest'
        }

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
        'colors': ['W'],
        'strategy': 'Aggressive tribal deck focused on soldier creatures with anthem effects',
        'keywords': ['soldier', 'tribal', 'anthem', 'pump', 'attack', 'vigilance', 'first strike'],
        'archetype': 'Aggro',
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'White Equipment': {
        'colors': ['W'],
        'strategy': 'Equipment-based deck with efficient creatures and powerful gear',
        'keywords': ['equipment', 'attach', 'equipped', 'equip', 'metalcraft', 'artifact', 'power', 'toughness', 
                    'sword', 'blade', 'equipped creature', 'gets +', 'artifact creature', 'living weapon', 'armor'],
        'archetype': 'Midrange',
        'scorer': create_equipment_scorer,
        'core_card_count': 5
    },
    'White Angels': {
        'colors': ['W'],
        'strategy': 'Mid-to-late game deck with powerful flying angels and protection',
        'keywords': ['angel', 'flying', 'vigilance', 'lifelink', 'protection', 'expensive'],
        'archetype': 'Control',
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    'White Weenies': {
        'colors': ['W'],
        'strategy': 'Aggressive low-cost creatures with efficient stats and combat abilities',
        'keywords': ['creature', 'cheap', 'aggressive', 'power', 'attack', 'first strike', 'vigilance', 'efficient', 'low cost', 'small'],
        'archetype': 'Aggro',
        'scorer': create_aggressive_scorer,
        'core_card_count': 3
    },
    
    # Blue themes
    'Blue Flying': {
        'colors': ['U'],
        'strategy': 'Evasive creatures with flying and tempo spells',
        'keywords': ['flying', 'bird', 'drake', 'spirit', 'bounce', 'counter', 'draw'],
        'archetype': 'Tempo',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    'Blue Wizards': {
        'colors': ['U'],
        'strategy': 'Wizard tribal with spell-based synergies and card advantage',
        'keywords': ['wizard', 'instant', 'sorcery', 'prowess', 'draw', 'counter', 'tribal'],
        'archetype': 'Control',
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Blue Card Draw': {
        'colors': ['U'],
        'strategy': 'Card advantage engine with draw spells and library manipulation',
        'keywords': ['draw', 'card', 'scry', 'look', 'library', 'hand', 'cycling'],
        'archetype': 'Control',
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    'Blue Tempo': {
        'colors': ['U'],
        'strategy': 'Efficient creatures with evasion and tempo spells for board control',
        'keywords': ['bounce', 'return', 'counter', 'flying', 'flash', 'prowess', 'tempo', 'efficient', 'evasion'],
        'archetype': 'Tempo',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Black themes
    'Black Zombies': {
        'colors': ['B'],
        'strategy': 'Zombie tribal with graveyard recursion and sacrifice synergies',
        'keywords': ['zombie', 'tribal', 'graveyard', 'return', 'sacrifice', 'dies'],
        'archetype': 'Midrange',
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Black Graveyard': {
        'colors': ['B'],
        'strategy': 'Graveyard-based value engine with recursion and reanimation',
        'keywords': ['graveyard', 'return', 'mill', 'flashback', 'unearth', 'threshold'],
        'archetype': 'Control',
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    'Black Sacrifice': {
        'colors': ['B'],
        'strategy': 'Sacrifice-based deck with death triggers and value generation',
        'keywords': ['sacrifice', 'dies', 'death', 'aristocrats', 'token', 'whenever'],
        'archetype': 'Midrange',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    'Black Control': {
        'colors': ['B'],
        'strategy': 'Control deck with removal spells and efficient creatures for board control',
        'keywords': ['destroy', 'remove', 'target', 'exile', 'control', 'doom blade', 'murder', 'kill', 'discard', 'draw'],
        'archetype': 'Control',
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    
    # Red themes
    'Red Goblins': {
        'colors': ['R'],
        'strategy': 'Fast goblin tribal with haste and explosive plays',
        'keywords': ['goblin', 'tribal', 'haste', 'sacrifice', 'token', 'aggressive'],
        'archetype': 'Aggro',
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Red Burn': {
        'colors': ['R'],
        'strategy': 'Direct damage spells and hasty creatures for quick wins',
        'keywords': ['damage', 'burn', 'lightning', 'shock', 'direct', 'haste', 'instant'],
        'archetype': 'Aggro',
        'scorer': create_aggressive_scorer,
        'core_card_count': 4
    },
    'Red Dragons': {
        'colors': ['R'],
        'strategy': 'Expensive dragons with powerful effects and flying',
        'keywords': ['dragon', 'flying', 'expensive', 'power', 'trample', 'haste'],
        'archetype': 'Ramp',
        'scorer': create_tribal_scorer,
        'core_card_count': 3
    },
    'Red Artifacts': {
        'colors': ['R'],
        'strategy': 'Artifact-based deck with improvise and metalcraft synergies',
        'keywords': ['artifact', 'improvise', 'metalcraft', 'construct', 'servo', 'energy', 
                    'equipment', 'enters', 'tap', 'sacrifice', 'colorless', 'cost', 'thopter'],
        'archetype': 'Artifacts',
        'scorer': create_artifact_scorer,
        'core_card_count': 4
    },
    
    # Green themes
    'Green Elves': {
        'colors': ['G'],
        'strategy': 'Elf tribal with mana acceleration and creature synergies',
        'keywords': ['elf', 'tribal', 'mana', 'tap', 'forest', 'counter', 'token', 'druid', 
                    'shaman', 'ranger', 'creature', 'add', 'produces', 'enters', 'lord', 
                    'gets +', 'elves you control', 'elf creature'],
        'archetype': 'Tribal',
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    },
    'Green Ramp': {
        'colors': ['G'],
        'strategy': 'Mana acceleration into large threats and expensive spells',
        'keywords': ['mana', 'land', 'search', 'expensive', 'big', 'ritual', 'forest'],
        'archetype': 'Ramp',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    'Green Stompy': {
        'colors': ['G'],
        'strategy': 'Large creatures with trample and pump effects',
        'keywords': ['trample', 'power', 'toughness', 'pump', 'overrun', 'fight', 'big', 'large', 
                    'creature', 'beast', 'giant', 'wurm', 'elemental', '4/4', '5/5', '6/6', 
                    'expensive', 'high power', 'stats'],
        'archetype': 'Stompy',  # Custom archetype instead of generic Aggro
        'scorer': create_aggressive_scorer,
        'core_card_count': 3
    },
    'Green Beasts': {
        'colors': ['G'],
        'strategy': 'Large beast creatures with powerful abilities',
        'keywords': ['beast', 'tribal', 'power', 'toughness', 'enters', 'expensive', 'bear', 
                    'wolf', 'elephant', 'rhino', 'boar', 'ape', 'creature', 'large', 'big', 
                    'trample', 'fight', 'lord', 'gets +', 'beasts you control'],
        'archetype': 'Tribal',
        'scorer': create_tribal_scorer,
        'core_card_count': 4
    }
}

# Dual-color themes (2-color combinations)
DUAL_COLOR_THEMES = {
    # White-Blue (Azorius)
    'Azorius Control': {
        'colors': ['W', 'U'],
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
        'archetype': 'Control',
        'color_priority': 'strict',  # Prioritize true WU cards
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    
    # Blue-Black (Dimir)
    'Dimir Mill': {
        'colors': ['U', 'B'],
        'strategy': 'Mill-based strategy with graveyard interaction and card advantage',
        'keywords': ['mill', 'graveyard', 'library', 'flashback', 'threshold', 'draw'],
        'archetype': 'Control',
        'scorer': create_control_scorer,
        'core_card_count': 4
    },
    
    # Black-Red (Rakdos)
    'Rakdos Aggro': {
        'colors': ['B', 'R'],
        'strategy': 'Aggressive deck with efficient creatures and direct damage',
        'keywords': ['haste', 'damage', 'aggressive', 'sacrifice', 'burn', 'power'],
        'archetype': 'Aggro',
        'scorer': create_aggressive_scorer,
        'core_card_count': 3
    },
    
    # Red-Green (Gruul)
    'Gruul Midrange': {
        'colors': ['R', 'G'],
        'strategy': 'Efficient midrange creatures with aggressive abilities and versatile spells',
        'keywords': ['haste', 'trample', 'efficient', 'versatile', 'combat', 'removal', 
                    'creature', 'aggressive', 'power', 'damage', 'burn', 'fight', 
                    'enters', 'whenever', 'attack', 'deal damage', 'direct'],
        'archetype': 'Midrange',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Green-White (Selesnya)
    'Selesnya Value': {
        'colors': ['G', 'W'],
        'strategy': 'Incremental advantage through efficient creatures, removal, and versatile utility spells',
        'keywords': ['efficient', 'creature', 'removal', 'destroy', 'exile', 'enchantment', 
                    'versatile', 'value', 'enters', 'lifegain', 'vigilance', 'flying', 
                    'combat tricks', 'instant', 'sorcery', 'token', 'utility', 'aura'],
        'archetype': 'Midrange',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # White-Black (Orzhov)
    'Orzhov Lifegain Value': {
        'colors': ['W', 'B'],
        'strategy': 'Incremental advantage through lifegain and card quality',
        'keywords': ['lifelink', 'lifegain', 'card advantage', 'value', 'ETB effects', 'versatile threats'],
        'archetype': 'Midrange',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Blue-Red (Izzet)
    'Izzet Spells Matter': {
        'colors': ['U', 'R'],
        'strategy': 'Instant and sorcery synergies with prowess and spell-based creatures',
        'keywords': ['instant', 'sorcery', 'prowess', 'spells', 'trigger', 'burn'],
        'archetype': 'Tempo',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Black-Green (Golgari)
    'Golgari Graveyard Value': {
        'colors': ['B', 'G'],
        'strategy': 'Graveyard-based value engine with recursion and sacrifice',
        'keywords': ['graveyard', 'sacrifice', 'return', 'dredge', 'undergrowth', 'dies'],
        'archetype': 'Midrange',
        'scorer': create_default_scorer,
        'core_card_count': 3
    },
    
    # Red-White (Boros)
    'Boros Equipment Aggro': {
        'colors': ['R', 'W'],
        'strategy': 'Aggressive creatures with equipment support and combat tricks',
        'keywords': ['equipment', 'haste', 'first strike', 'attack', 'combat', 'pump', 'equip', 'equipped',
                    'sword', 'blade', 'artifact', 'gets +', 'equipped creature', 'attach', 'living weapon'],
        'archetype': 'Aggro',
        'scorer': create_equipment_scorer,
        'core_card_count': 5
    },
    
    # Green-Blue (Simic)
    'Simic Ramp Control': {
        'colors': ['G', 'U'],
        'strategy': 'Ramp into large threats with card draw and protection',
        'keywords': ['ramp', 'mana', 'draw', 'expensive', 'evolve', 'counter', 'adapt'],
        'archetype': 'Ramp',
        'scorer': create_control_scorer,
        'core_card_count': 4
    }
}

# All themes combined for easy access
ALL_THEMES = {**MONO_COLOR_THEMES, **DUAL_COLOR_THEMES}

# Theme categories for organization
THEME_CATEGORIES = {
    'Aggressive': ['White Soldiers', 'Red Goblins', 'Red Burn', 'Green Stompy', 'White Weenies', 'Rakdos Aggro', 'Boros Equipment Aggro'],
    'Midrange': ['White Equipment', 'Black Zombies', 'Black Sacrifice', 'Red Artifacts', 'Green Beasts', 'Gruul Midrange', 'Selesnya Value', 'Orzhov Lifegain Value', 'Golgari Graveyard Value'],
    'Control': ['White Angels', 'Blue Wizards', 'Blue Card Draw', 'Black Graveyard', 'Black Control', 'Azorius Control', 'Dimir Mill'],
    'Ramp': ['Red Dragons', 'Green Elves', 'Green Ramp', 'Simic Ramp Control'],
    'Tempo': ['Blue Flying', 'Blue Tempo', 'Izzet Spells Matter']
}

# Color identity mapping for validation
COLOR_IDENTITY_MAP = {
    'W': 'White',
    'U': 'Blue', 
    'B': 'Black',
    'R': 'Red',
    'G': 'Green'
}
