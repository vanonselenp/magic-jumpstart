from gradio import Markdown
import pandas as pd


def export_cube_to_csv(cube_df, oracle_df, filename=None):
    """
    Export the cube to a CSV file with the same structure as ThePauperCube.csv
    
    Parameters:
    - cube_df: The current cube dataframe
    - oracle_df: The oracle dataframe with card details
    - filename: Output filename (if None, generates timestamp-based name)
    """
    
    if filename is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"JumpstartCube_Export_{timestamp}.csv"
    
    print(f"Exporting cube to {filename}...")
    
    # Create export dataframe with proper structure
    export_data = []
    
    for _, card_row in cube_df.iterrows():
        card_name = card_row['Name']
        deck_name = card_row.get('Tags', '')
        
        # Find card details in oracle
        oracle_card = oracle_df[oracle_df['name'] == card_name]
        
        if oracle_card.empty:
            # Card not found in oracle, use cube data
            export_row = {
                'name': card_name,
                'CMC': card_row.get('CMC', ''),
                'Type': card_row.get('Type', ''),
                'Color': '',
                'Color Category': '',
                'Oracle Text': '',
                'tags': deck_name,  # Deck name goes in tags column
                'MTGO ID': '',
                'Power': '',
                'Toughness': ''
            }
        else:
            # Use oracle data
            oracle_row = oracle_card.iloc[0]
            export_row = {
                'name': card_name,
                'CMC': oracle_row.get('CMC', ''),
                'Type': oracle_row.get('Type', ''),
                'Color': oracle_row.get('Color', ''),
                'Color Category': oracle_row.get('Color Category', ''),
                'Oracle Text': oracle_row.get('Oracle Text', ''),
                'tags': deck_name,  # Deck name goes in tags column
                'MTGO ID': oracle_row.get('MTGO ID', ''),
                'Power': oracle_row.get('Power', ''),
                'Toughness': oracle_row.get('Toughness', '')
            }
        
        export_data.append(export_row)
    
    # Create dataframe and export
    export_df = pd.DataFrame(export_data)
    
    # Ensure column order matches ThePauperCube.csv
    column_order = ['name', 'CMC', 'Type', 'Color', 'Color Category', 'Oracle Text', 'tags', 'MTGO ID', 'Power', 'Toughness']
    export_df = export_df[column_order]
    
    # Export to CSV
    export_df.to_csv(filename, index=False)
    
    print(f"✅ Successfully exported {len(export_df)} cards to {filename}")
    
    # Show summary statistics
    deck_counts = export_df['tags'].value_counts()
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

def quick_export_cube(cube_df, oracle_df, filename=None):
    """Quick wrapper to export and display success message"""
    filename = export_cube_to_csv(cube_df, oracle_df, filename)
    print(Markdown(f"**File:** `{filename}`"))
    return filename

def validate_export(filename, original_cube_df):
    """Validate that the exported file matches the original cube"""
    
    try:
        # Read the exported file
        exported_df = pd.read_csv(filename)
        
        print(f"🔍 Validating export: {filename}")
        
        # Check card count
        original_count = len(original_cube_df)
        exported_count = len(exported_df)
        
        if original_count == exported_count:
            print(f"✅ Card count matches: {exported_count} cards")
        else:
            print(f"❌ Card count mismatch: Original {original_count}, Exported {exported_count}")
            return False
        
        # Check that all original cards are present
        original_cards = set(original_cube_df['Name'].tolist())
        exported_cards = set(exported_df['name'].tolist())
        
        missing_cards = original_cards - exported_cards
        extra_cards = exported_cards - original_cards
        
        if not missing_cards and not extra_cards:
            print("✅ All cards match between original and export")
        else:
            if missing_cards:
                print(f"❌ Missing cards in export: {list(missing_cards)[:5]}")
            if extra_cards:
                print(f"❌ Extra cards in export: {list(extra_cards)[:5]}")
            return False
        
        # Check deck assignments
        original_assignments = original_cube_df.set_index('Name')['Tags'].to_dict()
        exported_assignments = exported_df.set_index('name')['tags'].to_dict()
        
        mismatched_assignments = 0
        for card in original_cards:
            if card in exported_assignments:
                orig_deck = original_assignments.get(card, '')
                exp_deck = exported_assignments.get(card, '')
                if str(orig_deck) != str(exp_deck):
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