"""Main theme extraction functionality."""

from typing import Dict, List, Set, Tuple, Any, Optional
import pandas as pd
from collections import Counter, defaultdict
import re
import numpy as np
from ..enums import Archetype, MagicColor
from ..scorer import (
    create_default_scorer, create_tribal_scorer, create_equipment_scorer,
    create_aggressive_scorer, create_stompy_scorer, create_artifact_scorer,
    create_control_scorer
)
from .keywords import *


class ThemeExtractor:
    """Extracts potential themes from oracle card data."""

    def __init__(self, oracle_df: pd.DataFrame):
        """Initialize with oracle DataFrame."""
        self.oracle_df = oracle_df.copy()
        self._preprocess_data()
    
    def _preprocess_data(self) -> None:
        """Preprocess the oracle data for analysis."""
        # Clean and normalize text data using original column names
        self.oracle_df['Oracle Text'] = self.oracle_df['Oracle Text'].fillna('').astype(str).str.lower()
        self.oracle_df['Type'] = self.oracle_df['Type'].fillna('').astype(str).str.lower()
        self.oracle_df['Color'] = self.oracle_df['Color'].fillna('').astype(str)
        
        # Convert CMC to numeric, handling non-numeric values
        self.oracle_df['cmc_numeric'] = pd.to_numeric(self.oracle_df['CMC'], errors='coerce').fillna(0)
        
        # Extract creature types
        self.oracle_df['creature_types'] = self.oracle_df['Type'].apply(self._extract_creature_types)
        
        # Calculate derived metrics using numeric CMC
        self.oracle_df['is_expensive'] = self.oracle_df['cmc_numeric'] >= 5
        self.oracle_df['is_cheap'] = self.oracle_df['cmc_numeric'] <= 2
    
    def _extract_creature_types(self, type_line: str) -> Set[str]:
        """Extract creature types from type line."""
        if 'creature' not in type_line:
            return set()
        
        # Split on common delimiters and extract types after 'creature'
        parts = re.split(r'[—\-]', type_line)
        if len(parts) > 1:
            subtypes = parts[1].strip().split()
            return {t.strip() for t in subtypes if t.strip()}
        return set()
    
    def _get_color_combinations(self, min_cards: int = 5) -> List[Tuple[List[str], str]]:
        """Get all color combinations present in the data."""
        color_counts = defaultdict(int)
        
        for _, card in self.oracle_df.iterrows():
            colors = self._parse_colors(card['Color'])  # Use original column name
            if colors:
                color_key = tuple(sorted(colors))
                color_counts[color_key] += 1
        
        # Return combinations with at least min_cards
        valid_combinations = []
        for colors, count in color_counts.items():
            if count >= min_cards:
                color_list = list(colors)
                if len(color_list) == 1:
                    name_prefix = self._get_color_name(color_list[0])
                elif len(color_list) == 2:
                    name_prefix = self._get_guild_name(color_list)
                else:
                    continue  # Skip 3+ color combinations for now
                
                valid_combinations.append((color_list, name_prefix))
        
        return valid_combinations
    
    def _parse_colors(self, colors_str: str) -> List[str]:
        """Parse color string into list of colors."""
        if not colors_str or pd.isna(colors_str) or colors_str == '':
            return []
        
        # Handle different color string formats
        if isinstance(colors_str, str):
            colors_str = str(colors_str).strip()
            
            # If it's a single color character (W, U, B, R, G)
            if len(colors_str) == 1 and colors_str.upper() in ['W', 'U', 'B', 'R', 'G']:
                return [colors_str.upper()]
            
            # If it's multiple characters (like "WU" for white-blue)
            if len(colors_str) <= 5 and all(c.upper() in 'WUBRG' for c in colors_str):
                return list(colors_str.upper())
            
            # Handle bracket/comma separated format like ['W', 'U'] or "W,U"
            cleaned = colors_str.strip('[]').replace("'", "").replace('"', '')
            if ',' in cleaned:
                colors = [c.strip().upper() for c in cleaned.split(',') if c.strip()]
                return [c for c in colors if c in ['W', 'U', 'B', 'R', 'G']]
            
            # Handle space separated
            if ' ' in cleaned:
                colors = [c.strip().upper() for c in cleaned.split() if c.strip()]
                return [c for c in colors if c in ['W', 'U', 'B', 'R', 'G']]
        
        return []
    
    def _get_color_name(self, color: str) -> str:
        """Get full color name from abbreviation."""
        color_map = {
            'W': 'White', 'U': 'Blue', 'B': 'Black', 
            'R': 'Red', 'G': 'Green'
        }
        return color_map.get(color.upper(), color.title())
    
    def _get_guild_name(self, colors: List[str]) -> str:
        """Get guild name for two-color combination."""
        guild_map = {
            ('B', 'G'): 'Golgari', ('G', 'W'): 'Selesnya', ('R', 'W'): 'Boros',
            ('B', 'R'): 'Rakdos', ('G', 'U'): 'Simic', ('R', 'U'): 'Izzet',
            ('B', 'W'): 'Orzhov', ('G', 'R'): 'Gruul', ('U', 'W'): 'Azorius',
            ('B', 'U'): 'Dimir'
        }
        color_key = tuple(sorted([c.upper() for c in colors]))
        return guild_map.get(color_key, f"{self._get_color_name(colors[0])}-{self._get_color_name(colors[1])}")
    
    def _analyze_tribal_themes(self, color_filter: List[str]) -> List[Dict[str, Any]]:
        """Analyze potential tribal themes for given colors."""
        filtered_df = self._filter_by_colors(color_filter)
        tribal_themes = []
        
        # Count creature types
        type_counts = Counter()
        for types_set in filtered_df['creature_types']:
            for creature_type in types_set:
                if creature_type in TRIBAL_TYPES:
                    type_counts[creature_type] += 1
        
        # Generate themes for types with enough cards
        for creature_type, count in type_counts.most_common():
            if count >= 8:  # Minimum threshold for tribal theme
                theme = self._create_tribal_theme(creature_type, color_filter, count)
                if theme:
                    tribal_themes.append(theme)
        
        return tribal_themes
    
    def _analyze_keyword_themes(self, color_filter: List[str]) -> List[Dict[str, Any]]:
        """Analyze themes based on keyword density."""
        filtered_df = self._filter_by_colors(color_filter)
        keyword_themes = []
        
        # Analyze different keyword categories
        theme_categories = [
            ('Equipment', EQUIPMENT_KEYWORDS, Archetype.EQUIPMENT, create_equipment_scorer),
            ('Aggro', AGGRESSIVE_KEYWORDS, Archetype.AGGRO, create_aggressive_scorer),
            ('Control', CONTROL_KEYWORDS, Archetype.CONTROL, create_control_scorer),
            ('Ramp', RAMP_KEYWORDS, Archetype.RAMP, create_default_scorer),
            ('Tempo', TEMPO_KEYWORDS, Archetype.TEMPO, create_aggressive_scorer),
            ('Combo', COMBO_KEYWORDS, Archetype.COMBO, create_default_scorer),
            ('Voltron', VOLTRON_KEYWORDS, Archetype.VOLTRON, create_equipment_scorer),
            ('Aristocrats', ARISTOCRATS_KEYWORDS, Archetype.ARISTOCRATS, create_default_scorer),
            ('Graveyard', GRAVEYARD_KEYWORDS, Archetype.GRAVEYARD, create_default_scorer),
            ('Burn', BURN_KEYWORDS, Archetype.BURN, create_aggressive_scorer),
            ('Spellslinger', SPELLSLINGER_KEYWORDS, Archetype.SPELLSLINGER, create_default_scorer),
            ('Lifegain', LIFEGAIN_KEYWORDS, Archetype.LIFEGAIN, create_default_scorer),
            ('Tokens', TOKEN_KEYWORDS, Archetype.TOKENS, create_default_scorer),
            ('Enchantments', ENCHANTMENTS_KEYWORDS, Archetype.ENCHANTMENTS, create_default_scorer),
            ('Counters', COUNTERS_KEYWORDS, Archetype.COUNTERS, create_default_scorer),
            ('Mill', MILL_KEYWORDS, Archetype.MILL, create_default_scorer),
            ('Landfall', LANDFALL_KEYWORDS, Archetype.LANDFALL, create_default_scorer),
            ('Cycling', CYCLING_KEYWORDS, Archetype.CYCLING, create_default_scorer),
            ('Madness', MADNESS_KEYWORDS, Archetype.MADNESS, create_default_scorer),
            ('Midrange', MIDRANGE_KEYWORDS, Archetype.MIDRANGE, create_default_scorer),
            ('Vehicles', VEHICLES_KEYWORDS, Archetype.VEHICLES, create_default_scorer),
            ('Planeswalkers', PLANESWALKERS_KEYWORDS, Archetype.PLANESWALKERS, create_default_scorer),
            ('Historic', HISTORIC_KEYWORDS, Archetype.HISTORIC, create_default_scorer),
            ('Kicker', KICKER_KEYWORDS, Archetype.KICKER, create_default_scorer),
            ('Multicolor', MULTICOLOR_KEYWORDS, Archetype.MULTICOLOR, create_default_scorer),
            ('Blink', BLINK_KEYWORDS, Archetype.BLINK, create_default_scorer),
            ('Sacrifice', SACRIFICE_KEYWORDS, Archetype.SACRIFICE, create_default_scorer),
            ('Storm', STORM_KEYWORDS, Archetype.STORM, create_default_scorer),
            ('Infect', INFECT_KEYWORDS, Archetype.INFECT, create_aggressive_scorer),
            ('Reanimator', REANIMATOR_KEYWORDS, Archetype.REANIMATOR, create_default_scorer),
            ('Slivers', SLIVERS_KEYWORDS, Archetype.SLIVERS, create_tribal_scorer),
            ('Eldrazi', ELDRAZI_KEYWORDS, Archetype.ELDRAZI, create_default_scorer),
            ('Energy', ENERGY_KEYWORDS, Archetype.ENERGY, create_default_scorer),
            ('Devotion', DEVOTION_KEYWORDS, Archetype.DEVOTION, create_default_scorer),
            ('Affinity', AFFINITY_KEYWORDS, Archetype.AFFINITY, create_artifact_scorer),
        ]
        
        for theme_name, keywords, archetype, scorer in theme_categories:
            keyword_cards = self._count_keyword_cards(filtered_df, keywords)
            if keyword_cards >= 10:  # Minimum threshold
                theme = self._create_keyword_theme(
                    theme_name, color_filter, keywords, archetype, scorer, keyword_cards
                )
                keyword_themes.append(theme)
        
        return keyword_themes
    
    def _analyze_cmc_themes(self, color_filter: List[str]) -> List[Dict[str, Any]]:
        """Analyze themes based on mana cost distribution."""
        filtered_df = self._filter_by_colors(color_filter)
        cmc_themes = []
        
        # Aggressive low-cost theme
        cheap_cards = len(filtered_df[filtered_df['is_cheap']])
        if cheap_cards >= 15:
            theme = {
                'colors': [self._color_to_enum_value(c) for c in color_filter],
                'strategy': 'Fast aggressive deck with efficient low-cost threats',
                'keywords': ['cheap', 'aggressive', 'efficient', 'low cost', 'fast', 'early'],
                'archetype': Archetype.AGGRO,
                'scorer': create_aggressive_scorer,
                'core_card_count': 3
            }
            cmc_themes.append(theme)
        
        # Big mana theme
        expensive_cards = len(filtered_df[filtered_df['is_expensive']])
        if expensive_cards >= 8:
            theme = {
                'colors': [self._color_to_enum_value(c) for c in color_filter],
                'strategy': 'Ramp into expensive threats and powerful late-game spells',
                'keywords': ['expensive', 'big', 'large', 'ramp', 'late game', 'powerful'],
                'archetype': Archetype.RAMP,
                'scorer': create_default_scorer,
                'core_card_count': 3
            }
            cmc_themes.append(theme)
        
        return cmc_themes
    
    def _filter_by_colors(self, color_filter: List[str]) -> pd.DataFrame:
        """Filter DataFrame by color identity."""
        if not color_filter:
            return self.oracle_df
        
        def matches_colors(card_colors_str):
            card_colors = self._parse_colors(card_colors_str)
            if not card_colors:
                return len(color_filter) == 0
            
            card_colors_set = set(c.upper() for c in card_colors)
            filter_colors_set = set(c.upper() for c in color_filter)
            
            # Card must contain all filter colors and no others
            return card_colors_set == filter_colors_set
        
        return self.oracle_df[self.oracle_df['Color'].apply(matches_colors)]
    
    def _count_keyword_cards(self, df: pd.DataFrame, keywords: Set[str]) -> int:
        """Count cards that contain any of the given keywords."""
        count = 0
        for _, card in df.iterrows():
            text = f"{card['Oracle Text']} {card['Type']}".lower()
            if any(keyword in text for keyword in keywords):
                count += 1
        return count
    
    def _create_tribal_theme(self, creature_type: str, colors: List[str], card_count: int) -> Optional[Dict[str, Any]]:
        """Create a tribal theme dictionary."""
        color_prefix = self._get_color_prefix(colors)
        
        # Generate tribal-specific keywords
        base_keywords = ['tribal', creature_type, 'creature', 'enters', 'lord', 'gets +']
        
        # Add type-specific keywords
        type_keywords = {
            'soldier': ['anthem', 'pump', 'attack', 'vigilance', 'first strike'],
            'wizard': ['instant', 'sorcery', 'prowess', 'draw', 'counter'],
            'goblin': ['haste', 'sacrifice', 'token', 'aggressive'],
            'elf': ['mana', 'tap', 'forest', 'add', 'produces'],
            'zombie': ['graveyard', 'return', 'sacrifice', 'dies'],
            'angel': ['flying', 'vigilance', 'lifelink', 'protection'],
            'dragon': ['flying', 'expensive', 'power', 'trample', 'haste'],
            'beast': ['power', 'toughness', 'trample', 'fight'],
        }
        
        keywords = base_keywords + type_keywords.get(creature_type, [])
        
        return {
            'colors': [self._color_to_enum_value(c) for c in colors],
            'strategy': f'{creature_type.title()} tribal with synergistic effects and creature bonuses',
            'keywords': keywords,
            'archetype': Archetype.TRIBAL,
            'scorer': create_tribal_scorer,
            'core_card_count': min(4, max(3, card_count // 4))
        }
    
    def _create_keyword_theme(self, theme_name: str, colors: List[str], keywords: Set[str], 
                            archetype: Archetype, scorer, card_count: int) -> Dict[str, Any]:
        """Create a keyword-based theme dictionary."""
        return {
            'colors': [self._color_to_enum_value(c) for c in colors],
            'strategy': f'{theme_name} strategy with {archetype.value.lower()} gameplan',
            'keywords': list(keywords),
            'archetype': archetype,
            'scorer': scorer,
            'core_card_count': min(5, max(3, card_count // 8))
        }
    
    def _get_color_prefix(self, colors: List[str]) -> str:
        """Get color prefix for theme naming."""
        if len(colors) == 1:
            return self._get_color_name(colors[0])
        elif len(colors) == 2:
            return self._get_guild_name(colors)
        else:
            return "Multicolor"
    
    def _color_to_enum_value(self, color: str) -> str:
        """Convert color string to MagicColor enum value."""
        color_map = {
            'W': MagicColor.WHITE.value,
            'U': MagicColor.BLUE.value,
            'B': MagicColor.BLACK.value,
            'R': MagicColor.RED.value,
            'G': MagicColor.GREEN.value
        }
        return color_map.get(color.upper(), color.upper())
    
    def _extract_guild_themes(self) -> Dict[str, Dict[str, Any]]:
        """Extract guild themes with lower thresholds specifically for 2-color combinations."""
        guild_themes = {}
        
        # Get all 2-color combinations with any number of cards
        color_combinations = self._get_color_combinations(min_cards=1)
        two_color_combinations = [(colors, name) for colors, name in color_combinations if len(colors) == 2]
        
        for colors, guild_name in two_color_combinations:
            filtered_df = self._filter_by_colors(colors)
            card_count = len(filtered_df)
            
            if card_count >= 3:  # Lower threshold for guilds
                # Determine best archetype based on guild identity
                guild_archetypes = {
                    'Azorius': Archetype.CONTROL,      # U/W - Control
                    'Dimir': Archetype.CONTROL,        # U/B - Control/Mill  
                    'Rakdos': Archetype.AGGRO,         # B/R - Aggro/Burn
                    'Gruul': Archetype.AGGRO,          # R/G - Aggro/Ramp
                    'Selesnya': Archetype.MIDRANGE,    # G/W - Tokens/Midrange
                    'Orzhov': Archetype.MIDRANGE,      # B/W - Lifegain/Midrange
                    'Izzet': Archetype.TEMPO,          # U/R - Spells/Tempo
                    'Golgari': Archetype.MIDRANGE,     # B/G - Graveyard/Midrange
                    'Boros': Archetype.AGGRO,         # R/W - Aggro/Equipment
                    'Simic': Archetype.RAMP            # G/U - Ramp/Value
                }
                
                archetype = guild_archetypes.get(guild_name, Archetype.MIDRANGE)
                
                # Create guild-specific keywords based on the guild identity
                guild_keywords = {
                    'Azorius': ['flying', 'counter', 'detain', 'control', 'flying creatures'],
                    'Dimir': ['mill', 'graveyard', 'card draw', 'control', 'surveillance'], 
                    'Rakdos': ['haste', 'aggressive', 'damage', 'sacrifice', 'unleash'],
                    'Gruul': ['trample', 'haste', 'power matters', 'bloodrush', 'ramp'],
                    'Selesnya': ['tokens', 'populate', 'convoke', 'creatures matter', 'anthem'],
                    'Orzhov': ['lifegain', 'extort', 'removal', 'aristocrats', 'afterlife'],
                    'Izzet': ['instant', 'sorcery', 'spells matter', 'card draw', 'overload'],
                    'Golgari': ['graveyard', 'scavenge', 'dredge', 'sacrifice', 'undergrowth'],
                    'Boros': ['equipment', 'battalion', 'mentor', 'aggressive', 'combat'],
                    'Simic': ['card draw', 'ramp', 'evolve', 'adapt', '+1/+1 counters']
                }
                
                keywords = guild_keywords.get(guild_name, ['multicolor', 'synergy'])
                
                # Get appropriate scorer for archetype
                scorer_map = {
                    Archetype.AGGRO: create_aggressive_scorer,
                    Archetype.CONTROL: create_control_scorer,
                    Archetype.MIDRANGE: create_default_scorer,
                    Archetype.TEMPO: create_aggressive_scorer,
                    Archetype.RAMP: create_default_scorer
                }
                scorer = scorer_map.get(archetype, create_default_scorer)
                
                # Create the theme
                theme = {
                    'colors': [self._color_to_enum_value(c) for c in colors],
                    'strategy': f'{guild_name} guild synergies with {archetype.value.lower()} gameplan',
                    'keywords': keywords,
                    'archetype': archetype,
                    'scorer': scorer,
                    'core_card_count': min(3, max(2, card_count // 2))
                }
                
                theme_name = f"{guild_name} {archetype.value.title()}"
                guild_themes[theme_name] = theme
        
        return guild_themes
    
    def extract_themes(self, min_cards_per_theme: int = 10, include_guilds: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Extract all potential themes from the oracle data.
        
        Args:
            min_cards_per_theme: Minimum number of cards required for a theme
            include_guilds: Whether to include guild themes with lower thresholds
            
        Returns:
            Dictionary of theme names to theme configurations
        """
        all_themes = {}
        
        # Get valid color combinations with dynamic threshold
        min_combination_cards = max(5, min_cards_per_theme // 2)  # Use half the theme threshold
        color_combinations = self._get_color_combinations(min_cards=min_combination_cards)
        
        for colors, color_prefix in color_combinations:
            # Analyze tribal themes
            tribal_themes = self._analyze_tribal_themes(colors)
            for i, theme in enumerate(tribal_themes):
                creature_type = [k for k in theme['keywords'] if k in TRIBAL_TYPES][0]
                theme_name = f"{color_prefix} {creature_type.title()}s"
                all_themes[theme_name] = theme
            
            # Analyze keyword themes
            keyword_themes = self._analyze_keyword_themes(colors)
            for i, theme in enumerate(keyword_themes):
                # Use enum value directly for theme naming
                archetype_name = theme['archetype'].value
                
                theme_name = f"{color_prefix} {archetype_name}"
                if theme_name not in all_themes:  # Avoid duplicates
                    all_themes[theme_name] = theme
            
            # Analyze CMC-based themes
            cmc_themes = self._analyze_cmc_themes(colors)
            for i, theme in enumerate(cmc_themes):
                archetype_name = 'Fast' if theme['archetype'] == Archetype.AGGRO else 'Big'
                theme_name = f"{color_prefix} {archetype_name}"
                if theme_name not in all_themes:
                    all_themes[theme_name] = theme
        
        # Add guild themes if requested
        if include_guilds:
            guild_themes = self._extract_guild_themes()
            all_themes.update(guild_themes)
        
        return all_themes
    
    def generate_theme_summary(self, themes: Dict[str, Dict[str, Any]]) -> str:
        """Generate a summary report of extracted themes."""
        summary = ["# Extracted Themes Summary\n"]
        
        # Group by archetype
        by_archetype = defaultdict(list)
        for name, theme in themes.items():
            by_archetype[theme['archetype']].append((name, theme))
        
        for archetype, theme_list in by_archetype.items():
            summary.append(f"## {archetype.value} Themes ({len(theme_list)})")
            for name, theme in sorted(theme_list):
                colors = " + ".join([c.split('.')[-1] for c in theme['colors']])
                summary.append(f"- **{name}** ({colors}): {theme['strategy']}")
            summary.append("")
        
        summary.append(f"**Total Themes Found:** {len(themes)}")
        return "\n".join(summary)
    
    def select_optimal_themes(self, themes: Dict[str, Dict[str, Any]], 
                            mono_count: int = 10, dual_count: int = 10,
                            prioritize_buildability: bool = True,
                            diversity_weight: float = 0.3) -> Dict[str, Dict[str, Any]]:
        """
        Select an optimal subset of themes for deck construction based on buildability and diversity.
        
        Args:
            themes: Dictionary of all available themes
            mono_count: Number of mono-color themes to select
            dual_count: Number of dual-color themes to select  
            prioritize_buildability: Whether to prioritize themes with more available cards
            diversity_weight: Weight for diversity scoring (0-1), higher = more diverse
            
        Returns:
            Dictionary of selected themes
        """
        print(f"🎯 Selecting optimal themes: {mono_count} mono + {dual_count} dual = {mono_count + dual_count} total")
        
        # Separate mono and dual color themes
        mono_themes = {name: theme for name, theme in themes.items() 
                      if len(theme['colors']) == 1}
        dual_themes = {name: theme for name, theme in themes.items() 
                      if len(theme['colors']) == 2}
        
        print(f"Available: {len(mono_themes)} mono, {len(dual_themes)} dual themes")
        
        # Select mono-color themes with balanced color distribution
        selected_mono = self._select_balanced_mono_themes(
            mono_themes, mono_count, prioritize_buildability, diversity_weight
        )
        
        # Select dual-color themes  
        selected_dual = self._select_themes_by_criteria(
            dual_themes, dual_count, prioritize_buildability, diversity_weight, "dual-color"
        )
        
        # Combine selections
        selected_themes = {}
        selected_themes.update(selected_mono)
        selected_themes.update(selected_dual)
        
        print(f"\n✅ Selected {len(selected_themes)} themes:")
        print(f"  📦 Mono-color: {len(selected_mono)}")
        print(f"  🎭 Dual-color: {len(selected_dual)}")
        
        # Show selection summary
        self._print_selection_summary(selected_themes)
        
        return selected_themes
    
    def _select_themes_by_criteria(self, themes: Dict[str, Dict[str, Any]], 
                                 count: int, prioritize_buildability: bool,
                                 diversity_weight: float, theme_type: str) -> Dict[str, Dict[str, Any]]:
        """Select themes based on buildability and diversity criteria."""
        if len(themes) <= count:
            print(f"  ℹ️  Only {len(themes)} {theme_type} themes available (requested {count})")
            return themes
        
        # Score each theme
        scored_themes = []
        for name, theme in themes.items():
            score = self._calculate_theme_score(name, theme, themes, prioritize_buildability, diversity_weight)
            scored_themes.append((name, theme, score))
        
        # Sort by score (highest first) and select top N
        scored_themes.sort(key=lambda x: x[2], reverse=True)
        selected = {name: theme for name, theme, score in scored_themes[:count]}
        
        print(f"  🎯 Selected top {len(selected)} {theme_type} themes")
        
        return selected
    
    def _select_balanced_mono_themes(self, mono_themes: Dict[str, Dict[str, Any]], 
                                   count: int, prioritize_buildability: bool,
                                   diversity_weight: float) -> Dict[str, Dict[str, Any]]:
        """Select mono-color themes with balanced distribution across all five colors."""
        if len(mono_themes) <= count:
            print(f"  ℹ️  Only {len(mono_themes)} mono-color themes available (requested {count})")
            return mono_themes
        
        # Group themes by color
        themes_by_color = defaultdict(list)
        for name, theme in mono_themes.items():
            color = theme['colors'][0]  # Single color for mono themes
            # Normalize color notation (handle both 'W' and 'WHITE' formats)
            if '.' in color:
                color_key = color.split('.')[-1]  # Extract 'W' from 'MagicColor.WHITE'
            else:
                color_key = color
            themes_by_color[color_key].append((name, theme))
        
        # Calculate themes per color (as evenly as possible)
        colors = ['W', 'U', 'B', 'R', 'G']  # White, Blue, Black, Red, Green
        themes_per_color = count // 5
        extra_themes = count % 5
        
        print(f"  🎨 Distributing {count} mono themes: {themes_per_color} per color + {extra_themes} extra")
        
        selected = {}
        color_distribution = {}
        
        # First pass: select base number of themes per color
        for color in colors:
            if color not in themes_by_color:
                print(f"  ⚠️  No themes available for color {color}")
                color_distribution[color] = 0
                continue
                
            available = themes_by_color[color]
            target_count = themes_per_color
            
            # Score and select best themes for this color
            scored_themes = []
            for name, theme in available:
                score = self._calculate_theme_score(name, theme, mono_themes, prioritize_buildability, diversity_weight)
                scored_themes.append((name, theme, score))
            
            # Sort by score and select top themes
            scored_themes.sort(key=lambda x: x[2], reverse=True)
            selected_count = min(target_count, len(scored_themes))
            
            for i in range(selected_count):
                name, theme, score = scored_themes[i]
                selected[name] = theme
            
            color_distribution[color] = selected_count
            print(f"    {color}: {selected_count} themes selected")
        
        # Second pass: distribute extra themes to colors with available themes
        remaining_extra = extra_themes
        while remaining_extra > 0:
            # Find colors that still have available themes
            for color in colors:
                if remaining_extra <= 0:
                    break
                    
                if color not in themes_by_color:
                    continue
                    
                current_selected = color_distribution[color]
                available_count = len(themes_by_color[color])
                
                if current_selected < available_count:
                    # Select next best theme for this color
                    available = themes_by_color[color]
                    scored_themes = []
                    for name, theme in available:
                        if name not in selected:  # Not already selected
                            score = self._calculate_theme_score(name, theme, mono_themes, prioritize_buildability, diversity_weight)
                            scored_themes.append((name, theme, score))
                    
                    if scored_themes:
                        scored_themes.sort(key=lambda x: x[2], reverse=True)
                        name, theme, score = scored_themes[0]
                        selected[name] = theme
                        color_distribution[color] += 1
                        remaining_extra -= 1
                        print(f"    {color}: +1 extra theme ({color_distribution[color]} total)")
            
            # Safety check to avoid infinite loop
            if remaining_extra == extra_themes:
                print(f"  ⚠️  Could not distribute {remaining_extra} extra themes (no more available)")
                break
            extra_themes = remaining_extra
        
        print(f"  🎯 Final distribution: {dict(color_distribution)}")
        print(f"  ✅ Selected {len(selected)} balanced mono-color themes")
        
        return selected
    
    def _calculate_theme_score(self, theme_name: str, theme: Dict[str, Any], 
                             all_themes: Dict[str, Dict[str, Any]],
                             prioritize_buildability: bool, diversity_weight: float) -> float:
        """Calculate a score for a theme based on buildability and diversity."""
        score = 0.0
        
        # 1. Buildability Score (0-1)
        buildability = self._assess_buildability(theme_name, theme)
        score += buildability * (0.7 if prioritize_buildability else 0.5)
        
        # 2. Diversity Score (0-1) 
        diversity = self._assess_diversity(theme, all_themes)
        score += diversity * diversity_weight
        
        # 3. Archetype Balance Score (0-1)
        balance = self._assess_archetype_rarity(theme, all_themes)
        score += balance * (1.0 - diversity_weight - (0.7 if prioritize_buildability else 0.5))
        
        return score
    
    def _assess_buildability(self, theme_name: str, theme: Dict[str, Any]) -> float:
        """Assess how likely a theme is to build successfully into a complete deck."""
        colors = theme['colors']
        is_mono = len(colors) == 1
        
        # Filter cards for this theme
        filtered_df = self._filter_by_colors([c.split('.')[-1] for c in colors])
        available_cards = len(filtered_df)
        
        # Base score from card availability
        card_score = min(available_cards / 30.0, 1.0)  # Normalize to 30 cards as ideal
        
        # Keyword density bonus
        keywords = set(theme.get('keywords', []))
        keyword_matches = 0
        for _, card in filtered_df.iterrows():
            text = f"{card['Oracle Text']} {card['Type']}".lower()
            if any(keyword in text for keyword in keywords):
                keyword_matches += 1
        
        keyword_score = min(keyword_matches / max(available_cards, 1), 0.5)
        
        # Archetype suitability
        archetype = theme.get('archetype')
        archetype_score = 0.8  # Default good score
        
        if archetype:
            # Bonus for archetypes that are easier to build
            easy_archetypes = [Archetype.AGGRO, Archetype.MIDRANGE, Archetype.TRIBAL]
            if archetype in easy_archetypes:
                archetype_score = 1.0
            elif archetype in [Archetype.CONTROL, Archetype.COMBO]:
                archetype_score = 0.6  # Harder to build well
        
        # Color availability bonus (mono-color themes easier to build)
        color_score = 1.0 if is_mono else 0.8
        
        total_score = (card_score * 0.4 + keyword_score * 0.3 + 
                      archetype_score * 0.2 + color_score * 0.1)
        
        return min(total_score, 1.0)
    
    def _assess_diversity(self, theme: Dict[str, Any], all_themes: Dict[str, Dict[str, Any]]) -> float:
        """Assess how much diversity this theme adds to the overall selection."""
        archetype = theme.get('archetype')
        colors = theme['colors']
        strategy = theme.get('strategy', '')
        
        # Count similar themes
        similar_archetype_count = sum(1 for t in all_themes.values() 
                                    if t.get('archetype') == archetype)
        similar_color_count = sum(1 for t in all_themes.values() 
                                if set(t['colors']) == set(colors))
        
        # Diversity bonus for underrepresented archetypes/colors
        archetype_diversity = 1.0 / max(similar_archetype_count, 1)
        color_diversity = 1.0 / max(similar_color_count, 1)
        
        # Strategy uniqueness (basic text analysis)
        strategy_words = set(strategy.lower().split())
        strategy_diversity = len(strategy_words) / max(len(strategy.split()), 1)
        
        diversity_score = (archetype_diversity * 0.5 + color_diversity * 0.3 + 
                         strategy_diversity * 0.2)
        
        return min(diversity_score, 1.0)
    
    def _assess_archetype_rarity(self, theme: Dict[str, Any], 
                               all_themes: Dict[str, Dict[str, Any]]) -> float:
        """Give bonus to archetypes that are underrepresented."""
        archetype = theme.get('archetype')
        
        # Count archetype frequency
        archetype_counts = defaultdict(int)
        for t in all_themes.values():
            if t.get('archetype'):
                archetype_counts[t['archetype']] += 1
        
        total_themes = len(all_themes)
        current_count = archetype_counts[archetype]
        
        # Bonus for rare archetypes
        rarity_score = 1.0 - (current_count / max(total_themes, 1))
        
        return max(rarity_score, 0.1)  # Minimum score of 0.1
    
    def _print_selection_summary(self, selected_themes: Dict[str, Dict[str, Any]]):
        """Print a summary of selected themes."""
        print(f"\n📋 THEME SELECTION SUMMARY:")
        print("=" * 50)
        
        # Group by color count
        mono_themes = {name: theme for name, theme in selected_themes.items() 
                      if len(theme['colors']) == 1}
        dual_themes = {name: theme for name, theme in selected_themes.items() 
                      if len(theme['colors']) == 2}
        
        # Mono-color themes with color distribution
        if mono_themes:
            print("🟡 MONO-COLOR THEMES:")
            
            # Group by color for distribution display
            color_groups = defaultdict(list)
            for name, theme in mono_themes.items():
                color = theme['colors'][0]
                if '.' in color:
                    color_key = color.split('.')[-1]
                else:
                    color_key = color
                color_groups[color_key].append((name, theme))
            
            # Display by color
            color_names = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green'}
            for color in ['W', 'U', 'B', 'R', 'G']:
                if color in color_groups:
                    print(f"  {color_names[color]} ({color}): {len(color_groups[color])} themes")
                    for name, theme in sorted(color_groups[color]):
                        archetype = theme['archetype'].value if hasattr(theme['archetype'], 'value') else str(theme['archetype'])
                        print(f"    • {name:<25} - {archetype}")
                else:
                    print(f"  {color_names[color]} ({color}): 0 themes")
        
        # Dual-color themes  
        if dual_themes:
            print("\n🎭 DUAL-COLOR THEMES:")
            for name, theme in sorted(dual_themes.items()):
                colors = '+'.join([c.split('.')[-1] if '.' in c else c for c in theme['colors']])
                archetype = theme['archetype'].value if hasattr(theme['archetype'], 'value') else str(theme['archetype'])
                print(f"  • {name:<25} ({colors}) - {archetype}")
        
        # Archetype distribution
        archetype_counts = defaultdict(int)
        for theme in selected_themes.values():
            archetype = theme['archetype']
            if hasattr(archetype, 'value'):
                archetype = archetype.value
            archetype_counts[str(archetype)] += 1
        
        print(f"\n🎯 ARCHETYPE DISTRIBUTION:")
        for archetype, count in sorted(archetype_counts.items()):
            print(f"  • {archetype:<12}: {count} themes")
        
        print(f"\n✅ Ready for deck construction with {len(selected_themes)} optimized themes!")
