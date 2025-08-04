import pandas as pd
import numpy as np
from collections import Counter
from .enums import Archetype

def average_cmc(deck_df):
    if 'CMC' in deck_df:
        return deck_df['CMC'].mean()
    return np.nan

def card_type_distribution(deck_df):
    if 'Type' in deck_df:
        types = deck_df['Type'].fillna('').str.lower()
        type_counts = Counter()
        for t in types:
            for part in t.split(' '):
                type_counts[part] += 1
        total = sum(type_counts.values())
        return {k: v / total for k, v in type_counts.items() if total > 0}
    return {}

def keyword_density(deck_df, keywords):
    if 'Oracle Text' in deck_df:
        text = ' '.join(deck_df['Oracle Text'].fillna('')).lower()
        return sum(1 for kw in keywords if kw in text) / max(1, len(keywords))
    return 0

def _get_deck_stats(deck_df):
    """Extract common deck statistics for archetype scoring."""
    deck_size = len(deck_df)
    avg_cmc = deck_df['CMC'].mean() if 'CMC' in deck_df else 0
    
    # Combine text fields for analysis
    text_fields = deck_df['Oracle Text'].fillna('') + ' ' + deck_df['Type'].fillna('')
    full_text = ' '.join(text_fields).lower()
    
    # Count card types
    creature_count = deck_df['Type'].str.contains('creature', case=False, na=False).sum()
    artifact_count = deck_df['Type'].str.contains('artifact', case=False, na=False).sum()
    
    return {
        'size': deck_size,
        'avg_cmc': avg_cmc,
        'text': full_text,
        'creature_ratio': creature_count / deck_size,
        'artifact_ratio': artifact_count / deck_size,
        'high_cmc_ratio': (deck_df['CMC'] > 4).sum() / deck_size if 'CMC' in deck_df else 0
    }

def _score_aggro_alignment(stats):
    """Score alignment with aggressive archetype."""
    # Favor creature-heavy decks with low average CMC
    creature_bonus = stats['creature_ratio']
    cmc_bonus = 1.0 if stats['avg_cmc'] <= 3 else 0.5
    return creature_bonus * cmc_bonus

def _score_control_alignment(stats):
    """Score alignment with control archetype."""
    # Count control-related keywords
    control_keywords = ['removal', 'destroy', 'counter', 'draw', 'exile']
    control_score = sum(stats['text'].count(keyword) for keyword in control_keywords)
    return min(control_score / stats['size'], 1.0)  # Cap at 1.0

def _score_midrange_alignment(stats):
    """Score alignment with midrange archetype."""
    # Balance of creatures and removal/value
    creature_component = stats['creature_ratio'] * 0.5
    removal_component = min(stats['text'].count('removal') / stats['size'], 0.5) * 0.5
    return creature_component + removal_component

def _score_ramp_alignment(stats):
    """Score alignment with ramp archetype."""
    # Mana acceleration and expensive spells
    ramp_keywords = ['ramp', 'mana', 'search', 'land']
    ramp_score = sum(stats['text'].count(keyword) for keyword in ramp_keywords)
    expensive_bonus = stats['high_cmc_ratio']
    return min((ramp_score / stats['size']) + expensive_bonus, 1.0)  # Cap at 1.0

def _score_tempo_alignment(stats):
    """Score alignment with tempo archetype."""
    # Evasion and tempo-related effects
    tempo_keywords = ['flying', 'bounce', 'return', 'counter', 'flash']
    tempo_score = sum(stats['text'].count(keyword) for keyword in tempo_keywords)
    return min(tempo_score / stats['size'], 1.0)  # Cap at 1.0

def _score_stompy_alignment(stats):
    """Score alignment with stompy archetype."""
    # Similar to aggro but allows higher CMC for bigger creatures
    creature_bonus = stats['creature_ratio']
    cmc_bonus = 1.0 if stats['avg_cmc'] <= 4 else 0.8  # More forgiving than aggro
    return creature_bonus * cmc_bonus

def _score_tribal_alignment(stats, keywords):
    """Score alignment with tribal archetype."""
    # Count tribal-specific keywords
    tribal_score = sum(stats['text'].count(keyword) for keyword in keywords)
    return min(tribal_score / stats['size'], 1.0)  # Cap at 1.0

def _score_artifacts_alignment(stats):
    """Score alignment with artifacts archetype."""
    return stats['artifact_ratio']

def archetype_alignment_score(deck_df, theme_config):
    """
    Calculate how well a deck aligns with its intended archetype.
    
    Returns a score between 0 and 1, where 1 indicates perfect alignment.
    """
    if deck_df is None or deck_df.empty:
        return 0.0
    
    archetype = theme_config.get('archetype')
    keywords = theme_config.get('keywords', [])
    
    # Normalize archetype to enum value
    if isinstance(archetype, Archetype):
        archetype_type = archetype
    else:
        # Try to match string to enum
        archetype_str = str(archetype).upper() if archetype else ''
        try:
            archetype_type = Archetype[archetype_str]
        except (KeyError, AttributeError):
            return 0.0
    
    # Get deck statistics once
    stats = _get_deck_stats(deck_df)
    
    # Route to appropriate scoring function
    scoring_functions = {
        Archetype.AGGRO: _score_aggro_alignment,
        Archetype.CONTROL: _score_control_alignment,
        Archetype.MIDRANGE: _score_midrange_alignment,
        Archetype.RAMP: _score_ramp_alignment,
        Archetype.TEMPO: _score_tempo_alignment,
        Archetype.STOMPY: _score_stompy_alignment,
        Archetype.TRIBAL: lambda stats: _score_tribal_alignment(stats, keywords),
        Archetype.ARTIFACTS: _score_artifacts_alignment,
    }
    
    scoring_function = scoring_functions.get(archetype_type)
    if scoring_function:
        return scoring_function(stats)
    
    return 0.0

def card_quality_score(deck_df):
    # Use average power + toughness if available
    if 'Power' in deck_df and 'Toughness' in deck_df:
        try:
            power = pd.to_numeric(deck_df['Power'], errors='coerce')
            toughness = pd.to_numeric(deck_df['Toughness'], errors='coerce')
            return (power.fillna(0) + toughness.fillna(0)).mean()
        except Exception:
            return np.nan
    return np.nan

def synergy_score(deck_df, keywords):
    # Count how many cards share a keyword/tribal type
    if 'Oracle Text' in deck_df:
        text = ' '.join(deck_df['Oracle Text'].fillna('')).lower()
        return sum(text.count(kw) for kw in keywords) / max(1, len(deck_df))
    return 0

def compute_deck_metrics(deck_df, theme_config):
    metrics = {}
    metrics['avg_cmc'] = average_cmc(deck_df)
    type_dist = card_type_distribution(deck_df)
    for t, v in type_dist.items():
        metrics[f'type_{t}'] = v
    metrics['keyword_density'] = keyword_density(deck_df, theme_config.get('keywords', []))
    metrics['archetype_alignment'] = archetype_alignment_score(deck_df, theme_config)
    metrics['card_quality'] = card_quality_score(deck_df)
    metrics['synergy'] = synergy_score(deck_df, theme_config.get('keywords', []))
    metrics['deck_size'] = len(deck_df) if deck_df is not None else 0
    return metrics

def compute_all_deck_metrics(deck_dataframes, all_themes):
    rows = []
    for theme, deck_df in deck_dataframes.items():
        theme_config = all_themes.get(theme, {})
        row = {'theme': theme}
        row.update(compute_deck_metrics(deck_df, theme_config))
        rows.append(row)
    return pd.DataFrame(rows)
