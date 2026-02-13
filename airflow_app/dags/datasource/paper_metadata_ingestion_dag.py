from airflow.sdk import dag
from dags.datasource.tasks.paper_metadata_ingestion_task import ingest_papers_task
from pendulum import datetime

from common.constants import DataSource
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
    for datasource in DataSource:
        try:
            ingest_papers_task(datasource)
        except Exception as e:
            logger.error("Error running paper metadata ingestion task", exc_info=e)


# paper_metadata_ingestion_dag()
