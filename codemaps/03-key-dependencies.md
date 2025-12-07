# Codemap: Key Dependencies (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: External services, files, and libraries.

## Local Data Dependencies
-   **`CT_data_full/main_data/`**: MUST exist. Scripts rely on specific filenames:
    -   `studies.txt`, `designs.txt` - Core trial metadata
    -   `brief_summaries.txt`, `detailed_descriptions.txt` - Trial descriptions
    -   `browse_conditions.txt` - MeSH (Medical Subject Headings) terms **[Critical for Phase 1b]**
    -   `conditions.txt` - Condition names (fallback for classification)
-   **`Data-dict/`**: Reference for schema.

## Library Dependencies
-   **Pandas**: Required for efficient CSV/Text processing.
-   **Python stdlib**: `csv`, `os`, `re` (regex for pattern matching).

## Environment
-   **`.env`**: Configuration (likely for API keys in future).
