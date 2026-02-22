from airflow.sdk import dag
from dags.datasource.tasks.paper_metadata_ingestion_task import (
    ingest_papers_task,
    load_domain_ingestion_states,
    load_subject_to_ingest,
)
from pendulum import datetime

from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


@dag(
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule="@daily",
    tags=["paper_metadata_ingestion"],
)
def paper_metadata_ingestion_dag():
    """Run paper metadata ingestion task per datasources."""
    logger.info("Running paper metadata ingestion task")

    ingestion_states = load_domain_ingestion_states()
    subject_candidates = load_subject_to_ingest.expand(ingestion_state=ingestion_states)


# paper_metadata_ingestion_dag()

if __name__ == "__main__":
    ingestion_states = load_domain_ingestion_states()
    for state in ingestion_states:
        subject_candidates = load_subject_to_ingest(state)
        for subject in subject_candidates:
            ingestion_state = ingest_papers_task(subject)
    print("here")
