"""
Individual scoring rules for card evaluation.

Each rule focuses on a specific aspect of card scoring and can be easily
tested, modified, or disabled independently.
"""

import re
from .base import ScoringRule, CardContext


class KeywordMatchingRule(ScoringRule):
    """Rule for basic keyword matching in card text."""
    
    def __init__(self):
        super().__init__("Keyword Matching", "Base scoring from keyword matches in card text")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return True  # Always applies
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        score = 0.0
        keywords = theme_config['keywords']
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in card_context.searchable_text:
                # Use regex for precise word boundary matching
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', card_context.searchable_text):
                    score += 1.0
                elif keyword_lower in card_context.searchable_text:
                    score += 0.5
        
        return score


class ArchetypeManaCurveRule(ScoringRule):
    """Rule for archetype-specific mana curve preferences."""
    
    def __init__(self):
        super().__init__("Archetype Mana Curve", "CMC bonuses/penalties based on archetype")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return theme_config.get('archetype') in ['Aggro', 'Control', 'Midrange']
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        archetype = theme_config.get('archetype', '')
        cmc = card_context.cmc
        
        if archetype == 'Aggro':
            if cmc == 1:
                return 2.0  # Big bonus for 1-drops
            elif cmc == 2:
                return 1.0  # Good bonus for 2-drops
            elif cmc >= 4:
                return -1.0  # Penalty for expensive cards
        
        elif archetype == 'Control':
            if cmc >= 4:
                return 0.5  # Bonus for expensive cards
            elif cmc == 1:
                return -0.5  # Small penalty for 1-drops
        
        elif archetype == 'Midrange':
            if 2 <= cmc <= 4:
                return 1.0  # Bonus for 2-4 CMC cards
            elif cmc == 1:
                return -0.5  # Penalty for too aggressive
            elif cmc >= 5:
                return -1.0  # Penalty for too expensive
        
        return 0.0


class SpecificKeywordRule(ScoringRule):
    """Rule for context-sensitive keyword matching."""
    
    def __init__(self):
        super().__init__("Specific Keywords", "Context-aware keyword bonuses")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        keywords = theme_config['keywords']
        return any(kw in keywords for kw in ['cheap', 'efficient', 'low cost', 'small'])
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        keywords = theme_config['keywords']
        score = 0.0
        
        if 'cheap' in keywords and card_context.cmc <= 2:
            score += 1.0
        
        if 'efficient' in keywords and 'creature' in card_context.card_type:
            if card_context.power > 0 and card_context.cmc > 0:
                if card_context.power >= card_context.cmc:
                    score += 1.0
                elif card_context.power >= card_context.cmc - 1:
                    score += 0.5
        
        if 'low cost' in keywords and card_context.cmc <= 2:
            score += 1.0
        
        if 'small' in keywords and 'creature' in card_context.card_type:
            if card_context.power <= 2:
                score += 0.5
        
        return score


class TypeBasedRule(ScoringRule):
    """Rule for card type bonuses."""
    
    def __init__(self):
        super().__init__("Type-Based", "Bonuses for specific card types matching theme focus")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return True  # Always check type bonuses
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        keywords = theme_config['keywords']
        score = 0.0
        
        if 'creature' in card_context.card_type:
            if any(kw in keywords for kw in ['creature', 'tribal', 'aggressive']):
                score += 0.3
        
        if 'instant' in card_context.card_type or 'sorcery' in card_context.card_type:
            if any(kw in keywords for kw in ['instant', 'sorcery', 'spells', 'burn', 'counter']):
                score += 0.3
        
        return score


class ArtifactRule(ScoringRule):
    """Rule for artifact and equipment bonuses."""
    
    def __init__(self):
        super().__init__("Artifact/Equipment", "Special bonuses for artifacts and equipment")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return 'artifact' in card_context.card_type
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        keywords = theme_config['keywords']
        score = 0.0
        
        # Base artifact bonus
        if any(kw in keywords for kw in ['artifact', 'equipment', 'metalcraft']):
            score += 0.5
        
        # Special equipment bonuses
        if 'equipment' in card_context.card_type:
            score += 2.0  # Strong bonus for actual equipment
            if 'living weapon' in card_context.oracle_text:
                score += 1.0  # Extra bonus for living weapon
        
        return score


class EquipmentCreatureRule(ScoringRule):
    """Rule for evaluating creatures in equipment themes."""
    
    def __init__(self):
        super().__init__("Equipment Creatures", "Evaluate creatures as equipment carriers")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return ('equipment' in theme_config['keywords'] and 
                'creature' in card_context.card_type)
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        score = 0.0
        
        # Evasion bonus
        evasion_keywords = ['flying', 'shadow', 'unblockable', 'menace', 'trample']
        if any(kw in card_context.oracle_text for kw in evasion_keywords):
            score += 1.0
        
        # Combat abilities bonus
        combat_keywords = ['first strike', 'double strike', 'vigilance', 'lifelink']
        if any(kw in card_context.oracle_text for kw in combat_keywords):
            score += 0.5
        
        # Efficient carrier bonus
        if (card_context.power > 0 and 
            card_context.toughness > 0 and 
            card_context.toughness <= 3):
            score += 0.5
        
        # Penalty for non-attackers
        if card_context.power == 0 or 'defender' in card_context.oracle_text:
            score -= 1.0
        
        return score


class TribalSynergyRule(ScoringRule):
    """Rule for enhanced tribal synergy scoring."""
    
    def __init__(self):
        super().__init__("Tribal Synergy", "Bonus for cards that care about creature types")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        # Apply to themes with tribal keywords
        tribal_indicators = ['soldier', 'elf', 'goblin', 'zombie', 'human', 'tribal']
        return any(indicator in theme_config['keywords'] for indicator in tribal_indicators)
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        score = 0.0
        
        # Check for tribal-caring text
        tribal_text_patterns = [
            'other', 'creatures you control', 'creature of the chosen type',
            'creatures of the same type', '+1/+1 counter', 'anthem effect'
        ]
        
        for pattern in tribal_text_patterns:
            if pattern in card_context.oracle_text:
                score += 0.5
        
        # Extra bonus if card mentions specific creature types from theme
        theme_keywords = [kw.lower() for kw in theme_config['keywords']]
        creature_types = ['soldier', 'elf', 'goblin', 'zombie', 'human', 'wizard', 'knight']
        
        for creature_type in creature_types:
            if creature_type in theme_keywords and creature_type in card_context.oracle_text:
                score += 1.0  # Strong bonus for mentioning the tribal type
        
        return score


class PowerToughnessRatioRule(ScoringRule):
    """Rule for evaluating power/toughness efficiency."""
    
    def __init__(self):
        super().__init__("P/T Efficiency", "Bonuses for efficient power/toughness ratios")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return ('creature' in card_context.card_type and 
                card_context.power > 0 and 
                card_context.toughness > 0 and
                card_context.cmc > 0)
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        """Score based on total stats vs CMC."""
        total_stats = card_context.power + card_context.toughness
        cmc = card_context.cmc
        
        # Good creatures typically have total P+T >= 2*CMC
        if total_stats >= 2 * cmc + 1:
            return 1.0  # Excellent stats
        elif total_stats >= 2 * cmc:
            return 0.5  # Good stats
        elif total_stats >= 2 * cmc - 1:
            return 0.0  # Acceptable stats
        else:
            return -0.5  # Poor stats for cost


class ColorRequirementRule(ScoringRule):
    """Rule for penalizing difficult-to-cast cards."""
    
    def __init__(self):
        super().__init__("Color Requirements", "Penalties for hard-to-cast multicolor cards")
    
    def applies(self, card_context: CardContext, theme_config: dict) -> bool:
        return True  # Always check casting costs
    
    def score(self, card_context: CardContext, theme_config: dict) -> float:
        # This is a placeholder - would need mana cost parsing to implement fully
        # For now, just penalize very high CMC cards in mono-color themes
        theme_colors = theme_config.get('colors', [])
        
        if len(theme_colors) == 1 and card_context.cmc >= 6:
            return -0.5  # Penalty for expensive cards in mono-color
        
        return 0.0
