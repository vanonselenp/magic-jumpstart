"""
Jumpstart deck construction module.

This module provides a modular approach to constructing Magic: The Gathering
Jumpstart decks with proper theme coherence and constraint satisfaction.

The module is organized into several focused components:
- core: Core data structures (CardConstraints, DeckState)  
- utils: Card utility functions (type checking, color analysis)
- selector: CardSelector for finding and scoring candidate cards
- builder: DeckBuilder orchestrator for the main construction phases

Main entry point is the DeckBuilder class which implements a phase-based
construction algorithm:
0. Core card reservation (ensures theme coherence)
1. Multicolor cards (for dual-color themes)  
2. General card assignment
3. Completion phase
4. Constraint validation and fixes
5. Optional reorganization for incomplete decks
"""

from .core import CardConstraints, DeckState
from .selector import CardSelector  
from .builder import DeckBuilder
from .utils import (
    is_land_card,
    is_creature_card,
    can_land_produce_colors,
    get_card_colors,
    get_card_type_display,
    score_land_for_dual_colors
)

# Import analysis functions for backward compatibility
import pandas as pd
from typing import Dict, List


def analyze_deck_composition(decks_df: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    """Analyze the composition of constructed decks."""
    analysis = {}
    
    for theme_name, deck_df in decks_df.items():
        if deck_df.empty:
            analysis[theme_name] = {
                'total_cards': 0,
                'creatures': 0,
                'lands': 0,
                'other_spells': 0,
                'colors': [],
                'avg_cmc': 0.0
            }
            continue
        
        # Basic counts
        creatures = deck_df[deck_df['Type'].str.contains('Creature', case=False, na=False)]
        lands = deck_df[deck_df['Type'].str.contains('Land', case=False, na=False)]
        other_spells = deck_df[~deck_df['Type'].str.contains('Creature|Land', case=False, na=False)]
        
        # Color analysis
        colors = set()
        for _, card in deck_df.iterrows():
            if pd.notna(card.get('mana_cost', '')):
                mana_cost = str(card['mana_cost'])
                if 'W' in mana_cost: colors.add('W')
                if 'U' in mana_cost: colors.add('U')  
                if 'B' in mana_cost: colors.add('B')
                if 'R' in mana_cost: colors.add('R')
                if 'G' in mana_cost: colors.add('G')
        
        # CMC analysis
        cmcs = []
        for _, card in deck_df.iterrows():
            cmc = card.get('cmc', 0)
            if pd.notna(cmc) and isinstance(cmc, (int, float)):
                cmcs.append(float(cmc))
        
        analysis[theme_name] = {
            'total_cards': len(deck_df),
            'creatures': len(creatures),
            'lands': len(lands), 
            'other_spells': len(other_spells),
            'colors': sorted(list(colors)),
            'avg_cmc': sum(cmcs) / len(cmcs) if cmcs else 0.0
        }
    
    return analysis


def print_detailed_deck_analysis(decks_df: Dict[str, pd.DataFrame], analysis: Dict[str, Dict]):
    """Print detailed analysis of all constructed decks."""
    print("\n" + "="*60)
    print("DETAILED DECK ANALYSIS")
    print("="*60)
    
    complete_decks = 0
    total_cards_used = 0
    
    for theme_name in sorted(analysis.keys()):
        deck_analysis = analysis[theme_name]
        total_cards = deck_analysis['total_cards']
        
        print(f"\n🎯 {theme_name.upper()}")
        print("-" * 40)
        
        if total_cards == 0:
            print("❌ No cards assigned")
            continue
        
        # Status
        if total_cards == 13:
            complete_decks += 1
            status = "✅ COMPLETE"
        else:
            status = f"⚠️  INCOMPLETE ({total_cards}/13)"
        
        print(f"Status: {status}")
        total_cards_used += total_cards
        
        # Composition
        print(f"Creatures: {deck_analysis['creatures']}")
        print(f"Lands: {deck_analysis['lands']}")
        print(f"Other Spells: {deck_analysis['other_spells']}")
        print(f"Colors: {', '.join(deck_analysis['colors']) if deck_analysis['colors'] else 'Colorless'}")
        print(f"Avg CMC: {deck_analysis['avg_cmc']:.1f}")
        
        # Show actual cards if deck exists
        if theme_name in decks_df and not decks_df[theme_name].empty:
            deck_df = decks_df[theme_name]
            print("\nCards in deck:")
            for _, card in deck_df.iterrows():
                card_type = str(card['Type'])
                if len(card_type) > 25:
                    card_type = card_type[:22] + "..."
                print(f"  • {card['name']:<30} {card_type}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Complete decks: {complete_decks}/30")
    print(f"Total cards used: {total_cards_used}")
    
    if complete_decks == 30:
        print("\n🎉 SUCCESS! All jumpstart decks completed!")
    else:
        incomplete_count = 30 - complete_decks
        print(f"\n⚠️  {incomplete_count} decks still need completion.")


# Main construction function for backward compatibility
def construct_jumpstart_decks(oracle_df, constraints=None):
    """
    Construct all jumpstart decks using the modular deck builder.
    
    This is the main entry point that maintains backward compatibility
    with the original construct.py interface.
    
    Args:
        oracle_df (pd.DataFrame): Card database with oracle information
        constraints (CardConstraints, optional): Deck building constraints
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping theme names to deck DataFrames
    """
    builder = DeckBuilder(oracle_df, constraints)
    return builder.build_all_decks()

__all__ = [
    # Main classes
    'DeckBuilder',
    'CardSelector', 
    'CardConstraints',
    'DeckState',
    
    # Utility functions
    'is_land_card',
    'is_creature_card', 
    'can_land_produce_colors',
    'get_card_colors',
    'get_card_type_display',
    'score_land_for_dual_colors',
    
    # Main entry point
    'construct_jumpstart_decks',
    
    # Analysis functions
    'analyze_deck_composition',
    'print_detailed_deck_analysis'
]
