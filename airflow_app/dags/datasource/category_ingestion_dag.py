from airflow.sdk import dag
from dags.datasource.tasks.category_ingestion_task import ingest_categories_task
from pendulum import datetime

from common.constants import DataSource
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


@dag(
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["category_ingestion"],
)
def category_ingestion_dag():
    """A dag that runs the category ingestion task for all datasources.

    Schedules the task to run once a month.
    """
    for datasource_type in DataSource:
        try:
            ingest_categories_task(datasource_type=datasource_type.value)
        except Exception as e:
            logger.error("Error running category ingestion task", exc_info=e)


category_ingestion_dag()
