import aiohttp

from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_stream_definition(full_auth: DomoFullAuth, stream_id: str,
                                session: aiohttp.ClientSession = None, debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        session=session,
        debug=debug,
    )
    return res


async def update_stream(full_auth: DomoFullAuth, stream_id: str,
                        body: dict,
                        session: aiohttp.ClientSession = None,
                        debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/data/v1/streams/{stream_id}'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        body=body,
        method='PUT',
        session=session,
        debug=debug,
    )
    return res


async def create_stream(full_auth: DomoFullAuth,
                        body: dict,
                        session: aiohttp.ClientSession = None,
                        debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/data/v1/streams'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        body=body,
        method='POST',
        session=session,
        debug=debug,
    )
    return res
