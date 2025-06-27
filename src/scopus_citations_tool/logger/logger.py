from loguru import logger as _logger

from scopus_citations_tool.cli import cli_settings

from .logger_config import config_logger


LOG_FILENAME_DEFAULT = ".log"


logger = _logger.bind(module="scopus-citations-tool")
config_logger(f"{cli_settings.log_dir}/{LOG_FILENAME_DEFAULT}")
