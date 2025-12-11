import pandas as pd
import os
import numpy as np

# Define paths
BASE_DIR = r"C:\Users\1234\OneDrive - Vanderbilt\Projects\LLM-clinical trials"
GROUND_TRUTH_PATH = os.path.join(BASE_DIR, "Final_data_sets", "terminated_ground_truth_enriched.csv")
DEEPSEEK_RESULTS_PATH = os.path.join(BASE_DIR, "output", "deepseek_extraction_results.csv")
INPUT_FIELDS_PATH = os.path.join(BASE_DIR, "Prediction", "Input_fields_for_LLM_prediction-Input.csv")
DATA_DIR = os.path.join(BASE_DIR, "CT_data_full", "main_data")
OUTPUT_PATH = os.path.join(BASE_DIR, "Pilot_datasets", "pilot_prediction_dataset.csv")

def load_and_select_nct_ids():
    """Selects 80 unique nct_ids: 50 from ground truth, 30 from deepseek results."""
    print("Loading source datasets...")
    df_gt = pd.read_csv(GROUND_TRUTH_PATH)
    df_ds = pd.read_csv(DEEPSEEK_RESULTS_PATH)
    
    # Selection Group A: 50 from Ground Truth (stratified by termination_category)
    # Filter for valid categories if needed, but here we just want variety
    print("Selecting 50 trials from Ground Truth...")
    # Group by termination_category and sample to ensure diversity
    # If a category has few samples, take all, then fill remainder randomly
    group_a_ids = []
    
    # Get counts per category
    category_counts = df_gt['termination_category'].value_counts()
    
    # Calculate target samples per category (proportional, but capped/floored)
    # Simple approach: Sample up to k items from each category until we have 50?
    # Or just random sample 50 from the whole set, hoping for diversity? 
    # Better: Stratified sampling.
    
    # Let's try to get a mix. 
    # If we simply sample 50 random rows, we might get mostly "Enrollment".
    # Let's take 5 samples from top 10 categories, or similar logic. 
    # Actually, verify column exists first.
    if 'termination_category' not in df_gt.columns:
        print("Warning: 'termination_category' not found, doing random sampling.")
        sampled_gt = df_gt.sample(n=50, random_state=42)
    else:
        # Stratified sampling
        # We want ~50. 
        # Calculate weights inverse to frequency? Or just take one from each category first?
        # Let's just do a simple stratified sample using pandas groupby
        # If n < 50, take all.
        try:
            # Fraction to get approx 50
            frac = 50 / len(df_gt)
            # Ensure at least 1 per category if possible? 
            # A simpler robust way:
            df_gt_shuffled = df_gt.sample(frac=1, random_state=42)
            # Take distinct categories first
            unique_cats = df_gt_shuffled.groupby('termination_category').head(2) 
            remaining_needed = 50 - len(unique_cats)
            if remaining_needed > 0:
                remaining = df_gt_shuffled[~df_gt_shuffled.index.isin(unique_cats.index)]
                sampled_gt = pd.concat([unique_cats, remaining.head(remaining_needed)])
            else:
                sampled_gt = unique_cats.head(50)
        except Exception as e:
            print(f"Stratified sampling failed: {e}. Falling back to random.")
            sampled_gt = df_gt.sample(n=50, random_state=42)

    group_a_ids = set(sampled_gt['nct_id'].unique())
    print(f"Selected {len(group_a_ids)} from Ground Truth.")

    # Selection Group B: 30 from Deepseek (Unclear/No Context)
    print("Selecting 30 trials from Deepseek results (Unclear/No Context)...")
    # Filter for 'No Context', 'Unclear', or NaNs in 'primary_reasons'
    # Based on user chat, ANY from this file are good as they are pre-processed for this.
    # But let's prioritize empty or "No Context" if present.
    # Check if 'primary_reasons' exists
    if 'primary_reasons' in df_ds.columns:
        unclear_mask = df_ds['primary_reasons'].astype(str).str.contains('No Context|Unclear|nan|None', case=False, regex=True) | df_ds['primary_reasons'].isnull()
        candidates_b = df_ds[unclear_mask]
        if len(candidates_b) < 30:
            # Fallback to any from deepseek
            candidates_b = df_ds
    else:
        candidates_b = df_ds

    # Remove IDs already in Group A
    candidates_b = candidates_b[~candidates_b['nct_id'].isin(group_a_ids)]
    
    # Sample 30
    if len(candidates_b) >= 30:
        sampled_b = candidates_b.sample(n=30, random_state=42)
    else:
        sampled_b = candidates_b
        print(f"Warning: Only found {len(sampled_b)} valid candidates in Deepseek results.")
    
    group_b_ids = set(sampled_b['nct_id'].unique())
    print(f"Selected {len(group_b_ids)} from Deepseek results.")
    
    all_ids = list(group_a_ids.union(group_b_ids))
    print(f"Total unique nct_ids: {len(all_ids)}")
    return all_ids, sampled_gt, sampled_b

def get_mapping_from_input_file():
    """Reads the mapping CSV and returns a dict {source_file: [col1, col2...]}."""
    print("Reading input fields mapping...")
    df_map = pd.read_csv(INPUT_FIELDS_PATH)
    
    mapping = {}
    for _, row in df_map.iterrows():
        source = row['Source file']
        var_name = row['Variable name']
        if pd.isna(source) or pd.isna(var_name):
            continue
        source = source.strip()
        var_name = var_name.strip()
        
        if source not in mapping:
            mapping[source] = []
        mapping[source].append(var_name)
    
    # Explicitly add brief_summaries.txt if not present
    if 'brief_summaries.txt' not in mapping:
        mapping['brief_summaries.txt'] = []
    if 'description' not in mapping['brief_summaries.txt']:
        mapping['brief_summaries.txt'].append('description')
        
    return mapping

def extract_data(target_nct_ids, mapping):
    """Iterates through source files and extracts data for target IDs."""
    
    # Initialize base dataframe with nct_ids
    # We want a DataFrame that we can merge into. 
    combined_df = pd.DataFrame({'nct_id': target_nct_ids})
    
    for source_file, columns in mapping.items():
        file_path = os.path.join(DATA_DIR, source_file)
        if not os.path.exists(file_path):
            print(f"Warning: Source file {source_file} not found at {file_path}. Skipping.")
            continue
            
        print(f"Processing {source_file}...")
        
        # 'description' in brief_summaries is usually 'description', but we want to rename it to 'brief_summary'? 
        # The user said "Add in brief_summaries.txt...". 
        # We will extract 'description' and rename it later if needed.
        
        cols_to_load = ['nct_id'] + columns
        # Remove duplicates
        cols_to_load = list(set(cols_to_load))
        
        try:
            # Pipe delimited
            # Using iterator or chunksize if files are huge, but let's try standard read first with usecols
            # columns might not exist in file? Best to check or read header first.
            
            # Read just header
            header = pd.read_csv(file_path, sep='|', nrows=0).columns.tolist()
            valid_cols = [c for c in cols_to_load if c in header]
            
            if 'nct_id' not in valid_cols:
                print(f"Error: 'nct_id' not found in {source_file}. Skipping.")
                continue
                
            df_chunk = pd.read_csv(file_path, sep='|', usecols=valid_cols, dtype=str)
            
            # Filter
            df_filtered = df_chunk[df_chunk['nct_id'].isin(target_nct_ids)].copy()
            
            # Drop duplicates if any (one row per study per file usually, but extracted fields might be 1:1)
            # brief_summaries is 1:1. designs is 1:1. 
            # If multiple rows, we need to decide how to aggregate. 
            # For now, drop duplicates on nct_id to keep it simple 1:1
            if df_filtered.duplicated(subset=['nct_id']).any():
                 # Aggregate? or first? input file implies simple variables.
                 # Let's keep first for now but warn
                 # print(f"Warning: Duplicates found in {source_file} for some IDs. Keeping first.")
                 df_filtered = df_filtered.drop_duplicates(subset=['nct_id'])
            
            # Merge
            combined_df = pd.merge(combined_df, df_filtered, on='nct_id', how='left')
            
        except Exception as e:
            print(f"Error processing {source_file}: {e}")
            
    return combined_df

def main():
    # 1. Select IDs
    target_ids, sampled_gt, sampled_ds = load_and_select_nct_ids()
    
    # 2. Get Field Mapping
    mapping = get_mapping_from_input_file()
    
    # 3. Extract Data
    extracted_df = extract_data(target_ids, mapping)
    
    # 4. Enrich with Labels/Metadata
    # We want to add back the info from GT and Deepseek (like why_stopped, termination_category, etc)
    # GT columns to keep
    gt_cols_to_enrich = ['nct_id', 'brief_title', 'why_stopped', 'termination_category', 'phase', 'medical_field', 'medical_subfield']
    ds_cols_to_enrich = ['nct_id', 'primary_reasons', 'reason_category'] # Adjust based on actual ds columns
    
    # Check actual columns in sampled_ds
    available_ds_cols = [c for c in ds_cols_to_enrich if c in sampled_ds.columns]
    
    print("Enriching dataset...")
    
    # Merge GT info
    # Note: sampled_gt only has 50 rows. The other 30 come from ds.
    # We merge left on extracted_df to keep all 80 rows
    final_df = pd.merge(extracted_df, sampled_gt[gt_cols_to_enrich], on='nct_id', how='left')
    
    # Merge DS info for the applicable rows
    # We need to be careful not to create duplicate columns if names overlap (e.g. 'nct_id')
    final_df = pd.merge(final_df, sampled_ds[available_ds_cols], on='nct_id', how='left')
    
    # Rename 'description' from brief_summaries to 'brief_summary' if present and not conflicting
    if 'description' in final_df.columns:
        # Check if 'brief_summary' already exists (from GT file maybe?)
        if 'brief_summary' in final_df.columns:
             # If yes, coerce or fillna?
             # GT file has 'brief_summary' column too! 
             # Let's prefer the extracted full text from brief_summaries.txt over the csv snippet if longer?
             # Or just rename description to 'brief_summary_extracted'
             final_df.rename(columns={'description': 'brief_summary_extracted'}, inplace=True)
        else:
             final_df.rename(columns={'description': 'brief_summary'}, inplace=True)

    # 5. Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved pilot dataset to {OUTPUT_PATH}")
    
    # 6. Verify
    print("Verifying...")
    assert len(final_df) == len(target_ids), f"Length mismatch: {len(final_df)} vs {len(target_ids)}"
    assert final_df['nct_id'].is_unique, "Duplicate nct_ids found!"
    print(f"Verification Check Passed: {len(final_df)} rows.")

if __name__ == "__main__":
    main()
