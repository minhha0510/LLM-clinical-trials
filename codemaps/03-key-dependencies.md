# Codemap: Key Dependencies (auto-maintained by LLM)
Last updated: 2025-12-11
Responsibility: External services, files, and libraries.

## Local Data Dependencies
-   **`CT_data_full/main_data/`**: Source of truth. Scripts often hardcode this path.
    -   `CT_data_full/main_data/`: (Read-Only) Source of truth for `studies.txt`, `browse_conditions.txt`.
-   `Data-dict/`: (Read-Only) Schema references.
-   `Pilot_datasets/`: Input for analysis and prediction phases.
-   `Prediction/`:
    -   `pilot_prompts.json`: Generated prompts for LLM.
    -   `Prediction_prompts_instruct.txt`: System instruction template.

## 2. External Services
-   **DeepSeek API**:
    -   **Context**: Phase 1c (Analysis) and Phase 2 (Prediction).
    -   **Model**: `deepseek-chat` (or `deepseek-reasoner`).
    -   **Client**: Accessed via `openai` Python library.
-   **OpenAI API**: Fallback/Alternative.

## 3. Libraries
-   **Pandas**: Data manipulation (ETL).
-   **OpenAI**: API Client for DeepSeek.
-   **Python stdlib**: `re`, `json`, `os`, `time`.

## 4. Environment
-   `.env`: MUST contain `DEEPSEEK_API_KEY` and/or `OPENAI_API_KEY`.
