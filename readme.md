# Project Progress

## Completed

### Ingestion (arXiv)
- [x] Airflow DAG for subject taxonomy ingestion
- [x] Airflow DAG for paper metadata ingestion
- [x] Idempotent, retry-safe ingestion logic
- [x] Pagination handling for arXiv API
- [x] Domain normalization and canonicalization
- [x] Paper–domain relationship mapping
- [x] Datasource abstraction and registry
- [x] Thread-safe datasource/schema registration
- [x] Ingestion state/schema models
- [x] Async DB setup with isolated test schemas
- [x] Mocked arXiv HTTP responses for tests
- [x] Concurrency and deduplication validation

## In Progress
- [ ] Preprocessing pipeline design

## Planned
- [ ] PDF download and text extraction
- [ ] Chunking and embedding generation
- [ ] Vector DB integration
- [ ] RAG pipeline
- [ ] Metrics and observability