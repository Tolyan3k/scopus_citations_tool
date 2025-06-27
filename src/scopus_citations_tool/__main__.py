from operator import attrgetter
from typing import List, Tuple
from datetime import datetime
import csv
import re

from pydantic import ValidationError
from selenium import webdriver
from loguru import logger
from tqdm import tqdm

from scrappers.orcid import OrcidId, OrcidWork
from scrappers.scopus import ScopusRecords
from scrappers import Orcid, Scopus

from cli import cli_settings
import logger_config


def scrap_works_records(
    driver: webdriver.Firefox, orcid: OrcidId
) -> List[Tuple[OrcidWork, ScopusRecords]]:
    orcid_works = Orcid.get_works(driver, [orcid])[0]
    scop_urls = list(map(attrgetter("scopus_url"), orcid_works))
    scops_records = Scopus.get_records(driver, scop_urls)
    return list(zip(orcid_works, scops_records, strict=True))


def parse_to_csv(
    works_records: List[Tuple[OrcidWork, ScopusRecords]],
    out_filename: str,
) -> None:
    logger.info(f"Writing to csv file: {out_filename}")
    with open(out_filename, "w", newline="", encoding="utf-8") as out:
        csv_w = csv.writer(out)
        csv_title = (
            "Work title",
            "Citations overall",
            "Citations available",
            "Citations",
        )
        csv_w.writerow(csv_title)
        works_records_iter = tqdm(
            works_records, desc="Writing to csv file", unit="row", delay=0.5
        )
        for work, records in works_records_iter:
            first_row = (work.title, 0, 0, None)
            if records is not None:
                first_record = records.records[0].title if records.records else None
                first_row = (
                    work.title,
                    records.count,
                    len(records.records),
                    first_record,
                )
            csv_w.writerow(first_row)
            if records:
                for i in range(1, len(records.records)):
                    csv_w.writerow((None, None, None, records.records[i].title))
    logger.success(f"Result saved to {out_filename}")


def get_most_unique_filename(orcid_id: OrcidId) -> str:
    dt_norm = str(datetime.now())
    dt_norm = re.sub(r"\:|\.| ", "-", dt_norm)
    return f"{orcid_id.id}_{dt_norm}"


def _get_driver() -> webdriver.Firefox:
    driver_opts = webdriver.FirefoxOptions()
    driver_opts.add_argument("--headless")
    driver: webdriver.Firefox = webdriver.Firefox(driver_opts)
    return driver


def main():
    orcid_str = input("Enter ORCID (ID or URL): ")
    out_dir = cli_settings.out_dir

    driver = None
    try:
        driver = _get_driver()
        orcid_id = OrcidId(id=orcid_str)
        filename = get_most_unique_filename(orcid_id)
        works_records = scrap_works_records(driver, orcid_id)
        parse_to_csv(works_records, f"{out_dir}\{filename}.csv")
    except ValidationError as err:
        for error in err.errors():
            logger.error(error["ctx"]["error"])
    except Exception as err:
        logger.exception(err)
        logger.info("Unexpected exceptions has occurred")
    finally:
        logger.info(
            f"Log saved to {cli_settings.log_dir}\{logger_config.LOG_FILENAME_DEFAULT}"
        )
        if driver is not None:
            driver.close()


if __name__ == "__main__":
    main()
