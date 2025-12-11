"""
Add Medical Field and Subfield columns to clinical trial ground truth datasets.

This script extracts medical field information from CT.gov data using:
1. MeSH (Medical Subject Headings) terms from browse_conditions.txt
2. Condition names from conditions.txt 
3. Pattern matching as fallback

Author: Generated for LLM Clinical Trials Project
Date: 2025-12-06
"""

import pandas as pd
import os
import re
from collections import defaultdict

# Configuration
DATA_DIR = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/CT_data_full/main_data"
PILOT_FILE = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/pilot_ground_truth.csv"
FULL_FILE = r"c:/Users/1234/OneDrive - Vanderbilt/Projects/LLM-clinical trials/terminated_ground_truth.csv"

# Medical Field Taxonomy - Mapping from MeSH/Condition terms to fields
# Based on common MeSH tree structures and clinical practice
FIELD_MAPPINGS = {
    # Oncology
    'Oncology': [
        'neoplasm', 'cancer', 'carcinoma', 'tumor', 'tumour', 'malignancy', 'melanoma',
        'lymphoma', 'leukemia', 'leukaemia', 'sarcoma', 'glioma', 'myeloma', 'metastatic',
        'oncology', 'chemotherapy', 'radiation therapy'
    ],
    
    # Cardiology
    'Cardiology': [
        'heart', 'cardiac', 'cardiovascular', 'myocardial', 'coronary', 'artery',
        'atrial', 'ventricular', 'arrhythmia', 'hypertension', 'heart failure',
        'angina', 'thrombosis', 'embolism', 'vascular', 'cardiology'
    ],
    
    # Neurology
    'Neurology': [
        'brain', 'neurological', 'neurology', 'stroke', 'epilepsy', 'seizure',
        'parkinson', 'alzheimer', 'dementia', 'cognitive', 'neural', 'cerebral',
        'neuropathy', 'sclerosis', 'migraine', 'headache'
    ],
    
    # Infectious Diseases
    'Infectious Diseases': [
        'infection', 'infectious', 'bacterial', 'viral', 'fungal', 'sepsis',
        'pneumonia', 'hepatitis', 'hiv', 'aids', 'tuberculosis', 'malaria',
        'covid', 'coronavirus', 'influenza', 'bacteremia'
    ],
    
    # Pulmonology/Respiratory
    'Pulmonology': [
        'lung', 'pulmonary', 'respiratory', 'asthma', 'copd', 'bronch',
        'pneumo', 'airway', 'breathing', 'ventilat'
    ],
    
    # Gastroenterology
    'Gastroenterology': [
        'gastrointestinal', 'digestive', 'stomach', 'intestin', 'colon', 'liver',
        'hepat', 'pancrea', 'biliary', 'crohn', 'colitis', 'ibd', 'cirrhosis'
    ],
    
    # Endocrinology
    'Endocrinology': [
        'diabetes', 'endocrin', 'thyroid', 'hormone', 'metabolic', 'glucose',
        'insulin', 'adrenal', 'pituitary'
    ],
    
    # Nephrology
    'Nephrology': [
        'kidney', 'renal', 'nephro', 'dialysis', 'urinary', 'glomerulo'
    ],
    
    # Hematology
    'Hematology': [
        'blood', 'hematol', 'haematol', 'anemia', 'anaemia', 'hemophilia',
        'coagul', 'platelet', 'thrombocyt'
    ],
    
    # Rheumatology
    'Rheumatology': [
        'arthritis', 'rheumat', 'autoimmune', 'lupus', 'joint', 'osteo',
        'scleroderma', 'vasculitis'
    ],
    
    # Psychiatry
    'Psychiatry': [
        'psychiatric', 'mental', 'depression', 'anxiety', 'psycho', 'schizophrenia',
        'bipolar', 'ptsd', 'stress'
    ],
    
    # Orthopedics
    'Orthopedics': [
        'bone', 'fracture', 'orthop', 'skeletal', 'musculoskeletal', 'spine',
        'vertebral', 'hip', 'knee'
    ],
    
    # Dermatology
    'Dermatology': [
        'skin', 'dermat', 'cutaneous', 'psoriasis', 'eczema', 'rash'
    ],
    
    # Ophthalmology
    'Ophthalmology': [
        'eye', 'ophthalm', 'vision', 'retina', 'glaucoma', 'cataract', 'ocular'
    ],
}


def classify_medical_field(text):
    """
    Classify medical field based on text matching.
    Returns (field, source) tuple.
    """
    if not isinstance(text, str) or not text:
        return ('Unknown', 'No data')
    
    text_lower = text.lower()
    
    # Score each field based on keyword matches
    scores = defaultdict(int)
    for field, keywords in FIELD_MAPPINGS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword), text_lower):
                scores[field] += 1
    
    if scores:
        # Return field with highest score
        best_field = max(scores.items(), key=lambda x: x[1])
        return (best_field[0], 'Pattern Match')
    
    return ('Unknown', 'No match')


def extract_subfield(text, field):
    """
    Extract a more specific subfield based on the primary field.
    This is a simplified version - can be expanded with more sophisticated logic.
    """
    if not isinstance(text, str) or field == 'Unknown':
        return ''
    
    text_lower = text.lower()
    
    # Oncology subfields
    if field == 'Oncology':
        cancer_types = {
            'breast cancer': ['breast cancer', 'breast carcinoma', 'breast neoplasm'],
            'lung cancer': ['lung cancer', 'lung carcinoma', 'nsclc', 'sclc'],
            'colon cancer': ['colon cancer', 'colorectal', 'rectal cancer'],
            'prostate cancer': ['prostate cancer', 'prostate carcinoma'],
            'lymphoma': ['lymphoma', 'hodgkin', 'non-hodgkin'],
            'leukemia': ['leukemia', 'leukaemia', 'aml', 'cml', 'all', 'cll'],
            'melanoma': ['melanoma'],
            'ovarian cancer': ['ovarian cancer', 'ovarian carcinoma'],
            'pancreatic cancer': ['pancreatic cancer', 'pancreatic carcinoma'],
            'brain tumor': ['glioma', 'glioblastoma', 'brain tumor', 'brain cancer'],
        }
        for subfield, patterns in cancer_types.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return subfield
        return 'Other cancer'
    
    # Cardiology subfields
    elif field == 'Cardiology':
        if any(term in text_lower for term in ['atrial fibrillation', 'afib', 'a-fib']):
            return 'Atrial Fibrillation'
        elif any(term in text_lower for term in ['heart failure', 'cardiac failure']):
            return 'Heart Failure'
        elif 'hypertension' in text_lower or 'high blood pressure' in text_lower:
            return 'Hypertension'
        elif 'coronary' in text_lower or 'myocardial infarction' in text_lower:
            return 'Coronary Artery Disease'
        return 'Cardiac disorder'
    
    # Neurology subfields
    elif field == 'Neurology':
        neuro_types = {
            'Stroke': ['stroke', 'cerebrovascular'],
            'Epilepsy': ['epilepsy', 'seizure'],
            "Parkinson's Disease": ['parkinson'],
            "Alzheimer's Disease": ['alzheimer'],
            'Multiple Sclerosis': ['multiple sclerosis', 'ms '],
        }
        for subfield, patterns in neuro_types.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return subfield
        return 'Neurological disorder'
    
    # For other fields, return generic subfield
    return f'{field} disorder'


def process_ground_truth_file(input_file, output_file, test_mode=True):
    """
    Process a ground truth CSV file and add medical field columns.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        test_mode: If True, shows detailed output for testing
    """
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(input_file)}")
    print(f"{'='*60}\n")
    
    # Load ground truth data
    print("Loading ground truth data...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} trials")
    print(f"Columns: {list(df.columns)}")
    
    # Load conditions, MeSH terms, and phase information
    print("\nLoading CT.gov data sources...")
    
    # Load phase information from studies.txt
    studies_phase = pd.read_csv(
        os.path.join(DATA_DIR, "studies.txt"),
        sep="|",
        usecols=["nct_id", "phase"],
        low_memory=False
    )
    print(f"  - Loaded phase information for {len(studies_phase)} studies")
    
    # Load conditions
    conditions = pd.read_csv(
        os.path.join(DATA_DIR, "conditions.txt"),
        sep="|",
        usecols=["nct_id", "name"],
        low_memory=False
    )
    print(f"  - Loaded {len(conditions)} condition records")
    
    # Load MeSH terms
    browse_conditions = pd.read_csv(
        os.path.join(DATA_DIR, "browse_conditions.txt"),
        sep="|",
        usecols=["nct_id", "mesh_term"],
        low_memory=False
    )
    print(f"  - Loaded {len(browse_conditions)} MeSH term records")
    
    # Aggregate all conditions and MeSH terms per trial
    print("\nAggregating medical information per trial...")
    
    # Group conditions by NCT ID
    cond_grouped = conditions.groupby('nct_id')['name'].apply(
        lambda x: ' | '.join(x.dropna())
    ).reset_index()
    cond_grouped.columns = ['nct_id', 'all_conditions']
    
    # Group MeSH terms by NCT ID
    mesh_grouped = browse_conditions.groupby('nct_id')['mesh_term'].apply(
        lambda x: ' | '.join(x.dropna())
    ).reset_index()
    mesh_grouped.columns = ['nct_id', 'all_mesh_terms']
    
    # Merge with ground truth
    df = df.merge(cond_grouped, on='nct_id', how='left')
    df = df.merge(mesh_grouped, on='nct_id', how='left')
    df = df.merge(studies_phase, on='nct_id', how='left')
    
    print(f"  - {df['all_conditions'].notna().sum()} trials have condition data")
    print(f"  - {df['all_mesh_terms'].notna().sum()} trials have MeSH data")
    print(f"  - {df['phase'].notna().sum()} trials have phase information")
    
    # Classify medical field using hierarchical approach
    print("\nClassifying medical fields...")
    
    results = []
    for idx, row in df.iterrows():
        # Try MeSH terms first (most reliable)
        if pd.notna(row.get('all_mesh_terms')):
            field, source = classify_medical_field(row['all_mesh_terms'])
            if field != 'Unknown':
                subfield = extract_subfield(row['all_mesh_terms'], field)
                results.append({
                    'medical_field': field,
                    'medical_subfield': subfield,
                    'field_source': 'MeSH'
                })
                continue
        
        # Fall back to condition names
        if pd.notna(row.get('all_conditions')):
            field, source = classify_medical_field(row['all_conditions'])
            if field != 'Unknown':
                subfield = extract_subfield(row['all_conditions'], field)
                results.append({
                    'medical_field': field,
                    'medical_subfield': subfield,
                    'field_source': 'Condition'
                })
                continue
        
        # Last resort: use brief_title or brief_summary
        text = str(row.get('brief_title', '')) + ' ' + str(row.get('brief_summary', ''))
        field, source = classify_medical_field(text)
        subfield = extract_subfield(text, field) if field != 'Unknown' else ''
        
        results.append({
            'medical_field': field,
            'medical_subfield': subfield,
            'field_source': 'Title/Summary' if field != 'Unknown' else 'Unable to classify'
        })
    
    # Add results to dataframe
    results_df = pd.DataFrame(results)
    df = pd.concat([df, results_df], axis=1)
    
    # Remove temporary columns but keep phase
    final_columns = [col for col in df.columns if col not in ['all_conditions', 'all_mesh_terms']]
    df = df[final_columns]
    
    # Reorder columns to put phase, medical_field, medical_subfield, and field_source together
    base_cols = [col for col in df.columns if col not in ['phase', 'medical_field', 'medical_subfield', 'field_source']]
    df = df[base_cols + ['phase', 'medical_field', 'medical_subfield', 'field_source']]
    
    # Save output
    print(f"\nSaving results to: {output_file}")
    df.to_csv(output_file, index=False)
    
    # Print statistics
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    print(f"\nTotal trials processed: {len(df)}")
    print(f"\nMedical Field Distribution:")
    print(df['medical_field'].value_counts())
    print(f"\nField Source Distribution:")
    print(df['field_source'].value_counts())
    print(f"\nPhase Distribution:")
    print(df['phase'].value_counts())
    print(f"\nCoverage: {(df['medical_field'] != 'Unknown').sum() / len(df) * 100:.1f}% classified")
    
    if test_mode:
        print("\n" + "="*60)
        print("SAMPLE RECORDS (first 5)")
        print("="*60)
        sample_cols = ['nct_id', 'brief_title', 'phase', 'medical_field', 'medical_subfield', 'field_source']
        print(df[sample_cols].head().to_string(index=False))
    
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60 + "\n")
    
    return df


if __name__ == "__main__":
    import sys
    
    # Check command line argument for which dataset to process
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # Process full dataset
        full_output = FULL_FILE.replace('.csv', '_enriched.csv')
        print("\n" + "#" * 60)
        print("# PROCESSING FULL DATASET: terminated_ground_truth.csv")
        print("# Output: terminated_ground_truth_enriched.csv")
        print("#" * 60)
        full_df = process_ground_truth_file(FULL_FILE, full_output, test_mode=False)
        
        print("\n" + "#" * 60)
        print("# FULL DATASET PROCESSING COMPLETE!")
        print(f"# Original file preserved: {FULL_FILE}")
        print(f"# Enriched file created: {full_output}")
        print("#" * 60)
    else:
        # Test on pilot first (default)
        pilot_output = PILOT_FILE.replace('.csv', '_with_fields.csv')
        
        print("PHASE 1: Testing on pilot_ground_truth.csv")
        print("(To process full dataset, run: python add_medical_fields.py --full)")
        pilot_df = process_ground_truth_file(PILOT_FILE, pilot_output, test_mode=True)
        
        print("\n" + "#" * 60)
        print("# Pilot processing complete!")
        print("# To process full dataset, run: python add_medical_fields.py --full")
        print("#" * 60)
