**Note**: I wrote this as an experiment in learning how to vibe code. The end result came out better than I expected with a solution to a problem I had at the time. This was a fun experiment. 

# Magic: The Gathering Jumpstart Cube Constructor

An intelligent deck construction system for building themed Magic: The Gathering Jumpstart cubes with perfect theme coherence and balanced gameplay from any card pool. The system features automated theme extraction, balanced color distribution, and comprehensive performance analysis.

## Overview

This project automatically constructs themed Jumpstart decks from a card pool, ensuring each deck has strong thematic identity while maintaining balanced gameplay. The system uses sophisticated multi-phase algorithms with specialized scoring, automated theme extraction, and intelligent color balancing to create cohesive, playable cubes.

see: [Pauper Jumpstart](https://cubecobra.com/cube/list/pauper-jumpstart-06-2025)

### Key Features

- **🤖 Automated Theme Extraction**: AI-powered analysis discovers themes from any card pool automatically
- **⚖️ Balanced Color Distribution**: Ensures equal representation across all Magic colors (20% each)
- **🎯 Theme-Aware Construction**: Advanced scoring system ensures decks match their intended themes
- **🔒 Core Card Reservation**: Guarantees theme-defining cards reach their intended decks
- **📏 Constraint Management**: Enforces deck building rules (creature limits, land ratios, etc.)
- **📊 Comprehensive Analysis**: Detailed reporting on deck composition and theme coherence
- **🚀 Auto-Download System**: Automatically downloads and caches MTG data - no manual setup required
- **📈 Performance Analysis**: In-depth deck performance evaluation with improvement suggestions
- **🏗️ Modular Architecture**: Clean, maintainable codebase with focused responsibilities
- **🎨 Guild Theme Support**: Automatic detection and inclusion of dual-color guild strategies

## Automated Theme Discovery

The system can automatically extract themes from any card pool using advanced keyword analysis and machine learning techniques:

### Theme Extraction Features

- **🔍 Intelligent Keyword Detection**: Analyzes card text for thematic patterns and synergies
- **🎭 Multi-Level Theme Analysis**: Discovers tribal, mechanical, and strategic themes
- **🌈 Balanced Color Selection**: Ensures perfect 20% distribution across all five Magic colors
- **⚙️ Configurable Parameters**: Adjustable minimum card requirements and diversity weights
- **🎯 Guild Integration**: Automatic detection of dual-color guild strategies
- **📊 Quality Scoring**: Ranks themes by buildability and coherence

### Supported Theme Types

- **Tribal Themes**: Elves, Goblins, Zombies, Angels, Wizards, Soldiers, etc.
- **Mechanical Themes**: Equipment, Artifacts, Spells Matter, Graveyard, etc.
- **Strategic Themes**: Aggro, Control, Ramp, Burn, Mill, etc.
- **Guild Themes**: Azorius Control, Simic Ramp, Rakdos Aggro, etc.

## Example Deck Themes

The system can construct decks from discovered themes or use predefined themes:

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
│   ├── theme_extraction/             # Automated theme discovery system
│   │   ├── __init__.py               # Theme extraction API
│   │   ├── extractor.py              # Main theme extraction engine
│   │   ├── keywords.py               # Keyword databases and pattern matching
│   │   └── utils.py                  # Theme formatting and code generation
│   ├── balance/                      # Performance analysis and metrics
│   │   ├── __init__.py               # Balance analysis API
│   │   ├── metrics.py                # Performance metric calculations
│   │   ├── archetypes.py             # Archetype-specific analysis
│   │   └── utils.py                  # Analysis utilities
│   ├── oracle.py                     # Auto-download MTG data and card processing
│   ├── export.py                     # CSV export functionality
│   ├── validation.py                 # Deck validation and analysis
│   ├── generate.py                   # Main cube generation orchestrator
│   └── consts.py                     # Theme definitions and constants
├── jumpstart.ipynb                   # Main analysis notebook with comprehensive examples
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

#### Automated Theme Extraction and Balanced Selection

```python
# Extract themes automatically from your card pool
from jumpstart.src.theme_extraction.extractor import ThemeExtractor
from jumpstart.src.oracle import generate_oracle_csv
import pandas as pd

# Generate oracle with auto-download (first run downloads MTG data)
generate_oracle_csv('your_card_list.txt', 'output/oracle_output.csv')
oracle_df = pd.read_csv('output/oracle_output.csv')

# Extract themes with balanced color distribution
extractor = ThemeExtractor(oracle_df)
all_themes = extractor.extract_themes(
    min_cards_per_theme=10, 
    include_guilds=True  # Include dual-color guild themes
)

# Generate summary of discovered themes
print(extractor.generate_theme_summary(all_themes))

# Select optimal themes with perfect color balance
selected_themes = extractor.select_optimal_themes(
    themes=all_themes,
    mono_count=20,  # 20 mono-color themes (4 per color)
    dual_count=10,  # 10 dual-color guild themes  
    prioritize_buildability=True,
    diversity_weight=0.7
)

# Verify perfect color balance
color_distribution = extractor.analyze_color_distribution(selected_themes)
print("Color balance ratio:", color_distribution['balance_ratio'])  # Should be 1.00
```

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

# Build all decks using discovered themes (or predefined ALL_THEMES)
deck_dataframes = construct_jumpstart_decks(
    oracle_df, 
    constraints=constraints,
    themes=selected_themes  # Use extracted themes or ALL_THEMES
)

# Analyze results
from jumpstart.src.construct import analyze_deck_composition, print_detailed_deck_analysis
analysis = analyze_deck_composition(deck_dataframes)
print_detailed_deck_analysis(deck_dataframes, analysis, constraints)
```

#### Comprehensive Performance Analysis

```python
# Generate comprehensive performance analysis with improvement suggestions
from jumpstart.src.balance import compute_all_deck_metrics
from jumpstart.src.consts import ALL_THEMES

# Calculate detailed performance metrics across 8 dimensions
def calculate_deck_performance_metrics(deck_df, theme_name, oracle_df):
    """
    Calculates comprehensive performance metrics including:
    - Speed & Consistency (mana curve efficiency)
    - Card Quality (power level assessment)  
    - Threat Density (win condition availability)
    - Interaction Quality (removal and answers)
    - Mana Efficiency (cost-to-impact ratio)
    - Late Game Power (expensive threats)
    - Archetype Coherence (strategy alignment)
    - Overall Performance Score (weighted composite)
    """
    # ... comprehensive analysis implementation

# Analyze all decks with performance scoring
performance_data = []
for theme_name, deck_df in deck_dataframes.items():
    metrics = calculate_deck_performance_metrics(deck_df, theme_name, oracle_df)
    performance_data.append(metrics)

performance_df = pd.DataFrame(performance_data)

# Generate improvement suggestions for weak decks
def generate_improvement_suggestions(deck_name, metrics, deck_df):
    """
    Provides specific actionable suggestions like:
    - ⚡ SPEED: Reduce average CMC - add more 1-2 mana cards
    - 👊 THREATS: Add more win conditions - need creatures with 3+ power
    - 🛡️ INTERACTION: Add removal spells or counterspells
    - 🎯 FOCUS: Better align cards with archetype strategy
    """
    # ... intelligent suggestion generation

print("Top performing decks:")
print(performance_df.nlargest(5, 'overall_performance'))

# Export comprehensive analysis
performance_df.to_csv('output/deck_performance_analysis.csv')
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

### Automated Theme Extraction System

**Problem**: Manual theme definition required deep MTG knowledge and was time-consuming for custom card pools.

**Solution**: AI-powered theme extraction that:
- Analyzes card text for thematic keywords and patterns
- Groups cards by tribal, mechanical, and strategic synergies  
- Scores theme quality and buildability automatically
- Discovers both obvious and subtle thematic connections
- Generates properly formatted theme dictionaries for construction

**Results**: Users can build themed cubes from any card pool without manually defining themes, while maintaining high theme coherence.

### Balanced Color Distribution

**Problem**: Random theme selection could create color imbalances (e.g., 6 white themes, 2 black themes).

**Solution**: Intelligent selection algorithm that:
- Ensures exactly 20% representation for each Magic color (W, U, B, R, G)
- Maintains quality-based selection within color constraints
- Balances mono-color themes equally (4 per color for 20 themes)
- Handles dual-color guild distribution intelligently

**Results**: Perfect color balance with 1.00 balance ratio, ensuring fair gameplay across all color combinations.

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

The system provides detailed performance evaluation and improvement recommendations:

**Performance Metrics:**
- **Speed & Consistency**: Mana curve analysis and game plan reliability
- **Card Quality**: Individual card power level assessment using rarity and efficiency
- **Threat Density**: Win condition availability and pressure capability  
- **Interaction Quality**: Removal spells and answer availability
- **Mana Efficiency**: Cost-to-impact ratio analysis
- **Late Game Power**: Expensive threat evaluation
- **Archetype Coherence**: How well the deck follows its intended strategy
- **Overall Performance**: Weighted composite score for deck ranking

**Analysis Features:**
- Automated improvement suggestions for weak decks (e.g., "⚡ SPEED: Reduce average CMC", "👊 THREATS: Add win conditions")
- Balance assessment across all archetypes with statistical analysis
- Exportable performance data for external analysis (`deck_performance_analysis.csv`)
- Visual dashboards showing performance comparisons and radar charts
- Detailed CMC curve analysis with archetype-specific coloring
- Category leaders identification (fastest, most consistent, highest quality, etc.)

**Smart Recommendations**: The system analyzes each deck's weaknesses and provides specific actionable suggestions like adding early-game cards, improving threat density, or enhancing archetype focus.

## Output Format

The system generates multiple analysis outputs:

### Deck Lists (`output/jumpstart_decks.csv`)
```csv
Name,Set,Collector Number,Rarity,Color Identity,Type,Mana Cost,CMC,Power,Toughness,Tags
Bonesplitter,Mixed,,common,,Artifact - Equipment,,1,,,White Equipment
Kor Skyfisher,Mixed,,common,W,Creature - Kor Soldier,,2,2.0,3.0,White Equipment
...
```

### Oracle Data (`output/oracle_output.csv`)
Processed card database with complete MTG data including power/toughness, oracle text, and color identity.

### Performance Analysis (`output/deck_performance_analysis.csv`)
```csv
theme,archetype,overall_performance,speed_score,card_quality,threat_density,interaction_score,mana_efficiency,late_game_power,archetype_coherence
White Soldiers,Aggro,3.245,4.2,2.8,0.65,0.15,1.2,0.1,0.85
Blue Control,Control,3.012,2.1,3.4,0.45,0.35,0.9,0.3,0.75
Red Goblins,Aggro,3.156,4.5,2.5,0.70,0.10,1.1,0.05,0.90
...
```

### Theme Extraction Results (`output/keyword_refinement_summary.csv`)
Analysis of discovered themes with keyword density and buildability scores.

Each deck is tagged with its theme for easy identification and analysis.

## Contributing  

Contributions are welcome! The modular architecture makes it easy to:

- **Add new themes** in `src/consts.py` or use automated theme extraction
- **Create specialized scorers** for new strategies in `src/scorer/`
- **Enhance the constraint system** in `src/construct/core.py`
- **Improve card analysis utilities** in `src/construct/utils.py`
- **Add performance metrics** in `src/balance/`
- **Extend theme extraction** with new keyword patterns in `src/theme_extraction/`

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

💡 **Theme Extraction & AI:**
- Advanced synergy detection using card interaction patterns
- Machine learning models for theme quality prediction
- Natural language processing for flavor-based theme discovery
- Community-driven theme validation and rating system

💡 **Performance & Analysis:**
- Mulligan probability calculations with opening hand simulation
- Expected win rate modeling based on deck composition
- Matchup analysis between themes with statistical modeling
- Meta-game adaptation for different play environments

💡 **Balance & Optimization:**
- Genetic algorithms for optimal theme selection
- Dynamic constraint adjustment based on card pool characteristics  
- Multi-objective optimization balancing fun, power, and diversity
- A/B testing framework for cube iterations

💡 **Data & Integration:**
- EDHRec integration for community synergy data
- Scryfall API integration for real-time card data and pricing
- Export formats for popular platforms (MTGO, Arena, Cockatrice, etc.)
- Deck similarity analysis and clustering for meta-analysis
- Integration with cube draft simulators for playtesting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.