from typing import Optional
from re import Match
import re

from pydantic import (
    BaseModel,
    HttpUrl,
    field_validator,
    ValidationInfo,
    ValidationError,
)
from loguru import logger

from ..scopus import ScopusUrl


class OrcidId(BaseModel):
    id: str

    @property
    def url(cls):
        return rf"https://orcid.org/{cls.id}"

    def __str__(cls) -> str:
        return cls.id.__str__()

    @field_validator("id")
    @classmethod
    def check_url(cls, id_or_url: HttpUrl, _: ValidationInfo) -> str:
        logger.debug(f"Check ORCID format: '{id_or_url}'")
        url_reg = r"http(s)?\:\/\/orcid\.org\/"
        id_reg = r"\d{4}(-\d{4}){3}"
        reg = rf"({url_reg})?{id_reg}"
        id_or_url = str(id_or_url).strip()
        is_orcid_with_id = re.fullmatch(reg, id_or_url)
        if not is_orcid_with_id:
            raise ValueError("Wrong ORCID URL format")
        m: Match = re.search(id_reg, id_or_url)
        return m.group()


class OrcidWork(BaseModel):
    title: str
    scopus_url: Optional[ScopusUrl]

    @field_validator("title")
    @classmethod
    def normalize_title(cls, title: str, _: ValidationInfo) -> Optional[str]:
        logger.debug(f"Normalizing title: '{title}'")
        title_norm = title.strip()
        logger.trace(f"'{title}'")
        logger.debug("Check title not empty")
        if title_norm:
            return title_norm
        else:
            raise ValueError("Empty work title")
