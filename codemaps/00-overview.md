# Codemap: Overview (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: High-level architecture, main components, tech stack.

## Project Goal
Predict clinical trial outcomes (Success/Failure) using LLMs, based on public data from CT.gov.

## Phases
1.  **Phase 1**: Build ground truth dataset for terminated trials (Reasons for stopping).
2.  **Phase 2**: LLM prediction and reasoning traces (Future).

## Architecture
-   **source**: `CT_data_full/main_data/*.txt` (Raw CT.gov dump).
-   **processing**: Python scripts to filter, join, and extract text.
-   **output**: CSV datasets (e.g., `pilot_ground_truth.csv`).

## Tech Stack
-   **Language**: Python
-   **Libraries**: Pandas (inferred)
-   **Input Data**: Pipe-delimited text files.
