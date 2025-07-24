"""
Validation functions for jumpstart cube construction.

This module contains functions to validate deck construction results,
check for constraint compliance, and analyze card distribution.
"""

# from src.validation import (
#     validate_card_uniqueness,      # Check for duplicate cards
#     validate_deck_constraints,     # Check deck building rules  
#     analyze_card_distribution,     # Analyze card usage patterns
#     validate_jumpstart_cube,       # Run all validations
#     display_validation_summary     # Show formatted results
# )

import pandas as pd
from typing import Dict, List, Tuple, Optional

from src.construct.core import CardConstraints


def validate_card_uniqueness(deck_dataframes: Dict[str, pd.DataFrame]) -> Dict:
    """
    Validate that no card appears in multiple decks.
    
    Args:
        deck_dataframes: Dictionary mapping theme names to their deck DataFrames
    
    Returns:
        dict: Validation results with duplicates info
    """
    
    print("🔍 VALIDATING CARD UNIQUENESS")
    print("=" * 50)
    
    # Track all cards and where they appear
    card_usage = {}  # card_name -> list of themes using it
    total_cards = 0
    
    # Collect all cards from all decks
    for theme_name, deck_df in deck_dataframes.items():
        if deck_df.empty:
            continue
            
        total_cards += len(deck_df)
        
        for _, card in deck_df.iterrows():
            card_name = card['name']
            
            if card_name not in card_usage:
                card_usage[card_name] = []
            
            card_usage[card_name].append(theme_name)
    
    # Find duplicates
    duplicates = {card: themes for card, themes in card_usage.items() if len(themes) > 1}
    unique_cards = len([card for card, themes in card_usage.items() if len(themes) == 1])
    
    print(f"📊 VALIDATION RESULTS:")
    print(f"Total cards across all decks: {total_cards}")
    print(f"Unique cards used: {unique_cards}")
    print(f"Duplicate cards found: {len(duplicates)}")
    
    if duplicates:
        print(f"\n❌ DUPLICATE CARDS DETECTED:")
        for card_name, themes in duplicates.items():
            print(f"  '{card_name}' appears in: {', '.join(themes)}")
        
        # Count how many extra cards we have due to duplicates
        extra_cards = sum(len(themes) - 1 for themes in duplicates.values())
        print(f"\nTotal duplicate instances: {extra_cards}")
        
        return {
            'valid': False,
            'total_cards': total_cards,
            'unique_cards': unique_cards,
            'duplicates': duplicates,
            'duplicate_count': len(duplicates),
            'extra_instances': extra_cards
        }
    else:
        print(f"\n✅ VALIDATION PASSED!")
        print(f"All {unique_cards} cards are used exactly once.")
        
        return {
            'valid': True,
            'total_cards': total_cards,
            'unique_cards': unique_cards,
            'duplicates': {},
            'duplicate_count': 0,
            'extra_instances': 0
        }


def validate_deck_constraints(deck_dataframes: Dict[str, pd.DataFrame], all_themes: Dict, constraints: CardConstraints) -> Dict:
    """
    Validate that all deck construction constraints are met.
    
    Args:
        deck_dataframes: Dictionary mapping theme names to their deck DataFrames
        all_themes: Dictionary of all theme configurations
        constraints: CardConstraints object defining the deck building rules
    
    Returns:
        dict: Validation results for constraints
    """
    
    print("🔍 VALIDATING DECK CONSTRAINTS")
    print("=" * 50)
    
    constraint_violations = []
    valid_decks = 0
    
    for theme_name, deck_df in deck_dataframes.items():
        if deck_df.empty:
            continue
            
        theme_config = all_themes.get(theme_name, {})
        theme_colors = theme_config.get('colors', [])
        is_mono_color = len(theme_colors) == 1
        
        # Count card types
        creatures = deck_df[deck_df['Type'].str.contains('Creature', case=False, na=False)]
        lands = deck_df[deck_df['Type'].str.contains('Land', case=False, na=False)]
        
        # Get unique land names
        unique_lands = lands['name'].nunique() if not lands.empty else 0
        
        # Check constraints using CardConstraints object
        violations = []
        
        # Creature limit
        if len(creatures) > constraints.max_creatures:
            violations.append(f"Too many creatures: {len(creatures)}/{constraints.max_creatures}")
        
        # Land limit
        max_lands = constraints.get_max_lands(is_mono_color)
        if unique_lands > max_lands:
            violations.append(f"Too many unique lands: {unique_lands}/{max_lands}")
        
        # Deck size
        if len(deck_df) != constraints.target_deck_size:
            violations.append(f"Wrong deck size: {len(deck_df)}/{constraints.target_deck_size}")
        
        if violations:
            constraint_violations.append({
                'theme': theme_name,
                'violations': violations,
                'creatures': len(creatures),
                'unique_lands': unique_lands,
                'deck_size': len(deck_df)
            })
        else:
            valid_decks += 1
    
    total_decks = len([df for df in deck_dataframes.values() if not df.empty])
    
    print(f"📊 CONSTRAINT VALIDATION RESULTS:")
    print(f"Valid decks: {valid_decks}/{total_decks}")
    print(f"Constraint violations: {len(constraint_violations)}")
    
    if constraint_violations:
        print(f"\n❌ CONSTRAINT VIOLATIONS:")
        for violation in constraint_violations:
            print(f"  {violation['theme']}:")
            for v in violation['violations']:
                print(f"    - {v}")
    else:
        print(f"\n✅ ALL CONSTRAINTS SATISFIED!")
    
    return {
        'valid': len(constraint_violations) == 0,
        'valid_decks': valid_decks,
        'total_decks': total_decks,
        'violations': constraint_violations
    }


def analyze_card_distribution(deck_dataframes: Dict[str, pd.DataFrame], oracle_df: pd.DataFrame) -> Dict:
    """
    Analyze how cards are distributed across decks and themes.
    
    Args:
        deck_dataframes: Dictionary mapping theme names to their deck DataFrames
        oracle_df: DataFrame with all available cards
    
    Returns:
        dict: Analysis results
    """
    
    print("\n📈 CARD DISTRIBUTION ANALYSIS")
    print("=" * 50)
    
    # Get all used cards
    all_used_cards = set()
    for deck_df in deck_dataframes.values():
        if not deck_df.empty:
            all_used_cards.update(deck_df['name'].tolist())
    
    total_available = len(oracle_df)
    total_used = len(all_used_cards)
    unused_count = total_available - total_used
    
    print(f"📊 OVERALL STATISTICS:")
    print(f"Total cards available: {total_available}")
    print(f"Total cards used: {total_used}")
    print(f"Cards unused: {unused_count}")
    print(f"Usage rate: {total_used/total_available*100:.1f}%")
    
    # Analyze by color
    print(f"\n🎨 USAGE BY COLOR:")
    color_stats = {}
    
    for color in ['W', 'U', 'B', 'R', 'G', 'C']:
        color_cards = oracle_df[oracle_df['Color'] == color] if color != 'C' else oracle_df[oracle_df['Color'].isna() | (oracle_df['Color'] == '')]
        available = len(color_cards)
        
        used_in_color = sum(1 for card_name in all_used_cards 
                           if card_name in color_cards['name'].values)
        
        if available > 0:
            usage_pct = used_in_color / available * 100
            color_name = {'W': 'White', 'U': 'Blue', 'B': 'Black', 
                         'R': 'Red', 'G': 'Green', 'C': 'Colorless'}[color]
            print(f"  {color_name:9}: {used_in_color:3d}/{available:3d} cards ({usage_pct:5.1f}%)")
            color_stats[color] = {'used': used_in_color, 'available': available, 'rate': usage_pct}
    
    # Analyze deck completeness
    print(f"\n🎯 DECK COMPLETENESS:")
    complete_decks = 0
    incomplete_decks = []
    
    for theme_name, deck_df in deck_dataframes.items():
        deck_size = len(deck_df)
        if deck_size == 13:
            complete_decks += 1
        elif deck_size > 0:
            incomplete_decks.append((theme_name, deck_size))
    
    print(f"Complete decks (13 cards): {complete_decks}")
    print(f"Incomplete decks: {len(incomplete_decks)}")
    
    if incomplete_decks:
        print(f"\nIncomplete deck details:")
        for theme, size in incomplete_decks:
            print(f"  {theme}: {size}/13 cards")
    
    # Analyze unused cards by type
    if unused_count > 0:
        print(f"\n📋 UNUSED CARDS ANALYSIS:")
        
        used_card_names = set(all_used_cards)
        unused_cards = oracle_df[~oracle_df['name'].isin(used_card_names)]
        
        # Group unused by type
        unused_creatures = unused_cards[unused_cards['Type'].str.contains('Creature', case=False, na=False)]
        unused_lands = unused_cards[unused_cards['Type'].str.contains('Land', case=False, na=False)]
        unused_spells = unused_cards[~unused_cards['Type'].str.contains('Creature|Land', case=False, na=False)]
        
        print(f"Unused creatures: {len(unused_creatures)}")
        print(f"Unused lands: {len(unused_lands)}")
        print(f"Unused spells: {len(unused_spells)}")
        
        # Show some examples of unused cards
        if len(unused_cards) > 0:
            print(f"\nSample unused cards:")
            for _, card in unused_cards.head(10).iterrows():
                print(f"  • {card['name']} ({card['Type']}) - {card['Color']}")
    
    return {
        'total_available': total_available,
        'total_used': total_used,
        'unused_count': unused_count,
        'usage_rate': total_used/total_available,
        'color_stats': color_stats,
        'complete_decks': complete_decks,
        'incomplete_decks': incomplete_decks
    }


def validate_jumpstart_cube(deck_dataframes: Dict[str, pd.DataFrame], oracle_df: pd.DataFrame, all_themes: Dict) -> Dict:
    """
    Comprehensive validation of the entire jumpstart cube construction.
    
    Args:
        deck_dataframes: Dictionary mapping theme names to their deck DataFrames
        oracle_df: DataFrame with all available cards
        all_themes: Dictionary of all theme configurations
    
    Returns:
        dict: Complete validation results
    """
    print("🎯 COMPREHENSIVE JUMPSTART CUBE VALIDATION")
    print("=" * 60)
    
    # Create constraints object
    constraints = CardConstraints()
    
    # Run all validations
    uniqueness_result = validate_card_uniqueness(deck_dataframes)
    constraint_result = validate_deck_constraints(deck_dataframes, all_themes, constraints)
    distribution_result = analyze_card_distribution(deck_dataframes, oracle_df)
    
    # Overall validation status
    overall_valid = uniqueness_result['valid'] and constraint_result['valid']
    
    print(f"\n🏆 OVERALL VALIDATION RESULT:")
    if overall_valid:
        print(f"✅ JUMPSTART CUBE CONSTRUCTION SUCCESSFUL!")
        print(f"All constraints satisfied, no violations detected.")
    else:
        print(f"❌ JUMPSTART CUBE CONSTRUCTION HAS ISSUES")
        print(f"Please review the violations above.")
    
    return {
        'overall_valid': overall_valid,
        'uniqueness': uniqueness_result,
        'constraints': constraint_result,
        'distribution': distribution_result
    }


def display_validation_summary(validation_results: Dict):
    """
    Display a formatted summary of validation results.
    
    Args:
        validation_results: Results from validate_jumpstart_cube()
    """
    
    print("\n📋 VALIDATION SUMMARY")
    print("=" * 40)
    
    # Card uniqueness
    uniqueness = validation_results['uniqueness']
    print(f"Card Uniqueness: {'✅ PASS' if uniqueness['valid'] else '❌ FAIL'}")
    print(f"  Total cards used: {uniqueness['total_cards']}")
    print(f"  Unique cards: {uniqueness['unique_cards']}")
    print(f"  Duplicates: {uniqueness['duplicate_count']}")
    
    # Constraints
    constraints = validation_results['constraints']
    print(f"\nDeck Constraints: {'✅ PASS' if constraints['valid'] else '❌ FAIL'}")
    print(f"  Valid decks: {constraints['valid_decks']}/{constraints['total_decks']}")
    print(f"  Violations: {len(constraints['violations'])}")
    
    # Distribution
    distribution = validation_results['distribution']
    print(f"\nCard Distribution:")
    print(f"  Usage rate: {distribution['usage_rate']*100:.1f}%")
    print(f"  Complete decks: {distribution['complete_decks']}")
    print(f"  Incomplete decks: {len(distribution['incomplete_decks'])}")
    
    # Overall
    print(f"\nOverall Result: {'✅ SUCCESS' if validation_results['overall_valid'] else '❌ NEEDS WORK'}")
