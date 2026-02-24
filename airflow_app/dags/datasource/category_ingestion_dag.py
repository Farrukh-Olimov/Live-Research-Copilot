from airflow.sdk import chain, dag
from dags.datasource.tasks.category_ingestion_task import (
    domain_ingestion_state_task,
    ingest_categories_task,
)
from pendulum import datetime

from common.constants import DataSource
from common.utils.logger.logger_config import LoggerManager, LOG_MODULES

LoggerManager._log_module = LOG_MODULES.AIRFLOW
logger = LoggerManager.get_logger(__name__)


@dag(
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule="@monthly",
    tags=["category_ingestion"],
)
def category_ingestion_dag():
    """A dag that runs the category ingestion task for all datasources.

    Schedules the task to run once a month.
    """
    chain(
        [ingest_categories_task(datasource_type=DataSource.ARXIV)],
        [domain_ingestion_state_task(datasource_type=DataSource.ARXIV)],
    )


category_ingestion_dag()
