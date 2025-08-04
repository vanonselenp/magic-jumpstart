
import os
import pandas as pd
import requests
import zipfile
import json
from pathlib import Path

def generate_oracle_csv(card_list_file, output_csv, build_dir='.build'):
    """
    Generate an oracle CSV for a list of cards.
    Automatically downloads and caches MTG data if not present.
    
    Args:
        card_list_file (str): Path to file with newline-separated card names.
        output_csv (str): Path to output CSV file.
        build_dir (str): Directory to cache downloaded data (default: '.build').
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
    
    # Ensure we have the cards data
    all_cards_csv = _ensure_cards_data(build_dir)
    
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


def _ensure_cards_data(build_dir):
    """
    Ensure MTG cards data is available, downloading if necessary.
    Returns the path to the cards CSV file.
    """
    build_path = Path(build_dir)
    build_path.mkdir(exist_ok=True)
    
    # Define file paths
    zip_file = build_path / "AllPrintings.json.zip"
    json_file = build_path / "AllPrintings.json"
    csv_file = build_path / "cards.csv"
    
    # Check if CSV already exists
    if csv_file.exists():
        print(f"Using cached cards data: {csv_file}")
        return str(csv_file)
    
    # Check if JSON exists, if not download and extract
    if not json_file.exists():
        if not zip_file.exists():
            print("Downloading MTG data from mtgjson.com...")
            _download_mtg_data(zip_file)
        
        print("Extracting MTG data...")
        _extract_zip_file(zip_file, build_path)
    
    # Convert JSON to CSV
    print("Converting JSON to CSV format...")
    _convert_json_to_csv(json_file, csv_file)
    
    return str(csv_file)


def _download_mtg_data(zip_file_path):
    """Download the MTG data ZIP file from mtgjson.com."""
    url = "https://mtgjson.com/api/v5/AllPrintings.json.zip"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading... {percent:.1f}%%", end='', flush=True)
        
        print(f"\nDownload complete: {zip_file_path}")
        
    except requests.RequestException as e:
        raise Exception(f"Failed to download MTG data: {e}")


def _extract_zip_file(zip_file_path, extract_path):
    """Extract the ZIP file to the specified directory."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"Extraction complete: {extract_path}")
        
    except zipfile.BadZipFile as e:
        raise Exception(f"Failed to extract ZIP file: {e}")


def _convert_json_to_csv(json_file_path, csv_file_path):
    """Convert the AllPrintings.json to a cards CSV format."""
    try:
        print("Loading JSON data...")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Processing card data...")
        cards = []
        
        # Extract cards from all sets
        for set_code, set_data in data['data'].items():
            if 'cards' in set_data:
                for card in set_data['cards']:
                    # Only include the fields we need
                    card_data = {
                        'name': card.get('name', ''),
                        'manaValue': card.get('manaValue', 0),
                        'type': card.get('type', ''),
                        'colors': ','.join(card.get('colors', [])),
                        'colorIdentity': ','.join(card.get('colorIdentity', [])),
                        'text': card.get('text', ''),
                        'power': card.get('power', ''),
                        'toughness': card.get('toughness', ''),
                        'setCode': set_code,
                        'faceName': card.get('faceName', ''),
                        'tags': '',  # Not available in MTGJSON, leaving empty
                        'MTGO ID': ''  # Not available in MTGJSON, leaving empty
                    }
                    cards.append(card_data)
        
        print(f"Creating CSV with {len(cards)} cards...")
        df = pd.DataFrame(cards)
        
        # Remove duplicates, keeping the most recent printing
        df = df.drop_duplicates(subset=['name'], keep='last')
        
        df.to_csv(csv_file_path, index=False)
        print(f"CSV created: {csv_file_path} ({len(df)} unique cards)")
        
    except (json.JSONDecodeError, KeyError) as e:
        raise Exception(f"Failed to process JSON data: {e}")
    except Exception as e:
        raise Exception(f"Failed to convert JSON to CSV: {e}")


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
