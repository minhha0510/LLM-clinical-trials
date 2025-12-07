# Codemap: Common Patterns and Rules (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: Project standards and constraints.

## Data Handling
-   **Separators**: Raw files use `|`.
-   **Encoding**: Handle potential encoding issues in raw text dumps (e.g., CP1252 vs UTF-8).
-   **Memory**: Do NOT load full datasets into memory if possible. Use `names=` or `usecols=` to load only necessary columns.
-   **Optimization**: Only merge `detailed_description` for rows that typically need deep context (e.g., "Other/Unclear").

## Nomenclature
-   **NCT ID**: Unique identifier for studies (e.g., `NCT00666029`).
-   **Terminated**: `overall_status` == "TERMINATED".

## Taxonomy (Termination Reasons)
Strict priority order for Regex:
1.  **COVID** -> Exclude.
2.  **Mislabeled** -> "Completed", "Successfully finished".
3.  **Enrollment** -> "Accrual", "Recruitment", "Enroll".
4.  **Administrative** -> "Sponsor", "Funding", "Business".
5.  **Safety** -> "Safety", "Adverse events".
6.  **Efficacy** -> "Efficacy", "Futile".
7.  **Other/Unclear** -> Fallback category. Needs LLM.
