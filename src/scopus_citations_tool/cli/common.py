from pydantic import BaseModel, DirectoryPath


CLI_LOG_DIR_DEFAULT = "./"
CLI_OUT_DIR_DEFAULT = "./"


class CliSettings(BaseModel):
    log_dir: DirectoryPath = DirectoryPath(CLI_LOG_DIR_DEFAULT)
    out_dir: DirectoryPath = DirectoryPath(CLI_OUT_DIR_DEFAULT)
