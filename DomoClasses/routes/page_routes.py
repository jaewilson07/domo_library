import aiohttp

from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_page_by_id(full_auth: DomoFullAuth, page_id: str,
                         debug: bool = False, log_result: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v3/stacks/{page_id}/cards'

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
    )

    if log_result:
        print(res)

    return res


async def get_page_definition(full_auth, page_id, debug: bool = False, session: aiohttp.ClientSession = None):

    close_session = False if session else True

    if not session:
        session = aiohttp.ClientSession()
    try:
        url = f"https://{full_auth.domo_instance}.domo.com/api/content/v3/stacks/{page_id}/cards"

        params = {"includeV4PageLayouts": "true",
                  "parts": "metadata,datasources,library,drillPathURNs,certification,owners,dateInfo,subscriptions,slicers"}

        res = await get_data(url,
                             method='GET',
                             auth=full_auth,
                             session=session,
                             params=params, debug=debug)

        return res
    finally:
        if close_session:
            await session.close()
