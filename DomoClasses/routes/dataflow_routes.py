import aiohttp
import pandas as pd
import io
from pprint import pprint

from .get_data import get_data, looper
from ..DomoAuth import DomoDeveloperAuth, DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_dataset_by_id(id: str,
                            full_auth: DomoFullAuth = None,
                            dev_auth: DomoDeveloperAuth = None,
                            debug: bool = False, log_result: bool = False) -> ResponseGetData:
    domo_instance = full_auth.domo_instance if full_auth else dev_auth.domo_instance

    url = f'https://{domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{id}'

    res = await get_data(
        auth=full_auth or dev_auth,
        url=url,
        method='GET',
        debug=debug,
    )

    if log_result:
        print(res)

    return res
