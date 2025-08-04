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
- **📊 Comprehensive Analysis**: Detailed reporting on deck composition and theme coherence
- **🚀 Auto-Download System**: Automatically downloads and caches MTG data - no manual setup required
- **📈 Performance Analysis**: In-depth deck performance evaluation with improvement suggestions
- **🏗️ Modular Architecture**: Clean, maintainable codebase with focused responsibilities

## Deck Themes

The system constructs 30 different themed decks across all colors:

### White Themes
- **White Soldiers**: Aggressive tribal deck focused on soldier creatures with anthem effects
- **White Equipment**: Equipment-based deck with efficient creatures and powerful gear  
- **White Angels**: Mid-to-late game deck with powerful flying angels and protection
- **White Vanguard**: Aggressive low-cost creatures with efficient stats and combat abilities

### Blue Themes  
- **Blue Flying**: Evasive creatures with flying and tempo spells
- **Blue Wizards**: Wizard tribal with spell-based synergies and card advantage
- **Blue Card Draw**: Card advantage engine with draw spells and library manipulation
- **Blue Tempo**: Efficient creatures with evasion and tempo spells for board control

### Black Themes
- **Black Zombies**: Zombie tribal with graveyard recursion and sacrifice synergies
- **Black Graveyard**: Graveyard-based value engine with recursion and reanimation  
- **Black Sacrifice**: Sacrifice-based deck with death triggers and value generation
- **Black Control**: Control deck with removal spells and efficient creatures for board control

### Red Themes
- **Red Goblins**: Fast goblin tribal with haste and explosive plays
- **Red Burn**: Direct damage spells and hasty creatures for quick wins
- **Red Inferno**: Expensive dragons with powerful effects and flying
- **Red Artifacts**: Artifact-based deck with improvise and metalcraft synergies

### Green Themes  
- **Green Elves**: Elf tribal with mana acceleration and creature synergies
- **Green Ramp**: Mana acceleration into large threats and expensive spells
- **Green Stompy**: Large creatures with trample and pump effects
- **Green Beasts**: Large beast creatures with powerful abilities

### Multicolor Themes
- **Azorius Control** (W/U): Control deck with counterspells, removal, card draw, and efficient win conditions
- **Dimir Mill** (U/B): Mill-based strategy with graveyard interaction and card advantage
- **Rakdos Aggro** (B/R): Aggressive deck with efficient creatures and direct damage  
- **Gruul Midrange** (R/G): Efficient midrange creatures with aggressive abilities and versatile spells
- **Selesnya Value** (G/W): Incremental advantage through efficient creatures, removal, and versatile utility spells
- **Orzhov Lifegain Value** (W/B): Incremental advantage through lifegain and card quality
- **Izzet Spells Matter** (U/R): Instant and sorcery synergies with prowess and spell-based creatures
- **Golgari Graveyard Value** (B/G): Graveyard-based value engine with recursion and sacrifice
- **Boros Equipment Aggro** (R/W): Aggressive creatures with equipment support and combat tricks  
- **Simic Ramp Control** (G/U): Ramp into large threats with card draw and protection

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
│   ├── construct/                    # Modular deck construction system
│   │   ├── __init__.py               # Main API and analysis functions
│   │   ├── builder.py                # Phase-based construction orchestrator  
│   │   ├── selector.py               # Card selection and scoring logic
│   │   ├── core.py                   # Data structures and constraints
│   │   └── utils.py                  # Card analysis utilities
│   ├── scorer/                       # Specialized theme scoring system
│   │   ├── __init__.py               # Scorer factory functions
│   │   ├── base.py                   # Base scorer classes
│   │   ├── rules.py                  # Individual scoring rules
│   │   └── scorer.py                 # Main scorer implementation
│   ├── oracle.py                     # Auto-download MTG data and card processing
│   ├── export.py                     # CSV export functionality
│   ├── validation.py                 # Deck validation and analysis
│   ├── balance.py                    # Deck performance and balance analysis
│   └── consts.py                     # Theme definitions and constants
├── jumpstart.ipynb                   # Main analysis notebook
├── pauper_cube_example_oracle.txt    # Example card list
└── pyproject.toml                    # Project dependencies
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
   uv run jupyter notebook jumpstart.ipynb
   ```

### 🚀 Auto-Download System

**No manual data setup required!** The system automatically handles MTG data:

- **First Run**: Downloads ~122MB MTG data from mtgjson.com (5-10 minutes)
- **Subsequent Runs**: Uses cached data instantly
- **Smart Caching**: Stores processed data in `.build/` directory
- **Always Current**: Fresh downloads get the latest MTG card data

The system downloads and processes:
1. `AllPrintings.json.zip` (122 MB) - Complete MTG database
2. `AllPrintings.json` (494 MB) - Extracted JSON data  
3. `cards.csv` (6.8 MB) - Processed CSV format for fast loading

To refresh data, simply delete the `.build/` directory and run again.

### Basic Usage

#### Quick Start - Build All Decks

```python
from jumpstart.src.construct import construct_jumpstart_decks, CardConstraints
from jumpstart.src.oracle import generate_oracle_csv
import pandas as pd

# Generate oracle with auto-download (first run downloads MTG data)
generate_oracle_csv('pauper_cube_example_oracle.txt', 'output/oracle_output.csv')

# Load processed card database
oracle_df = pd.read_csv('output/oracle_output.csv')

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
from jumpstart.src.construct import analyze_deck_composition, print_detailed_deck_analysis
analysis = analyze_deck_composition(deck_dataframes)
print_detailed_deck_analysis(deck_dataframes, analysis, constraints)
```

#### Performance Analysis

```python
# Generate comprehensive performance analysis
from jumpstart.src.balance import compute_all_deck_metrics
from jumpstart.src.consts import ALL_THEMES

# Calculate detailed performance metrics
metrics_df = compute_all_deck_metrics(deck_dataframes, ALL_THEMES)

# The system analyzes:
# - Speed & Consistency (mana curve efficiency)
# - Card Quality (power level assessment)  
# - Threat Density (win condition availability)
# - Interaction Quality (removal and answers)
# - Archetype Coherence (strategy alignment)
# - Overall Performance Score (weighted composite)

print("Top performing decks:")
print(metrics_df.nlargest(5, 'overall_performance'))
```

**Running with uv:**
```bash
# Run the notebook (auto-downloads MTG data on first run)
uv run jupyter notebook jumpstart.ipynb

# Or run Python scripts directly
uv run python your_script.py
```

#### Advanced Usage - Custom Constraints

```python
from jumpstart.src.construct import CardConstraints

# Custom constraints with detailed configuration
constraints = CardConstraints(
    target_deck_size=13,    # Cards per deck
    min_creatures=4,        # Minimum creatures per deck
    max_creatures=8,        # Maximum creatures per deck
    total_non_land=12,      # Maximum non-land cards per deck
    max_lands_mono=1,       # Lands for mono-color themes  
    max_lands_dual=1,       # Lands for dual-color themes
)

# Build decks with custom constraints
deck_dataframes = construct_jumpstart_decks(oracle_df, constraints=constraints)
```

#### Export Results

```python
from jumpstart.src.export import export_cube_to_csv

# Export decks to CSV with card database integration
export_cube_to_csv(deck_dataframes, 'output/my_jumpstart_cube.csv', oracle_df)
```

#### Validation and Analysis

```python
from jumpstart.src.validation import validate_jumpstart_cube, analyze_card_distribution
from jumpstart.src.consts import ALL_THEMES
from jumpstart.src.construct import CardConstraints

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
from jumpstart.src.consts import ALL_THEMES, MagicColor, MONO_COLOR_THEMES, DUAL_COLOR_THEMES

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

### Automated MTG Data Management

**Problem**: Manual data setup created barriers to entry and required technical knowledge of MTG data sources.

**Solution**: Intelligent auto-download system that:
- Downloads complete MTG database from mtgjson.com automatically
- Caches processed data for instant subsequent runs  
- Handles network errors and file corruption gracefully
- Provides clear progress feedback during downloads

**Results**: Zero-setup experience - users can start building cubes immediately without any manual data preparation.

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

### Comprehensive Performance Analysis

The system provides detailed performance evaluation for each deck:

**Performance Metrics:**
- **Speed & Consistency**: Mana curve analysis and game plan reliability
- **Card Quality**: Individual card power level assessment
- **Threat Density**: Win condition availability and pressure capability  
- **Interaction Quality**: Removal spells and answer availability
- **Archetype Coherence**: How well the deck follows its intended strategy
- **Overall Performance**: Weighted composite score for deck ranking

**Analysis Features:**
- Automated improvement suggestions for weak decks
- Balance assessment across all archetypes
- Exportable performance data for external analysis
- Visual dashboards showing performance comparisons

## Output Format

The system generates multiple analysis outputs:

### Deck Lists (`output/jumpstart_decks.csv`)
```csv
Name,Set,Collector Number,Rarity,Color Identity,Type,Mana Cost,CMC,Power,Toughness,Tags
Bonesplitter,Mixed,,common,,Artifact - Equipment,,1,,,White Equipment
Kor Skyfisher,Mixed,,common,W,Creature - Kor Soldier,,2,2.0,3.0,White Equipment
...
```

### Performance Analysis (`output/deck_performance_analysis.csv`)
```csv
theme,archetype,overall_performance,speed_score,card_quality,threat_density,interaction_score
White Soldiers,Aggro,3.245,4.2,2.8,0.65,0.15
Blue Control,Control,3.012,2.1,3.4,0.45,0.35
...
```

### Oracle Data (`output/oracle_output.csv`)
Processed card database with complete MTG data including power/toughness, oracle text, and color identity.

Each deck is tagged with its theme for easy identification and analysis.

## Contributing  

Contributions are welcome! The modular architecture makes it easy to:

- **Add new themes** in `src/consts.py`
- **Create specialized scorers** for new strategies in `src/scorer/`
- **Enhance the constraint system** in `src/construct/core.py`
- **Improve card analysis utilities** in `src/construct/utils.py`
- **Add performance metrics** in `src/balance.py`

### Development Setup

```bash
# Clone and setup
git clone https://github.com/vanonselenp/magic-jumpstart.git
cd magic-jumpstart
uv sync

# Run tests (if available)
uv run pytest

# Format code
uv run black jumpstart/src/
```

## Future Enhancements

💡 **Performance & Analysis:**
- Advanced synergy detection algorithms
- Mulligan probability calculations  
- Expected win rate modeling
- Matchup analysis between themes

💡 **Scoring Improvements:**
- PowerToughnessRatioRule: Score based on P/T efficiency
- ColorRequirementRule: Penalty for hard-to-cast cards  
- SynergyChainRule: Bonus for cards that work well together
- RarityBasedRule: Consider card rarity in limited environment
- MetagameRule: Adjust scores based on format considerations

💡 **Data & Integration:**
- EDHRec integration for synergy data
- Scryfall API integration for real-time card data
- Export formats for popular platforms (MTGO, Arena, etc.)
- Deck similarity analysis and clustering

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.