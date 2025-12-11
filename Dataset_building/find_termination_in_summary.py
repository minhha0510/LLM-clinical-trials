"""
Find specific examples where brief_summary contains termination reasons.
Looking for cases where the brief_summary explicitly mentions why a trial was stopped.
"""

import pandas as pd

# Load data
df = pd.read_csv('terminated_ground_truth_enriched.csv')

# Define patterns that indicate ACTUAL termination reasons in brief_summary
# (not just study objectives like "assess safety" or "evaluate efficacy")
termination_patterns = [
    r'study was terminated',
    r'trial was terminated',
    r'study was stopped',
    r'trial was stopped',
    r'study was discontinued',
    r'trial was discontinued',
    r'study was closed',
    r'study was halted',
    r'terminated due to',
    r'stopped due to',
    r'discontinued due to',
    r'closed due to',
    r'terminated because',
    r'stopped because',
    r'terminated early',
    r'stopped early',
    r'discontinued early',
    r'prematurely terminated',
    r'prematurely stopped',
    r'trial closed',
    r'enrollment was stopped',
    r'recruitment was stopped',
    r'terminated for',
    r'stopped for',
]

# Combine patterns
combined_pattern = '|'.join(termination_patterns)

# Find matches
matches = df[df['brief_summary'].str.contains(combined_pattern, case=False, na=False, regex=True)]

print(f"Found {len(matches)} trials where brief_summary contains termination reasons")
print("=" * 80)

# Show examples
for idx, row in matches.head(10).iterrows():
    print(f"\n{'='*80}")
    print(f"NCT ID: {row['nct_id']}")
    print(f"Phase: {row['phase']}")
    print(f"Medical Field: {row['medical_field']}")
    print(f"Termination Category: {row['termination_category']}")
    print(f"\nWHY_STOPPED:")
    print(f"  {row['why_stopped']}")
    print(f"\nBRIEF_SUMMARY (relevant excerpt):")
    
    # Find and highlight the termination-related part
    summary = str(row['brief_summary'])
    # Try to extract the sentence containing the termination info
    import re
    for pattern in termination_patterns:
        match = re.search(r'[^.]*' + pattern + r'[^.]*\.', summary, re.IGNORECASE)
        if match:
            print(f"  >>> {match.group(0).strip()}")
            break
    else:
        # If no sentence match, show first 500 chars
        print(f"  {summary[:500]}...")
    
    print("-" * 80)

print(f"\n\nTOTAL: {len(matches)} trials with termination reasons in brief_summary")
print(f"This is {len(matches)/len(df)*100:.2f}% of all trials")
