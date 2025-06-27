import csv

import pydantic
import tqdm
from orcid_scraping.models import OrcidResearcherWork
from scopus_scraping.models import ScrapeResult as ScopusScrapeResult

from scopus_citations_tool.logger import logger

from .base import ExporterABC


class CsvExporter(ExporterABC):
    @classmethod
    @pydantic.validate_call(validate_return=True)
    def export(
        cls,
        scrape_results: list[tuple[OrcidResearcherWork, ScopusScrapeResult]],
    ) -> str: ...

    @classmethod
    @pydantic.validate_call
    def export_to_file(
        cls,
        scrape_results: list[tuple[OrcidResearcherWork, ScopusScrapeResult]],
        filepath: str,
    ) -> None:
        logger.info(f"Writing to csv file {filepath}")
        with open(file=filepath, mode="w", newline="", encoding="utf-8") as out:
            csv_w = csv.writer(out)
            csv_title = (
                "Work title",
                "Citations overall",
                "Citations available",
                "Citations",
            )
            csv_w.writerow(csv_title)
            works_records_iter = tqdm.tqdm(
                scrape_results,
                desc="Writing to csv file",
                unit="row",
                delay=0.5,
            )
            for work, records in works_records_iter:
                first_row = (work.title, 0, 0, None)
                if records is not None:
                    first_record = (
                        records.result.citations[0].title if records.result.citations else None
                    )
                    first_row = (
                        work.title,
                        records.result.total,
                        records.result.count,
                        first_record,
                    )
                csv_w.writerow(first_row)
                if records:
                    for i in range(1, records.result.count):
                        csv_w.writerow((None, None, None, records.result.citations[i].title))
        logger.success(f"CSV written to file {filepath}")
