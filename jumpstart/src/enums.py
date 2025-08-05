# Magic: The Gathering Enums Module

from enum import Enum
from typing import List, Dict
from functools import total_ordering


@total_ordering
class Archetype(Enum):
    """Magic: The Gathering deck archetype constants."""
    AFFINITY = 'Affinity'
    AGGRO = 'Aggro'
    ARISTOCRATS = 'Aristocrats'
    ARTIFACTS = 'Artifacts'
    BLINK = 'Blink'
    BURN = 'Burn'
    COMBO = 'Combo'
    CONTROL = 'Control'
    COUNTERS = 'Counters'
    CYCLING = 'Cycling'
    DEVOTION = 'Devotion'
    ELDRAZI = 'Eldrazi'
    ENCHANTMENTS = 'Enchantments'
    ENERGY = 'Energy'
    EQUIPMENT = 'Equipment'
    GRAVEYARD = 'Graveyard'
    HISTORIC = 'Historic'
    INFECT = 'Infect'
    KICKER = 'Kicker'
    LANDFALL = 'Landfall'
    LIFEGAIN = 'Lifegain'
    MADNESS = 'Madness'
    MIDRANGE = 'Midrange'
    MILL = 'Mill'
    MULTICOLOR = 'Multicolor'
    PLANESWALKERS = 'Planeswalkers'
    RAMP = 'Ramp'
    REANIMATOR = 'Reanimator'
    SACRIFICE = 'Sacrifice'
    SLIVERS = 'Slivers'
    SPELLSLINGER = 'Spellslinger'
    STOMPY = 'Stompy'
    STORM = 'Storm'
    TEMPO = 'Tempo'
    TOKENS = 'Tokens'
    TRIBAL = 'Tribal'
    VEHICLES = 'Vehicles'
    VOLTRON = 'Voltron'
    
    def __lt__(self, other):
        """Define ordering for archetype enum values."""
        if not isinstance(other, Archetype):
            return NotImplemented
        # Order by string value
        return self.value < other.value
    
    def __eq__(self, other):
        """Define equality for archetype enum values."""
        if isinstance(other, Archetype):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False
    
    def __hash__(self):
        """Define hash for archetype enum values."""
        return hash(self.value)
    
    @classmethod
    def all_archetypes(cls) -> List[str]:
        """Get all archetype values as a list."""
        return [archetype.value for archetype in cls]
    
    @classmethod
    def aggressive_archetypes(cls) -> List[str]:
        """Get archetypes that are aggressive in nature."""
        return [cls.AGGRO.value, cls.STOMPY.value, cls.TEMPO.value]
    
    @classmethod
    def value_archetypes(cls) -> List[str]:
        """Get archetypes that focus on card advantage and value."""
        return [cls.CONTROL.value, cls.MIDRANGE.value, cls.RAMP.value]


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
