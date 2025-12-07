# Codemap: Data Flows (auto-maintained by LLM)
Last updated: 2025-12-06
Responsibility: Major data transformations and pipelines.

## Phase 1a: Ground Truth Extraction
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
```

## Phase 1b: Medical Field Enrichment
```mermaid
graph TD;
    BaseCSV["pilot_ground_truth.csv / terminated_ground_truth.csv"] --> Enrich["add_medical_fields.py"];
    Mesh["browse_conditions.txt (MeSH)"] -->|Primary Source| Enrich;
    Cond["conditions.txt"] -->|Fallback 1| Enrich;
    Title["brief_title + brief_summary"] -->|Fallback 2| Enrich;
    Enrich --> FieldMap["Field Mappings (15+ specialties)"];
    FieldMap --> Enriched["*_with_fields.csv / *_enriched.csv"];
```

## Key Transformations
-   **Phase 1a Filtering**: `overall_status` = 'TERMINATED', `study_type` = 'INTERVENTIONAL', `primary_purpose` = 'TREATMENT'.
-   **Phase 1b Classification**: Text matching against medical field taxonomy using MeSH terms → Conditions → Title/Summary hierarchy.
