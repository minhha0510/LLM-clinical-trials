# Codemap: Overview (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: High-level architecture, main components, tech stack.

## Project Goal
Predict clinical trial outcomes (Success/Failure) using LLMs, based on public data from CT.gov.

## Phases
1.  **Phase 1a**: Build ground truth dataset for terminated trials (Reasons for stopping).
2.  **Phase 1b**: Enrich datasets with medical field/subfield classifications.
3.  **Phase 2**: LLM prediction and reasoning traces (Future).

## Architecture
-   **source**: `CT_data_full/main_data/*.txt` (Raw CT.gov dump).
-   **processing**: Python scripts to filter, join, extract text, and classify medical fields.
-   **output**: 
    -   Base datasets: `pilot_ground_truth.csv`, `terminated_ground_truth.csv`
    -   Enriched datasets: `pilot_ground_truth_with_fields.csv`, `terminated_ground_truth_enriched.csv`

## Tech Stack
-   **Language**: Python
-   **Libraries**: Pandas, re (regex)
-   **Input Data**: Pipe-delimited text files (CT.gov data export).
