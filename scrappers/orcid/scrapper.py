from typing import List
from operator import attrgetter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pydantic import HttpUrl

from tqdm import tqdm
from loguru import logger

from .common import OrcidId, OrcidWork, ScopusUrl


WAIT_TIME = 15
AFTER_COOKIE_ACCEPT_WAIT_TIME = 3
SCOPUS_URL_WAIT_TIME = 1


class Orcid:
    @staticmethod
    def get_works(
        driver: webdriver.Firefox, orcid_ids: List[OrcidId]
    ) -> List[List[OrcidWork]]:
        logger.trace(orcid_ids)
        orcid_works = []
        for orcid_id in orcid_ids:
            logger.info(f"Scrapping works for ORCID: '{orcid_id}'")
            logger.trace(f"{orcid_id.__repr__()}")
            works = Orcid._get_works_for_orcid(driver, orcid_id)
            orcid_works.append(works)
            logger.info(
                f"Scrapped {len(works)} works, {sum(1 for w in works if w.scopus_url is not None)} of them have Scopus URL"
            )
        logger.trace(orcid_works)
        return orcid_works

    @staticmethod
    def _get_works_for_orcid(
        driver: webdriver.Firefox, orcid_id: OrcidId
    ) -> List[OrcidWork]:
        logger.debug(f"Loading works page: '{orcid_id.url}'")
        driver.get(orcid_id.url)
        logger.debug(f"Accepting cookies")
        Orcid._click_to_accept_cookies(driver)
        logger.debug(f"Scrapping work web elements")
        works_we = Orcid._get_works_we(driver)
        works = []
        logger.debug(f"Pasring work web elements to OrcidWork objects")
        works_we_iter = tqdm(works_we, desc="Parsing works", unit="work", delay=0.5)
        for work_we in works_we_iter:
            work = Orcid._work_we_to_work(driver, work_we)
            works.append(work)
        return works

    @staticmethod
    def _work_we_to_work(driver: webdriver.Firefox, work: WebElement) -> OrcidWork:
        logger.debug("Scrapping work title")
        work_title = work.find_element(
            By.XPATH, ".//h4[@class='work-title orc-font-body ng-star-inserted']"
        ).text
        logger.trace(f"{work_title}")
        scopus_url = None
        logger.debug(f"Trying to scrap scopus link")
        try:
            scopus_url = Orcid._get_scopus_link(driver, work)
        except NoSuchElementException:
            # logger.warning("Scopus link not found")
            pass
        else:
            scopus_url = ScopusUrl(url=scopus_url)
        logger.trace(f"{scopus_url}")
        return OrcidWork(
            title=work_title,
            scopus_url=scopus_url,
        )

    @staticmethod
    def _get_works_we(driver: webdriver.Firefox) -> List[WebElement]:
        logger.debug(f"Wait {WAIT_TIME} seconds until work web elements will appear")
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.ID, "works"))
        )
        logger.debug(f"Scrapping work web elements")
        works = driver.find_elements(By.TAG_NAME, "app-work-stack")
        return works

    @staticmethod
    def _get_scopus_link(driver: webdriver.Firefox, work: WebElement) -> HttpUrl:
        logger.debug(f"Trying to find 'Show More' button")
        show_more_button = work.find_element(
            By.XPATH, ".//a[@role='button'][contains(text(), 'Show more detail')]"
        )
        logger.debug("Scrolling to button and click it")
        driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
        show_more_button.click()
        logger.debug(
            f"Wait {SCOPUS_URL_WAIT_TIME} seconds until scopus url will appear and scrap it"
        )
        scopus_bv = (
            By.XPATH,
            ".//app-display-attribute//a[contains(text(), 'www.scopus.com')]",
        )
        scopus_we = None
        try:
            scopus_we = WebDriverWait(work, SCOPUS_URL_WAIT_TIME).until(
                EC.presence_of_element_located(scopus_bv)
            )
        except TimeoutException:
            scopus_we = work.find_element(*scopus_bv)
        scopus_url = scopus_we.text.strip()
        logger.trace(scopus_url)
        return HttpUrl(scopus_url)

    @staticmethod
    def _click_to_accept_cookies(driver: webdriver.Firefox) -> None:
        btn_xpath = "//button[contains(text(), 'Reject Unnecessary Cookies')]"
        logger.debug(
            f"Wait until 'Reject Unnecessary Cookies' button will appear and click it"
        )
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, btn_xpath))
        )
        cookie_btn = driver.find_element(By.XPATH, btn_xpath)
        cookie_btn.click()
        # WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "//div[@class='onetrust-pc-dark-filter ot-fade-in'][contains(@style, 'display: none;')]")))
        logger.debug(f"Wait {WAIT_TIME} seconds until 'Cookie banner' will dissapear")
        cookie_banner_xpath = (
            "//div[@aria-label='Cookie banner'][contains(@style, 'display: none;')]"
        )
        WebDriverWait(driver, WAIT_TIME).until(
            EC.presence_of_element_located((By.XPATH, cookie_banner_xpath))
        )

    @staticmethod
    def _click_show_citation(driver: webdriver.Firefox, work: WebElement) -> None:
        logger.debug(
            f"Wait {WAIT_TIME} seconds until 'Show citation' button will appear"
        )
        show_cit_btn_xpath = ".//a[@role='button'][normalize-space()='Show citation']"
        WebDriverWait(driver, WAIT_TIME).until(
            (EC.presence_of_element_located((By.XPATH, show_cit_btn_xpath)))
        )
        show_cit_btn = work.find_element(By.XPATH, show_cit_btn_xpath)
        logger.debug("Scroll to button and click it")
        driver.execute_script("arguments[0].scrollIntoView();", show_cit_btn)
        show_cit_btn.click()

    @staticmethod
    def scroll_to_elem(driver: webdriver.Firefox, elem: WebElement) -> None:
        driver.execute_script("arguments[0].scrollIntoView();", elem)
