from pprint import pprint

import aiohttp

from ...DomoClasses import DomoAuth as dmda
from ...utils import ResponseGetData as ResponseGetData
from . import get_data as gd


async def search_activity_log(full_auth: dmda.DomoFullAuth,
                              end_time: int,
                              start_time: int,
                              maximum: int, object_type=None,
                              session: aiohttp.ClientSession = None,
                              debug: bool = False):
    is_close_session = False

    if not session:
        session = aiohttp.ClientSession()
        is_close_session = True

    url = f'https://{full_auth.domo_instance}.domo.com/api/audit/v1/user-audits/{object_type if object_type else ""}'

    fixed_params = {
        'end': end_time,
        'start': start_time

    }

    offset_params = {
        'offset': 'offset',
        'limit': 'limit',
    }

    def arr_fn(res) -> list[dict]:
        return res.response

    res = await gd.looper(auth=full_auth,
                          method='GET',
                          url=url,
                          arr_fn=arr_fn,
                          fixed_params=fixed_params,
                          offset_params=offset_params,
                          session=session,
                          maximum=maximum, debug=debug)

    if is_close_session:
        await session.close()

    return res
