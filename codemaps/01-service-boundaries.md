# Codemap: Service Boundaries (auto-maintained by LLM)
Last updated: 2025-12-11
Responsibility: File/Module ownership and public contracts.

## 1. Data Source Layer (`CT_data_full/`)
-   **Owns**: Raw data files locally.
-   **Contract**: Text files are pipe-delimited (`|`). Key files: `studies.txt`, `designs.txt`, `brief_summaries.txt`, `browse_conditions.txt`.

## 2. Dataset Building layer (`Dataset_building/`)
### `assign_taxonomy.py`
-   **Owns**: Core Logic for `terminated_ground_truth.csv`.
-   **Logic**: Filters Terminated/Interventional -> Applies Regex Taxonomy -> Merges Descriptions.

### `add_medical_fields.py`
-   **Owns**: Enrichment (Phase 1b).
-   **Logic**: MeSH/Condition mapping -> Adds `medical_field`, `medical_subfield`.

### `analyze_reasons.py`
-   **Purpose**: Frequency analysis of `why_stopped` text to drive taxonomy rules.

## 3. Experimental Layer (`PhaseI_Endpoint_extraction/`)
### `analyze_reasons_deepseek.py`
-   **Status**: Active Experiment.
-   **Owms**: LLM-based reasoning extraction using DeepSeek API.
-   **Input**: `pilot_unclear_reasons.csv`, `terminated_ground_truth_enriched.csv`
-   **Output**: `deepseek_extraction_results.csv` (incremental)

### `find_termination_in_summary.py`
-   **Purpose**: Locating termination reasons buried in `brief_summary` when `why_stopped` is vague.

## 4. Directory: `Prediction/` (Phase 2)
**Responsibility**: Operational pipeline for predicting clinical trial outcomes using LLMs.

### A. Script: `prepare_llm_input.py`
-   **Responsibility**: Preprocesses pilot datasets into structured JSON prompts for the LLM. Handles merging of redundant columns and outcome consolidation.
-   **Logic**:
    -   Loads `pilot_prediction_dataset.csv`.
    -   Merges `brief_title` and `phase` columns if split.
    -   Consolidates `termination_category` and `primary_reasons` into `true_outcome`.
    -   Formats input fields (ID, Title, Phase, Field, Summary, Criteria) into a prompt string.
-   **Input**: `Pilot_datasets/pilot_prediction_dataset.csv`
-   **Output**: `Prediction/pilot_prompts.json`

### B. Script: `run_predictions.py`
-   **Responsibility**: Orchestrates the LLM inference process.
-   **Logic**:
    -   Loads JSON prompts and the system prompt template (`Prediction_prompts_instruct.txt`).
    -   Initializes OpenAI client for DeepSeek API.
    -   Iterates through prompts, sending requests to `deepseek-chat`.
    -   Parses JSON responses and handles errors/retries.
    -   Saves predictions to a JSON file.
-   **Input**: `Prediction/pilot_prompts.json`
-   **Output**: `Prediction/predicted_outcomes/predictions.json`

## 5. Output Data (`Final_data_sets/` & `Pilot_datasets/`)
-   **`terminated_ground_truth.csv`**: The Gold Standard dataset.
-   **`pilot_ground_truth.csv`**: 100-row sample for quick testing.
-   **`pilot_unclear_reasons.csv`**: Subset focusing on "Other/Unclear" for LLM improvement.
