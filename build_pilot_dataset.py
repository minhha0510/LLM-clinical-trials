
import pandas as pd
import os

# Configuration
DATA_DIR = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/CT_data_full/main_data"
OUTPUT_FILE = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/pilot_ground_truth.csv"
SAMPLE_SIZE = 100
RANDOM_SEED = 42

def load_data():
    print("Loading studies.txt...")
    studies = pd.read_csv(
        os.path.join(DATA_DIR, "studies.txt"),
        sep="|",
        usecols=["nct_id", "overall_status", "study_type", "why_stopped", "brief_title"],
        low_memory=False
    )
    
    print("Loading designs.txt...")
    designs = pd.read_csv(
        os.path.join(DATA_DIR, "designs.txt"),
        sep="|",
        usecols=["nct_id", "primary_purpose"],
        low_memory=False
    )
    
    print("Loading brief_summaries.txt...")
    brief_summaries = pd.read_csv(
        os.path.join(DATA_DIR, "brief_summaries.txt"),
        sep="|",
        usecols=["nct_id", "description"],
        low_memory=False
    ).rename(columns={"description": "brief_summary"})
    
    print("Loading detailed_descriptions.txt...")
    detailed_descriptions = pd.read_csv(
        os.path.join(DATA_DIR, "detailed_descriptions.txt"),
        sep="|",
        usecols=["nct_id", "description"],
        low_memory=False
    ).rename(columns={"description": "detailed_description"})

    return studies, designs, brief_summaries, detailed_descriptions

def filter_and_sample(studies, designs):
    print("Filtering data...")
    
    # Join studies and designs
    merged = studies.merge(designs, on="nct_id", how="left")
    
    # Apply filters
    # 1. Study Type = INTERVENTIONAL
    # 2. Overall Status = TERMINATED
    # 3. Primary Purpose = TREATMENT
    
    filtered = merged[
        (merged["study_type"] == "INTERVENTIONAL") &
        (merged["overall_status"] == "TERMINATED") &
        (merged["primary_purpose"] == "TREATMENT")
    ].copy()
    
    print(f"Total terminated/interventional/treatment trials found: {len(filtered)}")
    
    # Sample
    if len(filtered) > SAMPLE_SIZE:
        sampled = filtered.sample(n=SAMPLE_SIZE, random_state=RANDOM_SEED)
        print(f"Sampled {SAMPLE_SIZE} trials.")
    else:
        sampled = filtered
        print(f"Using all {len(filtered)} trials.")
        
    return sampled

def build_dataset():
    studies, designs, brief_summaries, detailed_descriptions = load_data()
    
    # Filter and Sample
    pilot_df = filter_and_sample(studies, designs)
    
    # Join with summaries and descriptions
    print("Joining with descriptions...")
    pilot_df = pilot_df.merge(brief_summaries, on="nct_id", how="left")
    pilot_df = pilot_df.merge(detailed_descriptions, on="nct_id", how="left")
    
    # Reorder columns
    cols = ["nct_id", "brief_title", "why_stopped", "brief_summary", "detailed_description"]
    # Add any extra columns that might be useful for context, but keep it clean
    
    final_df = pilot_df[cols]
    
    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    build_dataset()
