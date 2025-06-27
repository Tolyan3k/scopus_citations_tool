from argparse import ArgumentParser

from pydantic import DirectoryPath
from loguru import logger

from .common import (
    CliSettings,
    CLI_OUT_DIR_DEFAULT,
    CLI_LOG_DIR_DEFAULT,
)


parser = ArgumentParser(
    description= 
        """Gets Scopus URL from ORCID page
        and then gets citations information
        from Scopus work page""",
)

parser.add_argument(
    "--out-dir",
    help= "Output directory for file with Scopus citations",
    type= DirectoryPath,
    default= DirectoryPath(CLI_OUT_DIR_DEFAULT)
)

parser.add_argument(
    "--log-dir",
    help= "Output directory for log file",
    type= DirectoryPath,
    default= DirectoryPath(CLI_LOG_DIR_DEFAULT)
)

args = parser.parse_args()
cli_settings = CliSettings(
    out_dir= args.out_dir,
    log_dir= args.log_dir
)
