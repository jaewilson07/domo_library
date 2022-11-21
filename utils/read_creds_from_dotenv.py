import os
from os.path import exists
from pprint import pprint

from dotenv import load_dotenv

from . import DictDot as dd


def split_str_to_obj(env_string: str, value_split_keys: list[str]):
    env_list = env_string.split('|')
    obj = {}

    for index, new_obj_key in enumerate(value_split_keys):
        obj[new_obj_key] = env_list[index]

    return dd.DictDot(obj)


def split_creds(env: dd.DictDot, key_starts_with: str, env_var_list: list[str]):
    env_lines_to_split = [getattr(env, key) for key in dir(
        env) if key.startswith(key_starts_with)]

    return [split_str_to_obj(env_string=line, value_split_keys=env_var_list) for line in env_lines_to_split]


def read_creds_from_dotenv(env_path: str = '.env',
                           params: list[str] = None,
                           debug: bool = False) -> dd.DictDot:
    """use_prod = false will replace all PROD values with matching TEST values"""

    file_exists = exists(env_path)
    if not file_exists:
        print(f"file not found at -- {env_path}")
        raise Exception('env file not found')

    load_dotenv(env_path)
    params = params or list(os.environ.keys())

    params_res = {}
    for param in params:
        param = str(param)
        params_res.update({param: os.environ.get(param)})

    if debug:
        pprint(vars(os.environ))
        pprint({'read_creds_from_params': params_res})

    return dd.DictDot(params_res)
