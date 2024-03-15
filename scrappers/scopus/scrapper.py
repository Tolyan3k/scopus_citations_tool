from typing import List, Optional
import re

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium import webdriver

from pydantic import HttpUrl, NonNegativeInt
from loguru import logger
from tqdm import tqdm

from .common import ScopusUrl, ScopusRecord, ScopusRecords


class Scopus:
    @staticmethod
    def get_records(
        driver: webdriver.Firefox, scopus_urls: List[Optional[ScopusUrl]]
    ) -> List[ScopusRecords]:
        logger.trace(scopus_urls)
        scopus_records = []
        logger.debug("Scrapping scopus citations")
        scopus_urls_iter = tqdm(
            scopus_urls, desc="Scrapping scopus pages", unit="scopus page", delay=0.5
        )
        for scopus_url in scopus_urls_iter:
            scopus_record = None
            logger.debug("Check scopus link is not None")
            if scopus_url is not None:
                logger.debug("Extracting citations")
                records = Scopus._get_records(driver, scopus_url)
                logger.debug("Counting citatations")
                count = Scopus._get_records_count(driver)
                logger.debug(f"Available {len(records)} of {count}")
                scopus_record = ScopusRecords(
                    scopus_url=scopus_url,
                    count=count,
                    records=records,
                )
            scopus_records.append(scopus_record)
            logger.trace(scopus_record)
        logger.trace(scopus_records)
        return scopus_records

    @staticmethod
    def _get_records_count(driver: webdriver.Firefox) -> NonNegativeInt:
        logger.debug("Scrapping citations overall count")
        records_we = driver.find_element(
            By.XPATH, "//div[@id='recordPageBoxes']//h3[@class='panel-title']"
        )
        count = records_we.text
        count = re.search(r"\d+", count).group()
        logger.trace(count)
        return NonNegativeInt(count)

    @staticmethod
    def _get_records(
        driver: webdriver.Firefox, scopus_url: ScopusUrl
    ) -> List[ScopusRecord]:
        logger.trace(scopus_url)
        logger.debug(f"Scraping citation web elements from '{scopus_url.url}'")
        url = scopus_url.url.__str__()
        driver.get(url)
        records_we = driver.find_elements(
            By.XPATH, ".//div[@class='recordPageBoxItem']"
        )
        logger.debug("Parsing each citation web element to 'ScopusRecord'")
        records = list(map(Scopus._parse_record_we, records_we))
        logger.trace(records)
        return records

    @staticmethod
    def _parse_record_we(record_we: WebElement) -> ScopusRecord:
        logger.debug("Scrap 'authors', 'title' and 'journal' from citation web element")
        authors, _, title, _, journal = record_we.find_elements(By.XPATH, "*")
        logger.debug("Scrap 'authors' list")
        authors = authors.find_elements(By.XPATH, "*")
        authors = [author.text.strip() for author in authors]
        title = title.text
        journal = journal.text
        logger.trace((authors, title, journal))
        return ScopusRecord(
            authors=authors,
            title=title,
            journal=journal,
        )
