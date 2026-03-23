from airflow.sdk import TriggerRule, dag
from dags.datasource.tasks.paper_download_task import (
    download_papers,
    load_downloadable_papers,
)

from pendulum import datetime

from common.utils.logger import LOG_MODULES, LoggerManager

LoggerManager._log_module = LOG_MODULES.AIRFLOW

logger = LoggerManager.get_logger(__name__)


@dag(
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule="*/10 * * * *",  # every 10 minutes
    tags=["paper_download"],
    max_active_runs=1,
    max_active_tasks=6,
)
def download_papers_dag():
    """Run download paper task per datasources."""
    logger.info("Running download paper task")

    downloadable_papers = load_downloadable_papers()
    download_papers.expand(downloadable_paper=downloadable_papers)


dag_variable = download_papers_dag()

if __name__ == "__main__":
    dag_variable.test()
