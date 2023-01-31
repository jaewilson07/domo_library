# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/read_creds_from_dotenv.ipynb.

# %% auto 0
__all__ = ['ReadCreds_EnvFileNotExist', 'read_creds_from_dotenv']

# %% ../../nbs/utils/read_creds_from_dotenv.ipynb 2
import os

from pprint import pprint
from dotenv import load_dotenv

import domolibrary.utils.DictDot as utils_dd

# %% ../../nbs/utils/read_creds_from_dotenv.ipynb 3
class ReadCreds_EnvFileNotExist(Exception):
    def __init__(self, env_path):
        message = f"file not found at -- {env_path}"
        super().__init__(message)

def read_creds_from_dotenv(env_path: str = '.env',
                           params: list[str] = None # list of params you're expecting in the env file,
                           ) -> utils_dd.DictDot:
    """use_prod = false will replace all PROD values with matching TEST values"""

    file_exists = os.path.exists(env_path)

    if not file_exists:    
        raise ReadCreds_EnvFileNotExist(env_path)

    load_dotenv(env_path)
    params = params or list(os.environ.keys())

    params_res = {}
    for param in params:
        param = str(param)
        params_res.update({param: os.environ.get(param)})

    return utils_dd.DictDot(params_res)
