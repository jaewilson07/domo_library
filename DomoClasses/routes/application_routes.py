from pprint import pprint

import aiohttp

from ...utils.ResponseGetData import ResponseGetData
from ..DomoAuth import DomoFullAuth
from .get_data import get_data, looper


async def get_applications(full_auth: DomoFullAuth,
                           session: aiohttp.ClientSession = None,
                           debug: bool = False,
                           log_results: bool = False
                           ):

    url = f'https://{full_auth.domo_instance}.domo.com/api/executor/v1/applications/'

    if debug:
        print(url)

    return await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )


async def get_application_by_id(full_auth: DomoFullAuth,
                                application_id: str,
                                session: aiohttp.ClientSession = None,
                                debug: bool = False, log_results: bool = False):

    url = f'https://{full_auth.domo_instance}.domo.com/api/executor/v1/applications/{application_id}'

    if debug:
        print(url)

    return await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )
