
import pandas as pd
import os
import re

# Configuration
DATA_DIR = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/CT_data_full/main_data"
OUTPUT_FILE = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/terminated_ground_truth.csv"

def get_termination_category(why_stopped):
    if not isinstance(why_stopped, str):
        return "Unknown"
    
    text = why_stopped.lower()
    
    # 1. COVID (Sanity check matches)
    if re.search(r'covid|coronavirus|pandemic|sars-cov-2', text):
        return "COVID"
        
    # 2. Completed / Mislabeled
    if re.search(r'\b(completed|successfully finished|main study completed)\b', text):
        return "Mislabeled: Completed"
        
    # 3. Enrollment
    if re.search(r'accrual|enroll|recruit|participant|inclusion|subject|candidate|lack of samples', text):
        return "Enrollment"
        
    # 4. Administrative / Business
    if re.search(r'sponsor|funding|business|administrative|logistics|priority|contract|financial', text):
        return "Administrative"
        
    # 5. Safety
    if re.search(r'safety|toxic|adverse|side effect|risk', text):
        return "Safety"
        
    # 6. Efficacy
    if re.search(r'efficacy|futile|benefit|endpoint|inferiority|no effect', text):
        return "Efficacy"
        
    # 7. Fallback
    return "Other/Unclear"

def process_taxonomy():
    print("Loading data...")
    # Load raw data
    studies = pd.read_csv(
        os.path.join(DATA_DIR, "studies.txt"),
        sep="|",
        usecols=["nct_id", "overall_status", "study_type", "why_stopped", "brief_title"],
        low_memory=False
    )
    designs = pd.read_csv(
        os.path.join(DATA_DIR, "designs.txt"),
        sep="|",
        usecols=["nct_id", "primary_purpose"],
        low_memory=False
    )
    
    # Merge
    merged = studies.merge(designs, on="nct_id", how="left")
    
    # Filter
    print("Filtering for Terminated / Interventional / Treatment...")
    df = merged[
        (merged["study_type"] == "INTERVENTIONAL") &
        (merged["overall_status"] == "TERMINATED") &
        (merged["primary_purpose"] == "TREATMENT")
    ].copy()
    
    print(f"Candidates before cleaning: {len(df)}")
    
    # Apply Taxonomy
    print("Applying taxonomy rules...")
    df["termination_category"] = df["why_stopped"].apply(get_termination_category)
    
    # Filter out COVID immediately as per requirements
    df = df[df["termination_category"] != "COVID"]
    print(f"Candidates after removing COVID: {len(df)}")
    
    # Add Brief Summary for context (useful for next steps)
    print("Loading brief summaries...")
    brief_summaries = pd.read_csv(
        os.path.join(DATA_DIR, "brief_summaries.txt"),
        sep="|",
        usecols=["nct_id", "description"],
        low_memory=False
    ).rename(columns={"description": "brief_summary"})
    
    df = df.merge(brief_summaries, on="nct_id", how="left")

    # Optimization: Only load detailed descriptions for "Other/Unclear" and "Unknown"
    # This reduces memory usage and merge time.
    print("Identified studies requiring detailed description (Other/Unclear + Unknown)...")
    target_mask = df["termination_category"].isin(["Other/Unclear", "Unknown"])
    target_ids = set(df[target_mask]["nct_id"])
    print(f"Count of studies needing detailed description: {len(target_ids)}")
    
    print("Loading detailed descriptions...")
    detailed_descriptions = pd.read_csv(
        os.path.join(DATA_DIR, "detailed_descriptions.txt"),
        sep="|",
        usecols=["nct_id", "description"],
        low_memory=False
    ).rename(columns={"description": "detailed_description"})
    
    # Filter immediately to keep only relevant IDs
    detailed_descriptions = detailed_descriptions[detailed_descriptions["nct_id"].isin(target_ids)]
    
    print("Merging filtered detailed descriptions...")
    df = df.merge(detailed_descriptions, on="nct_id", how="left")
    
    # Select columns
    final_cols = ["nct_id", "brief_title", "why_stopped", "termination_category", "brief_summary", "detailed_description"]
    output_df = df[final_cols]
    
    # Save
    print(f"Saving {len(output_df)} rows to {OUTPUT_FILE}...")
    output_df.to_csv(OUTPUT_FILE, index=False)
    
    # Print Distribution
    print("\n--- Termination Category Distribution ---")
    print(output_df["termination_category"].value_counts())

if __name__ == "__main__":
    process_taxonomy()
