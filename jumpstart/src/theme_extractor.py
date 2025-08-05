from typing import Dict, List, Set, Tuple, Any, Optional
import pandas as pd
from collections import Counter, defaultdict
import re
import numpy as np
from .enums import Archetype, MagicColor
from .scorer import (
    create_default_scorer, create_tribal_scorer, create_equipment_scorer,
    create_aggressive_scorer, create_stompy_scorer, create_artifact_scorer,
    create_control_scorer
)

class ThemeExtractor:
    """Extracts potential themes from oracle card data."""
    
    # Common tribal creature types
    TRIBAL_TYPES = {
        'soldier', 'wizard', 'goblin', 'elf', 'zombie', 'angel', 'dragon', 
        'beast', 'bird', 'cat', 'dog', 'human', 'vampire', 'werewolf',
        'knight', 'warrior', 'rogue', 'cleric', 'shaman', 'druid'
    }
    
    # Equipment and artifact keywords
    EQUIPMENT_KEYWORDS = {
        'equipment', 'equip', 'equipped', 'attach', 'metalcraft', 'artifact',
        'sword', 'blade', 'armor', 'weapon', 'improvise', 'construct', 'servo'
    }
    
    # Aggressive keywords
    AGGRESSIVE_KEYWORDS = {
        'haste', 'first strike', 'double strike', 'menace', 'aggressive',
        'attack', 'combat', 'burn', 'damage', 'rush', 'charge'
    }
    
    # Control keywords
    CONTROL_KEYWORDS = {
        'counter', 'destroy', 'exile', 'remove', 'control', 'draw',
        'scry', 'flying', 'vigilance', 'lifelink', 'protection'
    }
    
    # Ramp keywords
    RAMP_KEYWORDS = {
        'mana', 'land', 'search', 'expensive', 'big', 'ritual', 'ramp'
    }

    def __init__(self, oracle_df: pd.DataFrame):
        """Initialize with oracle DataFrame."""
        self.oracle_df = oracle_df.copy()
        self._preprocess_data()
    
    def _preprocess_data(self) -> None:
        """Preprocess the oracle data for analysis."""
        # Map column names to expected format (handle different naming conventions)
        column_mapping = {
            'Color': 'colors',
            'Type': 'type_line', 
            'Oracle Text': 'oracle_text',
            'CMC': 'cmc',
            'name': 'name'  # Keep as is
        }
        
        # Rename columns to standardized format
        for old_name, new_name in column_mapping.items():
            if old_name in self.oracle_df.columns and new_name != old_name:
                self.oracle_df.rename(columns={old_name: new_name}, inplace=True)
        
        # Ensure required columns exist after mapping
        required_cols = ['name', 'cmc', 'type_line', 'oracle_text', 'colors']
        for col in required_cols:
            if col not in self.oracle_df.columns:
                print(f"Warning: Creating missing column '{col}' with empty values")
                self.oracle_df[col] = ''
        
        # For compatibility with existing code, add mana_cost if it doesn't exist
        if 'mana_cost' not in self.oracle_df.columns:
            self.oracle_df['mana_cost'] = ''  # Not available in this dataset
        
        # Clean and normalize text data
        self.oracle_df['oracle_text'] = self.oracle_df['oracle_text'].fillna('').astype(str).str.lower()
        self.oracle_df['type_line'] = self.oracle_df['type_line'].fillna('').astype(str).str.lower()
        self.oracle_df['colors'] = self.oracle_df['colors'].fillna('').astype(str)
        
        # Convert CMC to numeric, handling non-numeric values
        self.oracle_df['cmc_numeric'] = pd.to_numeric(self.oracle_df['cmc'], errors='coerce').fillna(0)
        
        # Extract creature types
        self.oracle_df['creature_types'] = self.oracle_df['type_line'].apply(self._extract_creature_types)
        
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
            colors = self._parse_colors(card['colors'])  # Use mapped column name
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
                if creature_type in self.TRIBAL_TYPES:
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
            ('Equipment', self.EQUIPMENT_KEYWORDS, Archetype.MIDRANGE, create_equipment_scorer),
            ('Aggro', self.AGGRESSIVE_KEYWORDS, Archetype.AGGRO, create_aggressive_scorer),
            ('Control', self.CONTROL_KEYWORDS, Archetype.CONTROL, create_control_scorer),
            ('Ramp', self.RAMP_KEYWORDS, Archetype.RAMP, create_default_scorer),
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
        
        return self.oracle_df[self.oracle_df['colors'].apply(matches_colors)]
    
    def _count_keyword_cards(self, df: pd.DataFrame, keywords: Set[str]) -> int:
        """Count cards that contain any of the given keywords."""
        count = 0
        for _, card in df.iterrows():
            text = f"{card['oracle_text']} {card['type_line']}".lower()
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
    
    def extract_themes(self, min_cards_per_theme: int = 10) -> Dict[str, Dict[str, Any]]:
        """
        Extract all potential themes from the oracle data.
        
        Args:
            min_cards_per_theme: Minimum number of cards required for a theme
            
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
                creature_type = [k for k in theme['keywords'] if k in self.TRIBAL_TYPES][0]
                theme_name = f"{color_prefix} {creature_type.title()}s"
                all_themes[theme_name] = theme
            
            # Analyze keyword themes
            keyword_themes = self._analyze_keyword_themes(colors)
            for i, theme in enumerate(keyword_themes):
                # Determine theme name based on archetype
                archetype_names = {
                    Archetype.AGGRO: 'Aggro',
                    Archetype.CONTROL: 'Control', 
                    Archetype.MIDRANGE: 'Equipment',
                    Archetype.RAMP: 'Ramp'
                }
                theme_name = f"{color_prefix} {archetype_names.get(theme['archetype'], 'Theme')}"
                if theme_name not in all_themes:  # Avoid duplicates
                    all_themes[theme_name] = theme
            
            # Analyze CMC-based themes
            cmc_themes = self._analyze_cmc_themes(colors)
            for i, theme in enumerate(cmc_themes):
                archetype_name = 'Fast' if theme['archetype'] == Archetype.AGGRO else 'Big'
                theme_name = f"{color_prefix} {archetype_name}"
                if theme_name not in all_themes:
                    all_themes[theme_name] = theme
        
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


def extract_themes_from_oracle(oracle_df: pd.DataFrame, 
                              min_cards_per_theme: int = 10) -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to extract themes from oracle DataFrame.
    
    Args:
        oracle_df: DataFrame containing Magic card data
        min_cards_per_theme: Minimum cards required to generate a theme
        
    Returns:
        Dictionary of theme configurations in the same format as MONO_COLOR_THEMES
    """
    extractor = ThemeExtractor(oracle_df)
    return extractor.extract_themes(min_cards_per_theme)


def generate_theme_code(themes: Dict[str, Dict[str, Any]], 
                       variable_name: str = "EXTRACTED_THEMES") -> str:
    """
    Generate Python code for the extracted themes.
    
    Args:
        themes: Dictionary of theme configurations
        variable_name: Name for the generated variable
        
    Returns:
        Python code string that can be added to consts.py
    """
    lines = [f"{variable_name} = {{"]
    
    for theme_name, theme_config in themes.items():
        lines.append(f"    '{theme_name}': {{")
        lines.append(f"        'colors': {theme_config['colors']},")
        lines.append(f"        'strategy': '{theme_config['strategy']}',")
        lines.append(f"        'keywords': {theme_config['keywords']},")
        lines.append(f"        'archetype': Archetype.{theme_config['archetype'].name},")
        lines.append(f"        'scorer': {theme_config['scorer'].__name__},")
        lines.append(f"        'core_card_count': {theme_config['core_card_count']}")
        lines.append("    },")
    
    lines.append("}")
    return "\n".join(lines)