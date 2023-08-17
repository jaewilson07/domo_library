import aiohttp
from pprint import pprint

from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_grants(full_auth: DomoFullAuth,
                     debug: bool = False, log_results: bool = False,
                     session: aiohttp.ClientSession = None):
    try:
        is_close_session = False

        if not session:
            session = aiohttp.ClientSession()
            is_close_session = True

        url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/authorities'

        if debug:
            print(url)

        return await get_data(auth=full_auth,
                              url=url,
                              method='GET',
                              log_results=log_results,
                              debug=debug,
                              session=session)

    finally:
        if is_close_session:
            await session.close()
