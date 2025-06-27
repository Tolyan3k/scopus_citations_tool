import datetime as dt
import re
import secrets
import time

import pydantic
from loguru import logger
from orcid_scraping.models import Orcid, OrcidResearcherWorkUrlSite
from orcid_scraping.models import ScrapeResult as OrcidScrapeResult
from orcid_scraping.tools.selenium import OrcidScrapeToolSelenium
from orcid_scraping.utils import sanitize_orcid
from pydantic import ValidationError
from scopus_scraping.models import ScrapeResult as ScopusScrapeResult
from scopus_scraping.tools import ScopusScrapeToolSelenium
from selenium import webdriver
from tqdm import tqdm

from scopus_citations_tool.cli import cli_settings
from scopus_citations_tool.exporters import CsvExporter
from scopus_citations_tool.logger import logger_config


def scrap_works_records(
    driver: webdriver.Firefox,
    orcid: Orcid,
) -> list[tuple[OrcidScrapeResult, ScopusScrapeResult]]:
    orcid_tool = OrcidScrapeToolSelenium(driver=driver)
    scopus_tool = ScopusScrapeToolSelenium(driver=driver)
    works = []
    logger.info("Scraping ORCID works")
    orcid_scrape_result = orcid_tool.scrape_works(orcid=orcid)
    orcid_works_iter = tqdm(
        orcid_scrape_result.works,
        desc="Scrapping Scopus citations",
        unit="scopus page",
        delay=0.5,
    )
    for orcid_work in orcid_works_iter:
        if (
            orcid_work.url is not None
            and orcid_work.url.source == OrcidResearcherWorkUrlSite.SCOPUS
        ):
            time.sleep(secrets.randbelow(3))
            citations = scopus_tool.scrape_citations(url=str(orcid_work.url.value))
            works.append((orcid_work, citations))
    return works


@pydantic.validate_call(validate_return=True)
def get_most_unique_filename(orcid: Orcid) -> str:
    dt_norm = str(dt.datetime.now(dt.UTC))
    dt_norm = re.sub(r"\:|\.| ", "-", dt_norm)
    return f"{orcid}_{dt_norm}"


def _get_driver() -> webdriver.Firefox:
    driver_opts = webdriver.FirefoxOptions()
    # driver_opts.add_argument("--headless")
    driver: webdriver.Firefox = webdriver.Firefox(driver_opts)
    return driver


def main() -> None:
    orcid_str = input("Enter ORCID (ID or URL): ")
    out_dir = cli_settings.out_dir

    driver = None
    try:
        driver = _get_driver()
        orcid_id = sanitize_orcid(orcid_str)
        filename = get_most_unique_filename(orcid_id)
        works_records = scrap_works_records(driver, orcid_id)
        CsvExporter.export_to_file(works_records, rf"{out_dir}\{filename}.csv")
    except ValidationError as err:
        for error in err.errors():
            logger.error(error["ctx"]["error"])
    except Exception as err:
        logger.exception(err)
        logger.info("Unexpected exceptions has occurred")
    finally:
        logger.info(rf"Log saved to {cli_settings.log_dir}\{logger_config.LOG_FILENAME_DEFAULT}")
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    main()
