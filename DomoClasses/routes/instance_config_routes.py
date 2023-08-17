import aiohttp

from .get_data import get_data, looper
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_whitelist(full_auth: DomoFullAuth,
                        session: aiohttp.ClientSession = None,
                        debug: bool = False,
                        log_results: bool = False
                        ) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/admin/companysettings/whitelist'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        session=session,
        debug=False
    )

    return res


async def update_whitelist(full_auth: DomoFullAuth,
                           ip_address_list: list[str],
                           debug: bool = False,
                           log_results: bool = False
                           ) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/admin/companysettings/whitelist'

    body = {'addresses': ip_address_list}

    if debug:
        print(url)
        print(body)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        log_results=log_results,
        debug=debug
    )

    return res


async def update_authorized_domains(full_auth: DomoFullAuth, authorized_domain_list: list[str],
                                    debug: bool = False, log_results: bool = False,
                                    session: aiohttp.ClientSession = None):
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-domains'

    body = {
        "name": "authorized-domains",
        "value": ",".join(authorized_domain_list)
    }

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        log_results=log_results,
        debug=debug,
        session=session
    )

    return res


async def get_authorized_domains(full_auth: DomoFullAuth,
                                 debug: bool = False, log_results: bool = False,
                                 session: aiohttp.ClientSession = None
                                 ):
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-domains'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )

    return res
