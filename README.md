**Note**: I wrote this as an experiment in learning how to vibe code. The end result came out better than I expected with a solution to a problem I had at the time. This was a fun experiment. 

# Magic: The Gathering Jumpstart Cube Constructor

An intelligent deck construction system for building themed Magic: The Gathering Jumpstart cubes with perfect theme coherence and balanced gameplay from a Pauper Cube. 

## Overview

This project automatically constructs 30 themed Jumpstart decks from a card pool, ensuring each deck has strong thematic identity while maintaining balanced gameplay. The system uses a sophisticated multi-phase algorithm with specialized scoring to create cohesive, playable decks.

see: [Pauper Jumpstart](https://cubecobra.com/cube/list/pauper-jumpstart-06-2025)

### Key Features

- **🎯 Theme-Aware Construction**: Advanced scoring system ensures decks match their intended themes
- **🔒 Core Card Reservation**: Guarantees theme-defining cards reach their intended decks
- **⚖️ Constraint Management**: Enforces deck building rules (creature limits, land ratios, etc.)
- **� Comprehensive Analysis**: Detailed reporting on deck composition and theme coherence
- **🏗️ Modular Architecture**: Clean, maintainable codebase with focused responsibilities

## Deck Themes

The system constructs 30 different themed decks across all colors:

### White Themes
- **White Soldiers**: Aggressive creature strategies with combat synergies
- **White Equipment**: Artifact equipment with creatures that benefit from them  
- **White Angels**: Flying creatures and divine magic
- **White Weenies**: Fast, low-cost aggressive creatures

### Blue Themes  
- **Blue Flying**: Aerial creatures and evasive strategies
- **Blue Wizards**: Spell-slinging with wizard tribal synergies
- **Blue Card Draw**: Card advantage and library manipulation
- **Blue Merfolk**: Merfolk tribal with tempo strategies

### Black Themes
- **Black Zombies**: Undead creatures with graveyard recursion
- **Black Graveyard**: Graveyard-as-resource strategies  
- **Black Sacrifice**: Sacrificial strategies for value
- **Black Vampires**: Vampire tribal with life drain

### Red Themes
- **Red Goblins**: Goblin tribal aggression
- **Red Burn**: Direct damage spells and aggressive creatures
- **Red Dragons**: Large flying threats and ramp
- **Red Artifacts**: Artifact creatures and synergies

### Green Themes  
- **Green Elves**: Elf tribal with mana acceleration
- **Green Ramp**: Large creatures enabled by mana acceleration
- **Green Stompy**: Aggressive creatures with pump spells
- **Green Beasts**: Beast tribal with large bodies

### Multicolor Themes
- **Azorius Control** (W/U): Control magic with card draw
- **Dimir Mill** (U/B): Library manipulation and graveyard value
- **Rakdos Aggro** (B/R): Fast, aggressive strategies  
- **Gruul Big Creatures** (R/G): Large creatures and ramp
- **Selesnya Tokens** (G/W): Token generation and wide strategies
- **Orzhov Lifedrain** (W/B): Life manipulation strategies
- **Izzet Spells Matter** (U/R): Instant/sorcery focused strategies
- **Golgari Graveyard Value** (B/G): Graveyard recursion and value
- **Boros Equipment Aggro** (R/W): Equipment-based aggressive strategies  
- **Simic Ramp Control** (G/U): Ramp into large threats with control elements

## How It Works

### Construction Algorithm

The system uses a **5-phase construction algorithm** to build optimal decks:

#### Phase 0: Core Card Reservation  
- Reserves theme-defining cards for each deck before general competition
- Ensures equipment reaches Equipment themes, tribal cards reach tribal themes, etc.
- **Critical innovation** that solved theme coherence problems

#### Phase 1: Multicolor Assignment
- Assigns multicolor cards to appropriate dual-color themes
- Prioritizes color requirements and theme relevance

#### Phase 2: General Assignment  
- Main construction phase using specialized scoring
- Assigns remaining cards based on theme compatibility

#### Phase 3: Completion
- Fills incomplete decks with best available cards
- Maintains constraints while maximizing deck size

#### Phase 4: Validation & Fixes
- Validates all constraint compliance  
- Fixes any violations (excess creatures/lands)

### Specialized Scoring System

Each theme uses **specialized scorers** for accurate card evaluation:

- **Equipment Scorer**: Prioritizes artifacts and creatures that benefit from equipment
- **Tribal Scorers**: Emphasize creature types and tribal synergies  
- **Aggressive Scorer**: Values low-cost creatures and combat tricks
- **Control Scorer**: Prioritizes card draw, removal, and win conditions

### Constraint System

The system enforces realistic deck building constraints:

- **Deck Size**: 13 cards per deck (390 cards total)
- **Creature Limit**: Maximum 9 creatures per deck  
- **Non-Land Limit**: Maximum 12 non-land cards per deck  
- **Land Limits**: 1 land per deck (mono and dual-color themes)
- **Card Uniqueness**: No card appears in multiple decks
- **Basic Lands**: Added separately during play (not part of the 13-card deck)

## Project Structure

```
jumpstart/
├── src/
│   ├── construct/           # Modular deck construction system
│   │   ├── __init__.py     # Main API and analysis functions
│   │   ├── builder.py      # Phase-based construction orchestrator  
│   │   ├── selector.py     # Card selection and scoring logic
│   │   ├── core.py         # Data structures and constraints
│   │   └── utils.py        # Card analysis utilities
│   ├── scorer/             # Specialized theme scoring system
│   │   ├── __init__.py     # Scorer factory functions
│   │   ├── base.py         # Base scorer classes
│   │   ├── rules.py        # Individual scoring rules
│   │   └── scorer.py       # Main scorer implementation
│   ├── export.py           # CSV export functionality
│   ├── validation.py       # Deck validation and analysis
│   └── consts.py          # Theme definitions and constants
├── jumpstart.ipynb        # Main analysis notebook
├── ThePauperCube_oracle_with_pt.csv  # Card database
└── jumpstart_decks.csv    # Generated deck output
```

## Getting Started

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vanonselenp/magic-jumpstart.git
   cd magic-jumpstart
   ```

2. **Set up Python environment with uv:**
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create virtual environment and install dependencies
   uv sync
   ```

3. **Launch Jupyter:**
   ```bash
   cd jumpstart
   uv run jupyter notebook jumpstart.ipynb
   ```

### Basic Usage

#### Quick Start - Build All Decks

```python
from src.construct import construct_jumpstart_decks, CardConstraints
import pandas as pd

# Load card database
oracle_df = pd.read_csv('ThePauperCube_oracle_with_pt.csv')

# Set up constraints  
constraints = CardConstraints(
    target_deck_size=13,
    total_non_land=12,  # All 12 cards should be non-lands
    max_lands_dual=1,
    max_lands_mono=1,
    max_creatures=9, 
)

# Build all decks
deck_dataframes = construct_jumpstart_decks(oracle_df, constraints=constraints)

# Analyze results
from src.construct import analyze_deck_composition, print_detailed_deck_analysis
analysis = analyze_deck_composition(deck_dataframes)
print_detailed_deck_analysis(deck_dataframes, analysis, constraints)
```

**Running with uv:**
```bash
# Run the notebook
uv run jupyter notebook jumpstart.ipynb

# Or run Python scripts directly
uv run python your_script.py
```

#### Advanced Usage - Custom Constraints

```python
from src.construct import CardConstraints

# Custom constraints with detailed configuration
constraints = CardConstraints(
    target_deck_size=13,    # Cards per deck
    total_non_land=12,      # Maximum non-land cards per deck
    max_lands_mono=1,       # Lands for mono-color themes  
    max_lands_dual=1,       # Lands for dual-color themes
    max_creatures=9,        # Max creatures per deck
)

# Build decks with custom constraints
deck_dataframes = construct_jumpstart_decks(oracle_df, constraints=constraints)
```

#### Export Results

```python
from src.export import export_cube_to_csv

# Export decks to CSV with card database integration
export_cube_to_csv(deck_dataframes, 'my_jumpstart_cube.csv', oracle_df)
```

#### Validation and Analysis

```python
from src.validation import validate_jumpstart_cube, analyze_card_distribution
from src.consts import ALL_THEMES
from src.construct import CardConstraints

constraints = CardConstraints(
    target_deck_size=13,    # Cards per deck
    total_non_land=12,      # Maximum non-land cards per deck
    max_lands_mono=1,       # Lands for mono-color themes  
    max_lands_dual=1,       # Lands for dual-color themes
    max_creatures=9,        # Max creatures per deck
)

# Comprehensive validation with proper parameters
validation_results = validate_jumpstart_cube(
    deck_dataframes, 
    oracle_df, 
    ALL_THEMES, 
    constraints
)

# Distribution analysis  
distribution = analyze_card_distribution(deck_dataframes, oracle_df, constraints)

# Check validation results
print("Overall valid:", validation_results['overall_valid'])
print("Card uniqueness:", validation_results['uniqueness']['valid'])
print("Constraint compliance:", validation_results['constraints']['valid'])
```

#### Working with Themes and Colors

```python
from src.consts import ALL_THEMES, MagicColor, MONO_COLOR_THEMES, DUAL_COLOR_THEMES

# Access all available themes
print("Total themes:", len(ALL_THEMES))
print("Mono-color themes:", len(MONO_COLOR_THEMES))
print("Dual-color themes:", len(DUAL_COLOR_THEMES))

# Work with the MagicColor enum
print("All colors:", MagicColor.all_colors())  # ['W', 'U', 'B', 'R', 'G']
print("Color names:", MagicColor.color_names())  # {'W': 'White', 'U': 'Blue', ...}
print("Basic lands:", MagicColor.basic_land_names())  # {'W': 'plains', 'U': 'island', ...}

# Example: Check theme colors
theme = ALL_THEMES['White Soldiers']
print(f"White Soldiers colors: {theme['colors']}")  # [MagicColor.WHITE.value]
print(f"Strategy: {theme['strategy']}")
```

## Algorithm Innovations

### Core Card Reservation System

The **Core Card Reservation System** was a critical breakthrough that solved theme coherence issues:

**Problem**: Original algorithm allowed other themes to claim theme-defining cards before the intended theme could access them.

**Solution**: Phase 0 reserves the most important cards for each theme before general competition begins.

**Results**: White Equipment theme improved from 0 equipment cards to 5 equipment cards, with theme coherence jumping from 50% to ~90%.

### Specialized Scoring Integration  

Each theme uses purpose-built scorers that understand the specific strategies:

- **Equipment themes** prioritize artifacts and creatures that benefit from equipment
- **Tribal themes** emphasize creature types and tribal payoffs
- **Control themes** value card draw, removal, and win conditions  
- **Aggressive themes** prioritize low costs and combat effectiveness

## Output Format

The system generates a CSV file with complete deck information:

```csv
Name,Set,Collector Number,Rarity,Color Identity,Type,Mana Cost,CMC,Power,Toughness,Tags
Bonesplitter,Mixed,,common,,Artifact - Equipment,,1,,,White Equipment
Kor Skyfisher,Mixed,,common,W,Creature - Kor Soldier,,2,2.0,3.0,White Equipment
...
```

Each deck is tagged with its theme for easy identification and analysis.

## Contributing  

Contributions are welcome! The modular architecture makes it easy to:

- Add new themes in `consts.py`
- Create specialized scorers for new strategies
- Enhance the constraint system
- Improve card analysis utilities

## Future Enhancements

💡 **Potential improvements:**
- PowerToughnessRatioRule: Score based on P/T efficiency
- ColorRequirementRule: Penalty for hard-to-cast cards  
- SynergyChainRule: Bonus for cards that work well together
- RarityBasedRule: Consider card rarity in limited environment
- MetagameRule: Adjust scores based on format considerations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.