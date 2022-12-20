import aiohttp
from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


def generate_body_create_group(group_name: str,
                               group_type: str,
                               description: str) -> dict:
    body = {"name": group_name, "type": group_type or 'open',
            "description": description or ''}

    return body


async def create_group(full_auth: DomoFullAuth,
                       group_name: str = None,
                       group_type: str = None,
                       description: str = None,
                       log_results: bool = False, debug: bool = False) -> ResponseGetData:
    # body : {"name": "GROUP_NAME", "type": "open", "description": ""}

    body = generate_body_create_group(
        group_name=group_name, group_type=group_type, description=description)
    print({'create_group_body': body})

    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/groups/'

    if log_results:
        print(f'Creating Group: {body.get("name")}- at {url}')

    res = await get_data(
        auth=full_auth,
        url=url,
        method='POST',
        body=body,
        debug=debug
    )

    return res


async def get_all_groups(full_auth: DomoFullAuth,
                         log_results: bool = False,
                         debug: bool = False,
                         session: aiohttp.ClientSession = None) -> ResponseGetData:
    if debug:
        print(full_auth)

    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/groups/grouplist'

    if debug:
        print(full_auth, url)

    if log_results:
        print(f'Getting groups from - {url}')

    res = await get_data(url=url, method='GET', auth=full_auth, session=session)

    return res


async def search_groups_by_name(full_auth: DomoFullAuth,
                                search_name: str,
                                debug: bool = False, log_results: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/groups/grouplist?ascending=true&search={search_name}&sort=name '

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
        log_results=log_results
    )
    return res


def generate_body_update_group_membership(group_id: str,
                                          add_user_arr: list[str] = None,
                                          remove_user_arr: list[str] = None,
                                          add_owner_user_arr: list[str] = None,
                                          remove_owner_user_arr: list[str] = None) -> list[dict]:
    body = {"groupId": int(group_id)}
    if add_owner_user_arr:
        body.update({"addOwners": [{"type": "USER", "id": str(
            userId)} for userId in add_owner_user_arr]})

    if remove_owner_user_arr:
        body.update({"removeOwners": [{"type": "USER", "id": str(
            userId)} for userId in remove_owner_user_arr]})

    if remove_user_arr:
        body.update({"removeMembers": [
                    {"type": "USER", "id": str(userId)} for userId in remove_user_arr]})
    if add_user_arr:
        body.update(
            {"addMembers": [{"type": "USER", "id": str(userId)} for userId in add_user_arr]})

    return [body]


async def update_group_membership(full_auth: DomoFullAuth,
                                  body: dict,
                                  log_results: bool = False, debug: bool = False) -> ResponseGetData:
    # body = [{
    #     "groupId":"GROUP_ID",
    #     "removeMembers": [{"type":"USER","id":"USER_ID"}],
    #     "addMembers"   : [{"type":"USER","id":"USER_ID"}]
    # }]

    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/groups/access'

    if debug:
        print(url, body)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        debug=debug
    )

    return res

async def get_group_by_id(full_auth:DomoFullAuth, group_id:id, debug:bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/groups/{group_id}'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug
    )

    return res