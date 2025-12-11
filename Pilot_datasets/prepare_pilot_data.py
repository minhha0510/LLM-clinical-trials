import pandas as pd
import os
import sys

# Configuration
INPUT_FILE = "terminated_ground_truth_enriched.csv"
OUTPUT_FILE = "pilot_unclear_reasons.csv"
TARGET_SAMPLE_SIZE = 50
TARGET_CATEGORIES = ["Unknown", "Other/Unclear"]
FALLBACK_CATEGORIES = ["Administrative"]

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        sys.exit(1)

    print(f"Reading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Total rows in input: {len(df)}")

    # Normalize phase for filtering
    # Expected values: PHASE2, PHASE3, PHASE1/PHASE2, etc.
    if 'phase' not in df.columns:
         print("Error: 'phase' column not found.")
         sys.exit(1)
         
    df['phase_upper'] = df['phase'].astype(str).str.upper()
    
    # Filter for Phase 2 or Phase 3 (including combined phases like PHASE1/PHASE2)
    # logic: contains "PHASE2" or "PHASE3"
    phase_mask = df['phase_upper'].str.contains('PHASE2', na=False) | \
                 df['phase_upper'].str.contains('PHASE3', na=False)
    
    phase_df = df[phase_mask].copy()
    print(f"Rows after Phase II/III filter: {len(phase_df)}")

    if 'termination_category' not in df.columns:
        print("Error: 'termination_category' column missing.")
        sys.exit(1)

    # Clean termination category
    phase_df['termination_category'] = phase_df['termination_category'].astype(str).str.strip()

    # Filter by Reason
    # We want trials where the reason is not immediately obvious (Unknown, Other/Unclear)
    target_mask = phase_df['termination_category'].isin(TARGET_CATEGORIES)
    target_df = phase_df[target_mask]
    
    count_target = len(target_df)
    print(f"Rows with Primary Unclear Categories {TARGET_CATEGORIES}: {count_target}")
    
    if count_target == 0:
        print("\nDEBUG INFO:")
        print("Unique phases found:", df['phase'].unique()[:10])
        print("Unique categories found in filtered phases:", phase_df['termination_category'].unique())

    final_pool = target_df

    # Fallback to Administrative if we don't have enough
    if count_target < TARGET_SAMPLE_SIZE:
        print(f"Warning: Found only {count_target} rows. Adding 'Administrative' category.")
        fallback_mask = phase_df['termination_category'].isin(FALLBACK_CATEGORIES)
        fallback_df = phase_df[fallback_mask]
        print(f"Rows with Fallback Categories {FALLBACK_CATEGORIES}: {len(fallback_df)}")
        
        final_pool = pd.concat([target_df, fallback_df]).drop_duplicates()
        
    print(f"Total available for sampling: {len(final_pool)}")

    # Sampling
    if len(final_pool) > TARGET_SAMPLE_SIZE:
        print(f"Sampling {TARGET_SAMPLE_SIZE} random rows...")
        sampled_df = final_pool.sample(n=TARGET_SAMPLE_SIZE, random_state=42)
    else:
        print(f"Taking all {len(final_pool)} available rows.")
        sampled_df = final_pool
    
    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    # Drop the helper column
    if 'phase_upper' in sampled_df.columns:
        sampled_df = sampled_df.drop(columns=['phase_upper'])
        
    sampled_df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
