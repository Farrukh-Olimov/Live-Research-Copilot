from airflow.sdk import chain, dag
from dags.datasource.tasks.category_ingestion_task import ingest_categories_task
from dags.datasource.tasks.domain_ingestion_state_task import (
    domain_ingestion_state_task,
)
from pendulum import datetime

from common.constants import DataSource
from common.utils.logger.logger_config import LoggerManager

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
        [ingest_categories_task(datasource_type=DataSource.ARXIV.value)],
        [domain_ingestion_state_task(datasource_type=DataSource.ARXIV.value)],
    )


category_ingestion_dag()
