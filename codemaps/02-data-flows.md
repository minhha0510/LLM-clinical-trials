# Codemap: Data Flows (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: Major data transformations and pipelines.

## Phase 1: Pilot Extraction
```mermaid
graph TD;
    RawStudies["studies.txt"] -->|Filter: Terminated, Treatment, Interventional| Candidates;
    Candidates -->|Regex Classification| Taxonomy["Taxonomy Category"];
    Taxonomy -->|Split| Clean["Identified (Enrollment, Admin, Safety, etc.)"];
    Taxonomy -->|Split| Unclear["Other/Unclear + Unknown"];
    Unclear -->|Merge| Detail["detailed_descriptions.txt"];
    Clean -->|Merge| Summary["brief_summaries.txt only"];
    Detail --> FinalCSV["terminated_ground_truth.csv"];
    Summary --> FinalCSV;
    FinalCSV -->|Input candidates| LLM_Extraction["Phase 2: LLM Classification"];
```

## Key Transformations
-   **Filtering**: `overall_status` = 'TERMINATED', `study_type` = 'INTERVENTIONAL', `primary_purpose` = 'TREATMENT'.
-   **Join** : Left join on `nct_id`.
