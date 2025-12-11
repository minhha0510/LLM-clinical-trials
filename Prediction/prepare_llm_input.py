import pandas as pd
import json
import os
import numpy as np

# Define paths
BASE_DIR = r"C:\Users\1234\OneDrive - Vanderbilt\Projects\LLM-clinical trials"
INPUT_CSV_PATH = os.path.join(BASE_DIR, "Pilot_datasets", "pilot_prediction_dataset.csv")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "Prediction", "pilot_prompts.json")

def preprocess_data():
    print(f"Loading dataset from {INPUT_CSV_PATH}...")
    try:
        df = pd.read_csv(INPUT_CSV_PATH)
    except FileNotFoundError:
        print(f"Error: File not found at {INPUT_CSV_PATH}")
        return

    print(f"Initial rows: {len(df)}")

    # 1. Redundancy Handling
    # Combine brief_title_x and brief_title_y
    if 'brief_title_x' in df.columns and 'brief_title_y' in df.columns:
        df['brief_title'] = df['brief_title_x'].combine_first(df['brief_title_y'])
        df.drop(columns=['brief_title_x', 'brief_title_y'], inplace=True)
    elif 'brief_title_x' in df.columns:
        df.rename(columns={'brief_title_x': 'brief_title'}, inplace=True)
    elif 'brief_title_y' in df.columns:
        df.rename(columns={'brief_title_y': 'brief_title'}, inplace=True)

    # Combine phase_x and phase_y
    if 'phase_x' in df.columns and 'phase_y' in df.columns:
        df['phase'] = df['phase_x'].combine_first(df['phase_y'])
        df.drop(columns=['phase_x', 'phase_y'], inplace=True)
    elif 'phase_x' in df.columns:
        df.rename(columns={'phase_x': 'phase'}, inplace=True)
    elif 'phase_y' in df.columns:
        df.rename(columns={'phase_y': 'phase'}, inplace=True)

    # 2. Outcome Consolidation
    # We want a single 'true_outcome' column.
    # Logic: Prefer 'termination_category' (Group A), fallback to 'primary_reasons' (Group B).
    # Note: In the pilot dataset, Group A has termination_category, Group B might have it as NaN but has primary_reasons.
    
    # Check if columns exist
    if 'termination_category' not in df.columns:
        df['termination_category'] = np.nan
    if 'primary_reasons' not in df.columns:
        df['primary_reasons'] = np.nan

    # Coalesce
    df['true_outcome'] = df['termination_category'].combine_first(df['primary_reasons'])
    
    # 3. Filtering
    # Critical columns: nct_id, brief_title, brief_summary, true_outcome
    critical_cols = ['nct_id', 'brief_title', 'brief_summary', 'true_outcome']
    
    # Check for missing
    missing_mask = df[critical_cols].isnull().any(axis=1)
    if missing_mask.any():
        print(f"Dropping {missing_mask.sum()} rows with missing critical data.")
        # Optional: Print IDs of dropped rows for debugging
        # print(df[missing_mask]['nct_id'].tolist())
        df = df[~missing_mask]
    
    print(f"Rows after filtering: {len(df)}")

    # 4. Prompt Engineering
    prompts = []
    
    for _, row in df.iterrows():
        # Construct manageable input text
        # We exclude outcome related fields from the input text!
        
        nct_id = str(row.get('nct_id', ''))
        title = str(row.get('brief_title', ''))
        phase = str(row.get('phase', ''))
        med_field = str(row.get('medical_field', ''))
        med_subfield = str(row.get('medical_subfield', ''))
        summary = str(row.get('brief_summary', ''))
        criteria = str(row.get('criteria', ''))
        
        # Format the input string
        # Using a structured format
        input_text = (
            f"Trial ID: {nct_id}\n"
            f"Title: {title}\n"
            f"Phase: {phase}\n"
            f"Medical Field: {med_field} - {med_subfield}\n\n"
            f"Brief Summary:\n{summary}\n\n"
            f"Eligibility Criteria:\n{criteria}"
        )
        
        entry = {
            "nct_id": nct_id,
            "input_text": input_text,
            "true_outcome": str(row['true_outcome'])
        }
        prompts.append(entry)

    # Limit to 100 (though we expect 80)
    prompts = prompts[:100]
    
    # 5. Output
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2)
        
    print(f"Saved {len(prompts)} prompts to {OUTPUT_JSON_PATH}")
    
    # Verify
    if len(prompts) > 0:
        print("Sample Entry:")
        print(json.dumps(prompts[0], indent=2))

if __name__ == "__main__":
    preprocess_data()
