
import os
import pandas as pd

def generate_oracle_csv(card_list_file, all_cards_csv, output_csv):
    """
    Generate an oracle CSV for a list of cards.
    Args:
        card_list_file (str): Path to file with newline-separated card names.
        all_cards_csv (str): Path to AllPrintingsCSVFiles/cards.csv.
        output_csv (str): Path to output CSV file.
    """
    # Mapping of output columns to source columns
    mapping = {
        'name': 'name',
        'CMC': 'manaValue',
        'Type': 'type',
        'Color': 'colors',
        'Color Category': 'colorIdentity',
        'Oracle Text': 'text',  # mapping from 'text' in source
        'tags': 'tags',
        'MTGO ID': 'MTGO ID',
        'Power': 'power',
        'Toughness': 'toughness'
    }
    # Read card list
    with open(card_list_file, 'r', encoding='utf-8') as f:
        card_names = [line.strip() for line in f if line.strip()]
    # Read all cards CSV
    all_cards_df = pd.read_csv(all_cards_csv, dtype=str)
    # Map 'text' to 'Oracle Text' for easier selection
    if 'text' in all_cards_df.columns:
        all_cards_df['Oracle Text'] = all_cards_df['text']
    # Enhanced matching: try faceName, then first part of name split by ' // ', then full name
    all_cards_df['name_lower'] = all_cards_df['name'].str.lower()
    if 'faceName' in all_cards_df.columns:
        all_cards_df['faceName_lower'] = all_cards_df['faceName'].str.lower()
    else:
        all_cards_df['faceName_lower'] = ''
    all_cards_df['name_firstpart_lower'] = all_cards_df['name'].str.split(' // ').str[0].str.lower()

    rows = []
    for name in card_names:
        name_lc = name.lower()
        # Try faceName first
        matches = all_cards_df[all_cards_df['faceName_lower'] == name_lc]
        # If not found, try first part of name split by ' // '
        if matches.empty:
            matches = all_cards_df[all_cards_df['name_firstpart_lower'] == name_lc]
        # If still not found, try full name
        if matches.empty:
            matches = all_cards_df[all_cards_df['name_lower'] == name_lc]
        if not matches.empty:
            row = {}
            for out_col, src_col in mapping.items():
                if src_col in matches.columns:
                    if out_col == 'CMC':
                        row[out_col] = int(float(matches.iloc[0][src_col])) if pd.notnull(matches.iloc[0][src_col]) else 0
                    elif out_col in ('Color Category', 'Color'):
                        val = matches.iloc[0][src_col]
                        if pd.isnull(val):
                            row[out_col] = ''
                        else:
                            # Split on ',' and join with '' (e.g., 'W, U' -> 'WU')
                            row[out_col] = ''.join(str(val).replace(' ', '').split(','))
                    else:
                        row[out_col] = matches.iloc[0][src_col]
                else:
                    row[out_col] = ''
            rows.append(row)
        else:
            # Card not found, fill with blanks
            row = {out_col: '' for out_col in mapping}
            row['name'] = name
            row['CMC'] = 0
            rows.append(row)
            print(f"Card '{name}' not found in all cards CSV.")
    out_df = pd.DataFrame(rows)
    out_df.to_csv(output_csv, index=False)
    print(f"Oracle CSV generated: {output_csv}")
