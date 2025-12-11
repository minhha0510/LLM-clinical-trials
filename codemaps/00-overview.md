# Codemap: Overview (auto-maintained by LLM)
Last updated: 2025-12-11
Responsibility: High-level architecture, main components, tech stack.

## Project Goal
Predict clinical trial outcomes (Success/Failure) using LLMs, based on public data from CT.gov.

## Phases
1.  **Phase 1a**: Build ground truth dataset (`terminated_ground_truth.csv`).
2. - **Phase 1b**: Enrich datasets with medical field/subfield classifications.
- **Phase 1c**: LLM Reasoning & Endpoint Analysis (Experimental).
- **Phase 2**: Prediction Model Development (Current).
  - Transform pilot data into structured prompts.
  - Execute LLM inference (DeepSeek) to predict trial outcomes.

## Architecture
The project follows a modular pipeline structure:

1.  **Source (`CT_data_full/`)**: Raw Read-only data.
2.  **Processing Modules**:
    - `Dataset_building/`: ETL scripts for ground truth creation.
    - `PhaseI_Endpoint_extraction/`: Experimental Logic & Reasoning.
    - `Prediction/`: **[NEW]** Operational Prediction Pipeline.
        - `prepare_llm_input.py`: Data -> Prompts.
        - `run_predictions.py`: Prompts -> LLM -> JSON Predictions.
3.  **Output**:
    - `Final_data_sets/`: Verified CSVs.
    - `Report_outputs/` & `Prediction/predicted_outcomes/`: Analysis results.

## Tech Stack
- **Languages**: Python 3.10+
- **Core Libraries**: `pandas` (ETL), `re` (Regex), `openai` (DeepSeek Client).
- **Data Format**: Pipe-delimited text (`|`), CSV, JSON (Prompts/Results).
- **APIs**: DeepSeek API (Reasoning/Chat), OpenAI API (Fallback).
