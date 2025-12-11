# Codemap: Common Patterns and Rules (auto-maintained by LLM)
Last updated: 2025-12-11
Responsibility: Project standards and constraints.

## Directory Structure Rules
1.  **ETL Logic** -> `Dataset_building/`. Do NOT put heavy processing scripts in root.
2.  **Experiments** -> `PhaseI_Endpoint_extraction/` or `Prediction/`.
3.  **Outputs** -> `Final_data_sets/` (for verified data) or `Pilot_datasets/` (for subsets).
4.  **Raw Data** -> `CT_data_full/`. READ-ONLY. Never write here.

## Data Handling
-   **Separators**: Raw files use `|`.
-   **Encoding**: Handle potential encoding issues in raw text dumps (e.g., CP1252 vs UTF-8).
-   **Memory**: Do NOT load full datasets into memory if possible. Use `names=` or `usecols=` to load only necessary columns.
-   **Optimization**: Only merge `detailed_description` for rows that typically need deep context (e.g., "Other/Unclear").

## Nomenclature
-   **NCT ID**: Unique identifier for studies (e.g., `NCT00666029`).
-   **Terminated**: `overall_status` == "TERMINATED".

## Taxonomy: Termination Reasons (Phase 1a)
Strict priority order for Regex:
1.  **COVID** -> Exclude.
2.  **Mislabeled** -> "Completed", "Successfully finished".
3.  **Enrollment** -> "Accrual", "Recruitment", "Enroll".
4.  **Administrative** -> "Sponsor", "Funding", "Business".
5.  **Safety** -> "Safety", "Adverse events".
6.  **Efficacy** -> "Efficacy", "Futile".
7.  **Other/Unclear** -> Fallback category. Needs LLM.

## Medical Field Classification (Phase 1b)
-   **Source Hierarchy**: MeSH terms (browse_conditions) → Conditions → Title/Summary
-   **Field Mappings**: 15+ specialties including:
    -   Oncology, Cardiology, Neurology, Infectious Disease
    -   Immunology, Hematology, Nephrology, Rheumatology
    -   Pulmonology, Gastroenterology, Endocrinology
    -   Psychiatry, Dermatology, Ophthalmology, Other
-   **Subfield Extraction**: Extracts specific conditions/diseases within each field
-   **Pattern Matching**: Case-insensitive keyword matching against curated medical term lists

## Phase 2: Prediction Patterns
### `Prediction/`
-   **Purpose**: Operational prediction pipeline.
-   **Contents**: `prepare_llm_input.py`, `run_predictions.py`, prompt templates.

## 4. Prompt Engineering (Phase 2)
Structured format used for LLM input:

```text
Trial ID: {nct_id}
Title: {brief_title}
Phase: {phase}
Medical Field: {medical_field} - {medical_subfield}

Brief Summary:
{brief_summary}

Eligibility Criteria:
{criteria}
```
**Rule**: Do NOT include the ground truth outcome in the `input_text` field sent to the LLM.

## 5. LLM Interaction Rules
-   **Client**: Use `openai` library (compatible with DeepSeek).
-   **Endpoint**: `https://api.deepseek.com`.
-   **Response Format**: Always enforce `{"type": "json_object"}`.
-   **Parsing**: Use `json.loads()` on the response content.
-   **Error Handling**: Wrap API calls in `try/except` and log errors without crashing the batch.
