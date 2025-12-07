# Codemap: Service Boundaries (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: File/Module ownership and public contracts.

## Data Source Layer (`CT_data_full`)
-   **Owns**: Raw data files locally.
-   **Contract**: Text files are pipe-delimited (`|`). Key files: `studies.txt`, `designs.txt`, `brief_summaries.txt`.

## Extraction Scripts
### `LLM_extraction.py`
-   **Status**: Existing.
-   **Purpose**: Initial LLM extraction logic (Under development).

### `build_pilot_dataset.py` (Decommissioned/Superseded)
-   **Purpose**: Original pilot sampler. Superseded by `assign_taxonomy.py` for full dataset.

### `analyze_reasons.py`
-   **Status**: Active / Utility.
-   **Purpose**: Analyzing text frequencies in `why_stopped`. Used to drive taxonomy.

### `assign_taxonomy.py`
-   **Owns**: Creation of `terminated_ground_truth.csv`.
-   **Logic**:
    -   Filters `studies.txt` (Interventional/Terminated/Treatment).
    -   Applies Regex Taxonomy (Enrollment, Admin, Safety, etc.).
    -   Merges `brief_summary` (all) and `detailed_description` (target sub-population).

### `add_medical_fields.py`
-   **Owns**: Enrichment of ground truth datasets with medical field classifications.
-   **Logic**:
    -   Uses MeSH terms from `browse_conditions.txt` as primary source.
    -   Falls back to `conditions` column if MeSH unavailable.
    -   Further fallback to `brief_title` + `brief_summary` for classification.
    -   Maps to 15+ medical specialties (Oncology, Cardiology, Neurology, etc.).
    -   Extracts medical subfields for more granular categorization.
-   **Outputs**: 
    -   `pilot_ground_truth_with_fields.csv`
    -   `terminated_ground_truth_enriched.csv` (when run with --full flag)
