# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/group.ipynb.

# %% auto 0
__all__ = ['generate_body_create_group', 'search_groups_by_name', 'CreateGroup_Error', 'create_group', 'get_all_groups',
           'generate_body_update_group_membership', 'update_group_membership']

# %% ../../nbs/routes/group.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/group.ipynb 3
def generate_body_create_group(group_name: str,
                               group_type: str = 'open',
                               description: str = '') -> dict:
    """ Generates the body to create group for content_v2_group API"""
    body = {"name": group_name, 
            "type": group_type,
            "description": description}

    return body

# %% ../../nbs/routes/group.ipynb 6
async def search_groups_by_name(auth: dmda.DomoAuth,
                                search_name: str,
                                debug_api: bool = False, 
                                log_results: bool = False) -> rgd.ResponseGetData:
    url = f'https://{auth.domo_instance}.domo.com/api/content/v2/groups/grouplist?ascending=true&search={search_name}&sort=name '

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        debug_api=debug_api
    )
    return res

# %% ../../nbs/routes/group.ipynb 9
class CreateGroup_Error(de.DomoError):
    def __init__(self, status, message, domo_instance, function_name = "create_group"):
        super().__init__(function_name = function_name, status = status, message = message , domo_instance = domo_instance)

async def create_group(auth: dmda.DomoAuth,
                       group_name: str,
                       group_type: str = 'open',
                       description: str = '',
                       debug_api: bool = False,
                       session: httpx.AsyncClient = None
                       ) -> rgd.ResponseGetData:
    # body : {"name": "GROUP_NAME", "type": "open", "description": ""}

    body = generate_body_create_group(
        group_name=group_name, group_type=group_type, description=description)

    url = f'https://{auth.domo_instance}.domo.com/api/content/v2/groups/'

    res= await gd.get_data(
        auth=auth,
        url=url,
        method='POST',
        body=body,
        debug_api=debug_api,
        session = session
    )

    if not res.is_success:
        group_exists = await search_groups_by_name(auth=auth, search_name=group_name)
        if group_exists.is_success:
            raise CreateGroup_Error(
                status = res.status,
                message = f'{group_name} already exists. Choose a different group_name',
                domo_instance = auth.domo_instance,
                function_name='create_group'
            )

    if not res.is_success:
        raise CreateGroup_Error(
            status = res.status, 
            message = res.response,
            domo_instance = auth.domo_instance, 
            function_name="create_group")

    return res


# %% ../../nbs/routes/group.ipynb 12
async def get_all_groups(auth: dmda.DomoAuth,
                         log_results: bool = False,
                         debug_api: bool = False,
                         session: httpx.AsyncClient = None) -> rgd.ResponseGetData:
    if debug_api:
        print(auth)

    url = f'https://{auth.domo_instance}.domo.com/api/content/v2/groups/grouplist'

    if debug_api:
        print(auth, url)

    if log_results:
        print(f'Getting groups from - {url}')

    res = await gd.get_data(url=url, method='GET', auth=auth, session=session)

    return res

# %% ../../nbs/routes/group.ipynb 15
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

# %% ../../nbs/routes/group.ipynb 16
async def update_group_membership(auth: dmda.DomoAuth,
                                  body: dict, # first need to create body with generate_body_update_group_membership() 
                                  log_results: bool = False, 
                                  debug_api: bool = False) -> rgd.ResponseGetData:
    # body = [{
    #     "groupId":"GROUP_ID",
    #     "removeMembers": [{"type":"USER","id":"USER_ID"}],
    #     "addMembers"   : [{"type":"USER","id":"USER_ID"}]
    # }]

    url = f'https://{auth.domo_instance}.domo.com/api/content/v2/groups/access'

    if debug_api:
        print(url, body)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        body=body,
        debug_api=debug_api
    )

    return res
