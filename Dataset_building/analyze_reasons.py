
import pandas as pd
import os
from collections import Counter
import re

DATA_DIR = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/CT_data_full/main_data"

def analyze_full_pipeline():
    print("Loading studies.txt...")
    studies = pd.read_csv(
        os.path.join(DATA_DIR, "studies.txt"),
        sep="|",
        usecols=["nct_id", "overall_status", "study_type", "why_stopped"],
        low_memory=False
    )
    total_studies = len(studies)
    unique_ids = studies["nct_id"].nunique()
    print(f"Total Studies in file: {total_studies}")
    print(f"Unique NCT IDs: {unique_ids}")
    
    print("Loading designs.txt...")
    designs = pd.read_csv(
        os.path.join(DATA_DIR, "designs.txt"),
        sep="|",
        usecols=["nct_id", "primary_purpose"],
        low_memory=False
    )
    
    # Merge
    df = studies.merge(designs, on="nct_id", how="left")
    
    # Step 1: Filter Interventional
    interventional = df[df["study_type"] == "INTERVENTIONAL"]
    print(f"Step 1 (Interventional): {len(interventional)}")
    
    # Step 2: Filter Terminated
    terminated = interventional[interventional["overall_status"] == "TERMINATED"]
    print(f"Step 2 (Terminated): {len(terminated)}")
    
    # Step 3: Filter Treatment
    treatment = terminated[terminated["primary_purpose"] == "TREATMENT"]
    print(f"Step 3 (Treatment): {len(treatment)}")
    
    # Step 4: COVID Analysis
    # Ensure why_stopped is string
    treatment = treatment.copy()
    treatment["why_stopped"] = treatment["why_stopped"].fillna("").astype(str)
    
    covid_mask = treatment["why_stopped"].str.contains("covid|coronavirus|pandemic|sars-cov-2", case=False)
    covid_count = covid_mask.sum()
    print(f"Step 4 (COVID Excluded): {covid_count}")
    
    final_prospects = treatment[~covid_mask]
    print(f"Final Candidates for Ground Truth: {len(final_prospects)}")
    
    # Text Analysis on Final Candidates
    print("\n--- Why Stopped Analysis (Final Candidates) ---")
    
    # Top 20 Exact Reasons
    print("\nTop 20 Exact Reasons:")
    print(final_prospects["why_stopped"].value_counts().head(20))
    
    # Top 20 Words
    text = " ".join(final_prospects["why_stopped"].tolist()).lower()
    # Simple tokenization
    words = re.findall(r'\b[a-z]{3,}\b', text) # Ignore short words
    stop_words = {'the', 'was', 'and', 'for', 'due', 'not', 'study', 'with', 'this', 'were', 'from', 'that', 'are', 'have', 'been'} 
    filtered_words = [w for w in words if w not in stop_words]
    
    common_words = Counter(filtered_words).most_common(20)
    print("\nTop 20 Common Words (Filtered):")
    print(common_words)

if __name__ == "__main__":
    analyze_full_pipeline()
