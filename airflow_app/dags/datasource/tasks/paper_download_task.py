# ruff: noqa: E402

from common.utils.logger import LOG_MODULES, LoggerManager

LoggerManager._log_module = LOG_MODULES.AIRFLOW
LoggerManager.get_logger(__name__)
import os
from httpx import AsyncClient
import asyncio
from datetime import timedelta
from typing import List
from airflow.sdk import task
from common.database.postgres.repositories import DatabaseRepository
from common.database.postgres.session import cleanup, get_session_factory, init_database
from common.constants.states import PaperProcessingStatus
from common.storage.s3_client import get_s3_client
from dags.datasource.schema.downloadable_paper import DownloadablePaper
from common.storage.storage_configs import S3PrefixConfig
from common.datasources.factories.paper_downloader_factory import PaperDownloaderFactory


@task(
    retries=2,
    retry_delay=timedelta(seconds=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=1),
    sla=timedelta(minutes=1),
    execution_timeout=timedelta(seconds=10),
)
def load_downloadable_papers() -> List[DownloadablePaper]:
    """Loads downloadable papers for ingestion.

    Returns:
        List[DownloadablePaper]: A list of downloadable papers.
    """
    DOWNLOAD_PAPERS_COUNT = 64

    async def _run(download_paper_counts: int):
        logger = LoggerManager.get_logger(__name__)
        logger.info("Start loading downloadable papers")
        init_database()
        _async_session_factory = get_session_factory()
        _db = DatabaseRepository()
        try:
            async with _async_session_factory() as session:
                # TODO: only papers that has retry count < 10 or something
                papers = await _db.paper_processing_state.claim_papers_by_status(
                    PaperProcessingStatus.METADATA_INGESTED,
                    PaperProcessingStatus.PAPER_DOWNLOADING,
                    download_paper_counts,
                    session,
                )
                await session.commit()

                downloadable_papers: List[DownloadablePaper] = []
                for paper in papers:
                    downloadable_papers.append(
                        DownloadablePaper(
                            paper_id=paper.id,
                            paper_identifier=paper.paper_identifier,
                            datasource_name=paper.datasource.name,
                        )
                    )
        except Exception as e:
            # TODO: increment retry count when failed
            # TODO: error message
            async with _async_session_factory() as session:
                for paper in papers:
                    await _db.paper_processing_state.update(
                        paper.id,
                        PaperProcessingStatus.METADATA_INGESTED,
                        session,
                    )
                await session.commit()
            logger.error(
                "Error running load downloadable papers task",
                exc_info=e,
            )
            raise e

        finally:
            await cleanup()

        downloadable_papers = [
            downloadable_paper.model_dump(mode="json")
            for downloadable_paper in downloadable_papers
        ]
        logger.info(
            "Downloadable papers loaded",
            extra={"count": len(downloadable_papers)},
        )
        return downloadable_papers

    return asyncio.run(_run(DOWNLOAD_PAPERS_COUNT))


@task(
    retries=5,
    retry_delay=timedelta(seconds=10),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(seconds=30),
)
def download_papers(downloadable_paper: DownloadablePaper):
    async def _run(downloadable_paper: DownloadablePaper):
        logger = LoggerManager.get_logger(__name__)
        logger.info("Start downloading paper")
        s3_location = S3PrefixConfig.PAPER_PDF
        http_client = AsyncClient()
        paper_downloader = PaperDownloaderFactory.get(
            datasource_type=downloadable_paper.datasource_name, client=http_client
        )

        try:
            s3_key = os.path.join(
                s3_location.prefix, f"{downloadable_paper.paper_identifier}.pdf"
            )
            paper_bytes = await paper_downloader.download(
                downloadable_paper.paper_identifier
            )
            async with get_s3_client() as s3_client:
                await s3_client.put_object(
                    Body=paper_bytes,
                    Bucket=s3_location.bucket,
                    Key=s3_key,
                )

        except Exception as e:
            init_database()
            _async_session_factory = get_session_factory()
            _db = DatabaseRepository()
            async with _async_session_factory() as session:
                await _db.paper_processing_state.update(
                    downloadable_paper.paper_id,
                    PaperProcessingStatus.METADATA_INGESTED,
                    session,
                )
                await session.commit()
            await cleanup()
            logger.error(
                "Error running download paper task",
                exc_info=e,
            )
            raise e

    download_paper = DownloadablePaper.model_validate(downloadable_paper)
    return asyncio.run(_run(download_paper))
