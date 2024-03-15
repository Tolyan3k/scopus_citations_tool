from typing import List, Optional
import re

from pydantic import (
    BaseModel,
    HttpUrl,
    field_validator,
    ValidationInfo,
    ValidationError,
)
from loguru import logger


class ScopusUrl(BaseModel):
    url: HttpUrl

    def __str__(self) -> str:
        return self.url.__str__()

    @field_validator("url")
    @classmethod
    def check_url(cls, url: HttpUrl, _: ValidationInfo) -> HttpUrl:
        logger.debug(f"Check Scopus URL format: '{url}'")
        any = r".*"
        reg = rf"https?:\/\/www.scopus.com\/.+\?eid=2-s2\.0-\d+{any}"
        url = str(url).strip()
        is_scopus_url = re.fullmatch(reg, url.__str__())
        logger.trace(f"'{is_scopus_url}'")
        if not is_scopus_url:
            raise ValueError("Wrong scopus url")
        return url


class ScopusRecord(BaseModel):
    title: str
    authors: Optional[List[str]]
    journal: Optional[str]


class ScopusRecords(BaseModel):
    scopus_url: ScopusUrl
    count: int
    records: List[ScopusRecord]
