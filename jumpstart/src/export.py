from gradio import Markdown
import pandas as pd


def export_cube_to_csv(deck_dataframes, filename=None):
    """
    Export the jumpstart cube to a CSV file with the same structure as JumpstartCube_ThePauperCube_ULTIMATE_Final.csv
    
    Parameters:
    - deck_dataframes: Dictionary mapping theme names to their deck DataFrames
    - filename: Output filename (if None, generates timestamp-based name)
    """
    
    if filename is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"JumpstartCube_Export_{timestamp}.csv"
    
    print(f"Exporting jumpstart cube to {filename}...")
    
    # Create export dataframe with proper structure
    export_data = []
    
    for theme_name, deck_df in deck_dataframes.items():
        if deck_df.empty:
            continue
            
        for _, card_row in deck_df.iterrows():
            # Map from oracle_df columns to export format
            card_name = card_row['name']
            
            # Create export row matching JumpstartCube_ThePauperCube_ULTIMATE_Final.csv structure
            export_row = {
                'Name': card_name,
                'Set': 'Mixed',  # Default to 'Mixed' like in the original file
                'Collector Number': '',  # Not available in oracle_df
                'Rarity': 'common',  # Default to 'common' like in the original file
                'Color Identity': card_row.get('Color', ''),
                'Type': card_row.get('Type', ''),
                'Mana Cost': '',  # Not available in oracle_df
                'CMC': card_row.get('CMC', ''),
                'Power': card_row.get('Power', ''),
                'Toughness': card_row.get('Toughness', ''),
                'Tags': theme_name  # Use theme name as the deck tag
            }
            
            export_data.append(export_row)
    
    # Create dataframe and export
    export_df = pd.DataFrame(export_data)
    
    # Ensure column order matches JumpstartCube_ThePauperCube_ULTIMATE_Final.csv
    column_order = ['Name', 'Set', 'Collector Number', 'Rarity', 'Color Identity', 'Type', 'Mana Cost', 'CMC', 'Power', 'Toughness', 'Tags']
    export_df = export_df[column_order]
    
    # Export to CSV
    export_df.to_csv(filename, index=False)
    
    print(f"✅ Successfully exported {len(export_df)} cards to {filename}")
    
    # Show summary statistics
    deck_counts = export_df['Tags'].value_counts()
    print(f"\n📊 Export Summary:")
    print(f"Total cards: {len(export_df)}")
    print(f"Number of decks: {len(deck_counts)}")
    
    if len(deck_counts) > 0:
        print(f"\nDeck breakdown:")
        for deck, count in deck_counts.head(10).items():
            if deck and deck.strip():
                print(f"  {deck}: {count} cards")
        
        if len(deck_counts) > 10:
            print(f"  ... and {len(deck_counts) - 10} more decks")
    
    return filename

def quick_export_cube(deck_dataframes, filename=None):
    """Quick wrapper to export jumpstart cube and display success message"""
    filename = export_cube_to_csv(deck_dataframes, filename)
    print(Markdown(f"**File:** `{filename}`"))
    return filename

def validate_export(filename, deck_dataframes):
    """Validate that the exported file matches the original deck dataframes"""
    
    try:
        # Read the exported file
        exported_df = pd.read_csv(filename)
        
        print(f"🔍 Validating export: {filename}")
        
        # Calculate expected counts
        expected_count = sum(len(deck_df) for deck_df in deck_dataframes.values())
        exported_count = len(exported_df)
        
        if expected_count == exported_count:
            print(f"✅ Card count matches: {exported_count} cards")
        else:
            print(f"❌ Card count mismatch: Expected {expected_count}, Exported {exported_count}")
            return False
        
        # Check that all cards are present
        expected_cards = set()
        for deck_df in deck_dataframes.values():
            if not deck_df.empty:
                expected_cards.update(deck_df['name'].tolist())
        
        exported_cards = set(exported_df['Name'].tolist())
        
        missing_cards = expected_cards - exported_cards
        extra_cards = exported_cards - expected_cards
        
        if not missing_cards and not extra_cards:
            print("✅ All cards match between original and export")
        else:
            if missing_cards:
                print(f"❌ Missing cards in export: {list(missing_cards)[:5]}")
            if extra_cards:
                print(f"❌ Extra cards in export: {list(extra_cards)[:5]}")
            return False
        
        # Check deck assignments
        expected_assignments = {}
        for theme_name, deck_df in deck_dataframes.items():
            if not deck_df.empty:
                for card_name in deck_df['name']:
                    expected_assignments[card_name] = theme_name
        
        exported_assignments = exported_df.set_index('Name')['Tags'].to_dict()
        
        mismatched_assignments = 0
        for card in expected_cards:
            if card in exported_assignments:
                expected_theme = expected_assignments.get(card, '')
                exported_theme = exported_assignments.get(card, '')
                if str(expected_theme) != str(exported_theme):
                    mismatched_assignments += 1
        
        if mismatched_assignments == 0:
            print("✅ All deck assignments match")
        else:
            print(f"❌ {mismatched_assignments} deck assignment mismatches")
            return False
        
        print(f"✅ Export validation successful! {filename} is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False