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

def archetype_alignment_score(deck_df, theme_config):
    # Reuse logic from notebook
    keywords = theme_config.get('keywords', [])
    archetype = theme_config.get('archetype')
    if deck_df is None or deck_df.empty:
        return 0
    text_fields = deck_df['Oracle Text'].fillna('') + ' ' + deck_df['Type'].fillna('')
    text = ' '.join(text_fields).lower()
    
    # Handle enum archetype values
    if isinstance(archetype, Archetype):
        archetype_value = archetype.value.lower()
    else:
        archetype_value = str(archetype).lower() if archetype else ''
    
    # Aggro: low CMC, lots of creatures
    if archetype_value == Archetype.AGGRO.value.lower():
        avg_cmc = deck_df['CMC'].mean() if 'CMC' in deck_df else 0
        creature_count = deck_df['Type'].str.contains('creature', case=False, na=False).sum()
        return (creature_count / len(deck_df)) * (1 if avg_cmc <= 3 else 0.5)
    # Control: removal, card draw, instants/sorceries
    if archetype_value == Archetype.CONTROL.value.lower():
        removal_count = text.count('removal') + text.count('destroy') + text.count('counter')
        return removal_count / len(deck_df)
    # Midrange: mix of creatures, value, removal
    if archetype_value == Archetype.MIDRANGE.value.lower():
        return 0.5 * (deck_df['Type'].str.contains('creature', case=False, na=False).sum() / len(deck_df)) + 0.5 * (text.count('removal') / len(deck_df))
    # Ramp: ramp, mana, expensive spells
    if archetype_value == Archetype.RAMP.value.lower():
        return text.count('ramp') + text.count('mana') + (deck_df['CMC'] > 4).sum() / len(deck_df)
    # Tempo: flying, bounce, tempo
    if archetype_value == Archetype.TEMPO.value.lower():
        return text.count('flying') + text.count('bounce') + text.count('tempo')
    # Handle custom archetypes
    if archetype_value == Archetype.STOMPY.value.lower():
        # Similar to aggro but favors higher power creatures
        avg_cmc = deck_df['CMC'].mean() if 'CMC' in deck_df else 0
        creature_count = deck_df['Type'].str.contains('creature', case=False, na=False).sum()
        return (creature_count / len(deck_df)) * (0.8 if avg_cmc <= 4 else 1.0)  # Allow slightly higher CMC
    if archetype_value == Archetype.TRIBAL.value.lower():
        # Count tribal synergies
        return sum(text.count(kw) for kw in keywords) / max(1, len(deck_df))
    if archetype_value == Archetype.ARTIFACTS.value.lower():
        artifact_count = deck_df['Type'].str.contains('artifact', case=False, na=False).sum()
        return artifact_count / len(deck_df)
    return 0

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
