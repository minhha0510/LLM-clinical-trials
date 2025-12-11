"""
Quick analysis to check if brief_summary contains termination reason information.

This script analyzes the terminated_ground_truth_enriched.csv to determine
if the brief_summary column provides additional context about why trials were stopped.
"""

import pandas as pd
import re
from collections import Counter

# Load data
print("Loading data...")
df = pd.read_csv('terminated_ground_truth_enriched.csv')

print(f"\n{'='*70}")
print("BRIEF SUMMARY ANALYSIS: Termination Information")
print(f"{'='*70}\n")

# Basic statistics
print(f"Total trials: {len(df):,}")
print(f"Trials with brief_summary: {df['brief_summary'].notna().sum():,} ({df['brief_summary'].notna().sum()/len(df)*100:.1f}%)")
print(f"Trials without brief_summary: {df['brief_summary'].isna().sum():,} ({df['brief_summary'].isna().sum()/len(df)*100:.1f}%)")

# Check if brief_summary contains termination-related keywords
termination_keywords = [
    'terminated', 'stopped', 'discontinued', 'closed', 'halted',
    'enrollment', 'accrual', 'recruit', 'funding', 'sponsor',
    'safety', 'adverse', 'efficacy', 'futility'
]

print(f"\n{'='*70}")
print("KEYWORD ANALYSIS IN BRIEF_SUMMARY")
print(f"{'='*70}\n")

keyword_counts = {}
for keyword in termination_keywords:
    count = df['brief_summary'].str.contains(keyword, case=False, na=False).sum()
    keyword_counts[keyword] = count
    print(f"{keyword:20s}: {count:5,} trials ({count/len(df)*100:5.1f}%)")

# Compare why_stopped vs brief_summary content
print(f"\n{'='*70}")
print("COMPARISON: WHY_STOPPED vs BRIEF_SUMMARY")
print(f"{'='*70}\n")

# Sample cases where brief_summary might have additional info
print("Analyzing if brief_summary provides ADDITIONAL termination context...\n")

# Check for trials where brief_summary mentions termination but why_stopped is short
df['why_stopped_length'] = df['why_stopped'].fillna('').str.len()
df['summary_has_term_info'] = df['brief_summary'].str.contains(
    '|'.join(termination_keywords), case=False, na=False
)

additional_info_cases = df[
    (df['summary_has_term_info'] == True) & 
    (df['why_stopped_length'] < 50)
]

print(f"Trials with SHORT why_stopped (<50 chars) but termination info in brief_summary:")
print(f"  Count: {len(additional_info_cases):,} ({len(additional_info_cases)/len(df)*100:.1f}%)")

# Sample examples
print(f"\n{'='*70}")
print("SAMPLE EXAMPLES (5 random cases)")
print(f"{'='*70}\n")

sample = df.sample(5, random_state=42)
for idx, row in sample.iterrows():
    print(f"NCT ID: {row['nct_id']}")
    print(f"Phase: {row['phase']}")
    print(f"Medical Field: {row['medical_field']}")
    print(f"Termination Category: {row['termination_category']}")
    print(f"\nWhy_stopped ({len(str(row['why_stopped']))} chars):")
    print(f"  {str(row['why_stopped'])[:150]}...")
    print(f"\nBrief_summary ({len(str(row['brief_summary']))} chars):")
    print(f"  {str(row['brief_summary'])[:300]}...")
    print(f"\n{'-'*70}\n")

# Conclusion
print(f"\n{'='*70}")
print("CONCLUSION")
print(f"{'='*70}\n")

has_summary = df['brief_summary'].notna().sum()
has_keywords = df['summary_has_term_info'].sum()

print(f"✓ {has_summary:,} trials ({has_summary/len(df)*100:.1f}%) have brief_summary data")
print(f"✓ {has_keywords:,} trials ({has_keywords/len(df)*100:.1f}%) have termination keywords in brief_summary")
print(f"✓ {len(additional_info_cases):,} trials may have ADDITIONAL context in brief_summary")

if has_keywords > 0:
    print(f"\n⚠️  RECOMMENDATION: Brief_summary DOES contain termination-related information")
    print(f"   and could be valuable for enriching termination reason analysis.")
else:
    print(f"\n✓ Brief_summary appears to be primarily study description, not termination reasons")

print(f"\n{'='*70}\n")
