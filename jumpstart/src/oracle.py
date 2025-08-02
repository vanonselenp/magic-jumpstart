
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
    # Column mapping from output to source
    COLUMN_MAPPING = {
        'name': 'name',
        'CMC': 'manaValue',
        'Type': 'type',
        'Color': 'colors',  # Use colors for the Color column
        'Color Category': 'colorIdentity',  # Use colorIdentity for Color Category
        'Oracle Text': 'text',
        'tags': 'tags',
        'MTGO ID': 'MTGO ID',
        'Power': 'power',
        'Toughness': 'toughness'
    }
    
    # Load data
    card_names = _load_card_names(card_list_file)
    all_cards_df = _prepare_cards_dataframe(all_cards_csv)
    
    # Process each card
    rows = []
    for name in card_names:
        card_match = _find_card_match(all_cards_df, name)
        if card_match is not None:
            row = _extract_card_data(card_match, COLUMN_MAPPING)
        else:
            row = _create_blank_card_row(name, COLUMN_MAPPING)
            print(f"Card '{name}' not found in all cards CSV.")
        rows.append(row)
    
    # Save results
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(f"Oracle CSV generated: {output_csv}")


def _load_card_names(card_list_file):
    """Load and return list of card names from file."""
    with open(card_list_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def _prepare_cards_dataframe(all_cards_csv):
    """Load and prepare the cards dataframe with lowercase columns for matching."""
    df = pd.read_csv(all_cards_csv, dtype=str)
    
    # Create lowercase matching columns
    df['name_lower'] = df['name'].str.lower()
    df['name_firstpart_lower'] = df['name'].str.split(' // ').str[0].str.lower()
    
    if 'faceName' in df.columns:
        df['faceName_lower'] = df['faceName'].str.lower()
    else:
        df['faceName_lower'] = ''
    
    return df


def _find_card_match(df, card_name):
    """Find a card match using multiple strategies."""
    name_lower = card_name.lower()
    
    # Try different matching strategies in order of preference
    for column in ['faceName_lower', 'name_firstpart_lower', 'name_lower']:
        matches = df[df[column] == name_lower]
        if not matches.empty:
            return matches.iloc[0]
    
    return None


def _extract_card_data(card_row, column_mapping):
    """Extract card data using the column mapping."""
    row = {}
    for output_col, source_col in column_mapping.items():
        if source_col in card_row.index:
            row[output_col] = _process_column_value(output_col, card_row[source_col], card_row)
        else:
            row[output_col] = ''
    return row


def _process_column_value(column_name, value, card_row=None):
    """Process column values based on their type."""
    if column_name == 'CMC':
        if pd.isnull(value):
            return 0
        return int(float(value)) if value else 0
    elif column_name == 'Color':
        # Special case: Lands should have empty/null Color to match legacy format
        if card_row is not None and 'Land' in str(card_row.get('type', '')):
            return ''
        
        # Special case: if Color column is empty but we have colorIdentity, use that
        if (pd.isnull(value) or not str(value).strip()) and card_row is not None:
            if 'colorIdentity' in card_row.index and pd.notna(card_row['colorIdentity']):
                value = card_row['colorIdentity']
        # Handle null/nan values for Color
        if pd.isnull(value) or str(value).lower() == 'nan':
            return ''
        # Convert "W, U" -> "WU" for the Color column
        return ''.join(str(value).replace(' ', '').split(','))
    elif column_name == 'Color Category':
        # Always process Color Category, even if value is null
        return _convert_colors_to_category(value, card_row)
    elif column_name == 'name':
        # Split on "//" and use the left entry (for double-faced cards)
        return str(value).split(' // ')[0]
    else:
        # For all other columns, handle nulls
        if pd.isnull(value):
            return ''
        return value


def _convert_colors_to_category(color_value, card_row=None):
    """Convert color codes to descriptive category names."""
    # Check if this is a land card first
    if card_row is not None and 'Land' in str(card_row.get('type', '')):
        return 'Lands'
    
    # Handle null/empty values
    if pd.isnull(color_value) or not str(color_value).strip() or str(color_value).lower() == 'nan':
        return 'Colorless'
    
    # Clean up the color value (remove spaces, etc.)
    clean_colors = ''.join(str(color_value).replace(' ', '').split(','))
    
    # If empty after cleaning
    if not clean_colors:
        return 'Colorless'
    
    # Single colors
    if len(clean_colors) == 1:
        color_map = {
            'W': 'White',
            'U': 'Blue', 
            'B': 'Black',
            'R': 'Red',
            'G': 'Green'
        }
        return color_map.get(clean_colors, 'Colorless')
    
    # Multiple colors - check if it might be hybrid
    elif len(clean_colors) > 1:
        # For now, treat all multicolor as "Multicolored"
        # Note: The legacy data seems to have "Hybrid" for some specific cases
        # but without more context about what makes a card "Hybrid" vs "Multicolored",
        # we'll use "Multicolored" for consistency
        return 'Multicolored'
    
    return 'Colorless'


def _create_blank_card_row(card_name, column_mapping):
    """Create a blank row for cards that weren't found."""
    row = {col: '' for col in column_mapping.keys()}
    row['name'] = card_name
    row['CMC'] = 0
    return row
