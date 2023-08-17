import aiohttp

from ...utils.ResponseGetData import ResponseGetData
from ..DomoAuth import DomoFullAuth
from .get_data import get_data


async def get_bootstrap(full_auth: DomoFullAuth, debug: bool, session: aiohttp.ClientSession = None) -> ResponseGetData:
    """get bootstrap data"""

    url = f'https://{full_auth.domo_instance}.domo.com/api/domoweb/bootstrap?v2Navigation=false'

    res = await get_data(url=url, method='GET', auth=full_auth, debug=debug, session=session)

    if debug:
        res.print(is_pretty=True)

    return res


async def bsr_features(full_auth: DomoFullAuth, session: aiohttp.ClientSession = None, debug: bool = False) -> list[
        dict]:
    res = await get_bootstrap(full_auth=full_auth, session=session, debug=debug)

    if res.status == 200:
        bsr = res.response.get('data').get('features')
        return bsr
