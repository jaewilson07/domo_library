import aiohttp

from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_roles(full_auth: DomoFullAuth,
                    debug: bool = False,
                    session: aiohttp.ClientSession = None,
                    ) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/roles'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
        session=session
    )
    return res


async def create_role(full_auth: DomoFullAuth,
                      name: str,
                      description: str,
                      debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/roles'

    body = {
        'name': name,
        'description': description
    }

    if debug:
        print(url)
        print({"body": body})

    res = await get_data(
        auth=full_auth,
        url=url,
        method='POST',
        debug=debug,
        body=body
    )

    return res


async def set_default_role(full_auth: DomoFullAuth,
                           role_id: str,
                           debug: bool = False,
                           session: aiohttp.ClientSession = None) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default'

    body = {
        'name': 'user.roleid.default',
        'value': role_id
    }

    if debug:
        print(url)
        print({"body": body})

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        debug=debug,
        body=body,
        session=session
    )
    return res


async def get_role_grants(full_auth: DomoFullAuth,
                          role_id: str,
                          debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
    )
    return res


async def update_role_grants(full_auth: DomoFullAuth,
                             role_id: str,
                             role_grant_list: list[str],
                             debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities'

    if debug:
        print(url)

    res = await get_data(auth=full_auth,
                         url=url,
                         method='PUT',
                         debug=debug, body=role_grant_list)
    return res


async def role_membership_add_user(full_auth: DomoFullAuth,
                                   role_id: str,
                                   user_list: list[str],
                                   debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        debug=debug,
        body=user_list
    )
    return res


async def get_role_membership(full_auth: DomoFullAuth,
                              role_id: str,
                              debug: bool = False, session: aiohttp.ClientSession = None) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
        session=session
    )
    return res
