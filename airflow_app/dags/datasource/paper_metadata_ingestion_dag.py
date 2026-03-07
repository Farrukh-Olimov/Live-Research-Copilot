from airflow.sdk import TriggerRule, dag
from dags.datasource.tasks.paper_metadata_ingestion_task import (
    flatten,
    ingest_papers_task,
    load_domain_ingestion_states,
    load_subject_to_ingest,
    update_domain_ingestion_states,
    update_statistics,
)
from pendulum import datetime

from common.utils.logger import LOG_MODULES, LoggerManager

LoggerManager._log_module = LOG_MODULES.AIRFLOW

logger = LoggerManager.get_logger(__name__)


@dag(
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule="@daily",
    tags=["paper_metadata_ingestion"],
    max_active_tasks=6,
    max_active_runs=1,
)
def paper_metadata_ingestion_dag():
    """Run paper metadata ingestion task per datasources."""
    logger.info("Running paper metadata ingestion task")

    ingestion_states = load_domain_ingestion_states()
    subject_candidates = load_subject_to_ingest.expand(ingestion_state=ingestion_states)
    flattened_subject_candidates = flatten(subject_candidates)
    ingested_tasks = ingest_papers_task.expand(
        subject_record=flattened_subject_candidates
    )
    updated_states = update_domain_ingestion_states()
    updated_statistics = update_statistics.override(trigger_rule=TriggerRule.ALL_DONE)()

    ingested_tasks >> updated_states
    updated_states >> updated_statistics


dag_variable = paper_metadata_ingestion_dag()

if __name__ == "__main__":
    dag_variable.test()
    print("hrer")
