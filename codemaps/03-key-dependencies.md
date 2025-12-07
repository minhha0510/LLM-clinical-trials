# Codemap: Key Dependencies (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: External services, files, and libraries.

## Local Data Dependencies
-   **`CT_data_full/main_data/`**: MUST exist. Scripts rely on specific filenames (`studies.txt`, etc.).
-   **`Data-dict/`**: Reference for schema.

## Library Dependencies
-   **Pandas**: Required for efficient CSV/Text processing.
-   **Python stdlib**: `csv`, `os`.

## Environment
-   **`.env`**: Configuration (likely for API keys in future).
