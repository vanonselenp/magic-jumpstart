"""Keyword definitions for Magic: The Gathering theme detection.

This module contains all the keyword sets used for detecting various
Magic archetypes and strategies in card text analysis.
"""

from typing import Set

# Common tribal creature types
TRIBAL_TYPES = {
    'soldier', 'wizard', 'goblin', 'elf', 'zombie', 'angel', 'dragon', 
    'beast', 'bird', 'cat', 'dog', 'human', 'vampire', 'werewolf',
    'knight', 'warrior', 'rogue', 'cleric', 'shaman', 'druid',
    'sliver', 'eldrazi', 'pirate', 'merfolk', 'faerie', 'ninja'
}

# Equipment and artifact keywords
EQUIPMENT_KEYWORDS = {
    'equipment', 'equip', 'equipped', 'attach', 'metalcraft', 'artifact',
    'sword', 'blade', 'armor', 'weapon', 'improvise', 'construct', 'servo'
}

# Aggressive keywords
AGGRESSIVE_KEYWORDS = {
    'haste', 'first strike', 'double strike', 'menace', 'aggressive',
    'attack', 'combat', 'burn', 'damage', 'rush', 'charge'
}

# Control keywords
CONTROL_KEYWORDS = {
    'counter', 'destroy', 'exile', 'remove', 'control', 'draw',
    'scry', 'flying', 'vigilance', 'lifelink', 'protection'
}

# Ramp keywords
RAMP_KEYWORDS = {
    'mana', 'land', 'search', 'expensive', 'big', 'ritual', 'ramp'
}

# Tempo keywords
TEMPO_KEYWORDS = {
    'bounce', 'return', 'tap', 'counter', 'flash', 'cheap', 'efficient',
    'draw', 'cantrip', 'pressure', 'disrupt', 'tempo'
}

# Combo keywords
COMBO_KEYWORDS = {
    'combo', 'synergy', 'enters', 'sacrifice', 'triggered', 'ability',
    'when', 'whenever', 'cost reduction', 'infinite', 'untap', 'activated'
}

# Voltron keywords (single creature focus)
VOLTRON_KEYWORDS = {
    'aura', 'enchant', 'attach', 'equipped', 'gets +', 'hexproof',
    'protection', 'indestructible', 'unblockable', 'trample', 'enchantment'
}

# Aristocrats keywords (sacrifice/death matters)
ARISTOCRATS_KEYWORDS = {
    'sacrifice', 'dies', 'death', 'creature dies', 'when.*dies',
    'blood artist', 'drain', 'token', 'creature token', 'etb', 'leaves'
}

# Graveyard keywords
GRAVEYARD_KEYWORDS = {
    'graveyard', 'return', 'flashback', 'escape', 'delve', 'threshold',
    'mill', 'self-mill', 'dredge', 'reanimator', 'from.*graveyard'
}

# Burn/Direct Damage keywords
BURN_KEYWORDS = {
    'damage', 'burn', 'shock', 'bolt', 'deals.*damage', 'ping',
    'direct damage', 'face damage', 'player', 'target.*player'
}

# Spellslinger keywords
SPELLSLINGER_KEYWORDS = {
    'instant', 'sorcery', 'prowess', 'spell', 'cast', 'magecraft',
    'storm', 'copy', 'fork', 'noncreature spell'
}

# Lifegain keywords
LIFEGAIN_KEYWORDS = {
    'lifegain', 'gain.*life', 'lifelink', 'soul sister', 'soul warden',
    'when.*gain.*life', 'life total', 'life you gained', 'whenever.*gain.*life'
}

# Token keywords
TOKEN_KEYWORDS = {
    'token', 'create.*token', 'creature token', 'artifact token',
    'populate', 'convoke', 'go wide', 'amass', 'fabricate'
}

# Enchantments matter keywords
ENCHANTMENTS_KEYWORDS = {
    'enchantment', 'constellation', 'enchantress', 'aura', 'enchant',
    'enchantments matter', 'when.*enchantment.*enters'
}

# +1/+1 Counters keywords
COUNTERS_KEYWORDS = {
    'counter', '+1/+1', 'modular', 'evolve', 'proliferate', 'graft',
    'adapt', 'monstrosity', 'renown', 'outlast', 'bolster'
}

# Mill/Self-Mill keywords
MILL_KEYWORDS = {
    'mill', 'library', 'top.*library', 'bottom.*library', 'self-mill',
    'surveil', 'look.*top', 'cards.*library'
}

# Landfall keywords
LANDFALL_KEYWORDS = {
    'landfall', 'land.*enters', 'whenever.*land', 'land drop',
    'lands matter', 'additional land', 'extra land'
}

# Cycling keywords
CYCLING_KEYWORDS = {
    'cycling', 'cycle', 'discard.*draw', 'whenever.*cycle',
    'cycling matters', 'astral slide', 'lightning rift'
}

# Madness keywords
MADNESS_KEYWORDS = {
    'madness', 'discard', 'whenever.*discard', 'hellbent',
    'empty hand', 'no cards in hand', 'graveyard size'
}

# Midrange keywords (efficient threats + card advantage + interaction)
MIDRANGE_KEYWORDS = {
    'efficient', 'value', 'threat', 'removal', 'interaction', 'versatile',
    'good stats', 'card advantage', 'flexible', 'balanced', 'quality',
    'solid', 'reasonable', 'enters.*battlefield', 'when.*enters'
}

# Vehicles keywords
VEHICLES_KEYWORDS = {
    'vehicle', 'crew', 'pilot', 'artifact creature', 'becomes.*creature',
    'crewed', 'manning'
}

# Planeswalkers keywords
PLANESWALKERS_KEYWORDS = {
    'planeswalker', 'loyalty', 'superfriends', 'planeswalkers matter',
    'whenever.*planeswalker', 'loyalty counter'
}

# Historic keywords (artifacts, legendaries, sagas)
HISTORIC_KEYWORDS = {
    'historic', 'legendary', 'artifact', 'saga', 'historic spell',
    'artifacts.*legendaries.*sagas'
}

# Kicker keywords
KICKER_KEYWORDS = {
    'kicker', 'kicked', 'additional cost', 'multikicker', 'entwine',
    'modal', 'choose.*mode', 'if.*kicked'
}

# Multicolor/Domain keywords
MULTICOLOR_KEYWORDS = {
    'multicolored', 'domain', 'converge', 'sunburst', 'basic land types',
    'different.*colors', 'five colors', 'rainbow'
}

# Blink/ETB Value keywords
BLINK_KEYWORDS = {
    'blink', 'flicker', 'exile.*return', 'enters.*battlefield',
    'etb', 'leaves.*battlefield', 'when.*enters', 'triggered ability'
}

# Sacrifice keywords (distinct from aristocrats)
SACRIFICE_KEYWORDS = {
    'sacrifice', 'sac', 'as.*additional.*cost', 'devour', 'exploit',
    'emerge', 'offering', 'altar'
}

# Storm keywords
STORM_KEYWORDS = {
    'storm', 'spell.*cast.*turn', 'copy.*spell', 'replicate',
    'cascade', 'suspend', 'rebound'
}

# Infect keywords
INFECT_KEYWORDS = {
    'infect', 'poisonous', 'poison counter', 'infected', 'toxic',
    'wither', 'persist', '-1/-1 counter'
}

# Reanimator keywords
REANIMATOR_KEYWORDS = {
    'reanimate', 'animate dead', 'return.*creature.*graveyard', 'resurrection',
    'unearth', 'persist', 'undying', 'return.*battlefield', 'brings back'
}

# Slivers keywords
SLIVERS_KEYWORDS = {
    'sliver', 'all slivers', 'sliver creatures', 'shared', 'abilities',
    'all creatures share', 'gains', 'have'
}

# Eldrazi keywords  
ELDRAZI_KEYWORDS = {
    'eldrazi', 'annihilator', 'devoid', 'colorless', 'exile.*permanent',
    'ingest', 'process', 'void', 'emerge', 'large'
}

# Energy keywords
ENERGY_KEYWORDS = {
    'energy', 'energy counter', 'get.*energy', 'pay.*energy',
    'fabricate', 'servo', 'aetherworks'
}

# Devotion keywords
DEVOTION_KEYWORDS = {
    'devotion', 'mana symbols', 'permanents you control', 'among permanents',
    'devotion to', 'colored mana symbols'
}

# Affinity keywords
AFFINITY_KEYWORDS = {
    'affinity', 'artifact', 'metalcraft', 'costs.*less', 'improvise',
    'artifact spells', 'artifact creatures', 'cost reduction'
}

# All keyword sets for easy access
ALL_KEYWORD_SETS = {
    'TRIBAL_TYPES': TRIBAL_TYPES,
    'EQUIPMENT_KEYWORDS': EQUIPMENT_KEYWORDS,
    'AGGRESSIVE_KEYWORDS': AGGRESSIVE_KEYWORDS,
    'CONTROL_KEYWORDS': CONTROL_KEYWORDS,
    'RAMP_KEYWORDS': RAMP_KEYWORDS,
    'TEMPO_KEYWORDS': TEMPO_KEYWORDS,
    'COMBO_KEYWORDS': COMBO_KEYWORDS,
    'VOLTRON_KEYWORDS': VOLTRON_KEYWORDS,
    'ARISTOCRATS_KEYWORDS': ARISTOCRATS_KEYWORDS,
    'GRAVEYARD_KEYWORDS': GRAVEYARD_KEYWORDS,
    'BURN_KEYWORDS': BURN_KEYWORDS,
    'SPELLSLINGER_KEYWORDS': SPELLSLINGER_KEYWORDS,
    'LIFEGAIN_KEYWORDS': LIFEGAIN_KEYWORDS,
    'TOKEN_KEYWORDS': TOKEN_KEYWORDS,
    'ENCHANTMENTS_KEYWORDS': ENCHANTMENTS_KEYWORDS,
    'COUNTERS_KEYWORDS': COUNTERS_KEYWORDS,
    'MILL_KEYWORDS': MILL_KEYWORDS,
    'LANDFALL_KEYWORDS': LANDFALL_KEYWORDS,
    'CYCLING_KEYWORDS': CYCLING_KEYWORDS,
    'MADNESS_KEYWORDS': MADNESS_KEYWORDS,
    'MIDRANGE_KEYWORDS': MIDRANGE_KEYWORDS,
    'VEHICLES_KEYWORDS': VEHICLES_KEYWORDS,
    'PLANESWALKERS_KEYWORDS': PLANESWALKERS_KEYWORDS,
    'HISTORIC_KEYWORDS': HISTORIC_KEYWORDS,
    'KICKER_KEYWORDS': KICKER_KEYWORDS,
    'MULTICOLOR_KEYWORDS': MULTICOLOR_KEYWORDS,
    'BLINK_KEYWORDS': BLINK_KEYWORDS,
    'SACRIFICE_KEYWORDS': SACRIFICE_KEYWORDS,
    'STORM_KEYWORDS': STORM_KEYWORDS,
    'INFECT_KEYWORDS': INFECT_KEYWORDS,
    'REANIMATOR_KEYWORDS': REANIMATOR_KEYWORDS,
    'SLIVERS_KEYWORDS': SLIVERS_KEYWORDS,
    'ELDRAZI_KEYWORDS': ELDRAZI_KEYWORDS,
    'ENERGY_KEYWORDS': ENERGY_KEYWORDS,
    'DEVOTION_KEYWORDS': DEVOTION_KEYWORDS,
    'AFFINITY_KEYWORDS': AFFINITY_KEYWORDS,
}
