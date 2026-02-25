from airflow.sdk import dag
from dags.datasource.tasks.paper_metadata_ingestion_task import (
    flatten,
    ingest_papers_task,
    load_domain_ingestion_states,
    load_subject_to_ingest,
    update_domain_ingestion_states,
)
from pendulum import datetime

from common.utils.logger.logger_config import LOG_MODULES, LoggerManager

LoggerManager._log_module = LOG_MODULES.AIRFLOW

logger = LoggerManager.get_logger(__name__)


@dag(
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule="@daily",
    tags=["paper_metadata_ingestion"],
    max_active_tasks=16,
)
def paper_metadata_ingestion_dag():
    """Run paper metadata ingestion task per datasources."""
    logger.info("Running paper metadata ingestion task")

    ingestion_states = load_domain_ingestion_states()
    subject_candidates = load_subject_to_ingest.expand(ingestion_state=ingestion_states)
    flattened_subject_candidates = flatten(subject_candidates)
    ingested_states = ingest_papers_task.expand(
        subject_record=flattened_subject_candidates
    )
    flattened_ingested_states = flatten(ingested_states)
    update_domain_ingestion_states(ingestion_states=flattened_ingested_states)


dag_variable = paper_metadata_ingestion_dag()

if __name__ == "__main__":
    dag_variable.test()
    print("hrer")
