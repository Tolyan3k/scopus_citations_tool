import abc

from orcid_scraping.models import OrcidResearcherWork
from scopus_scraping.models import ScrapeResult as ScopusScrapeResult


class ExporterABC(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def export(
        cls,
        scrape_results: list[tuple[OrcidResearcherWork, ScopusScrapeResult]],
    ) -> str: ...

    @classmethod
    @abc.abstractmethod
    def export_to_file(
        cls,
        scrape_results: list[tuple[OrcidResearcherWork, ScopusScrapeResult]],
        filepath: str,
    ) -> None: ...
