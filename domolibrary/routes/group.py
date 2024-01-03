# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/group.ipynb.

# %% auto 0
__all__ = [
    "SearchGroups_Error",
    "search_groups_by_name",
    "get_all_groups",
    "get_group_by_id",
    "toggle_system_group_visibility",
    "Group_CRUD_Error",
    "GroupType_Enum",
    "generate_body_create_group",
    "create_group",
    "update_group",
    "delete_groups",
    "get_group_owners",
    "get_group_membership",
    "generate_body_update_group_membership",
    "update_group_membership",
]

# %% ../../nbs/routes/group.ipynb 2
import httpx
from enum import Enum
from typing import Union, List

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de


# %% ../../nbs/routes/group.ipynb 5
class SearchGroups_Error(de.DomoError):
    def __init__(
        self,
        status,
        message,
        domo_instance,
        function_name="search_groups_by_name",
        parent_class: str = None,
    ):
        super().__init__(
            function_name=function_name,
            status=status,
            message=message,
            domo_instance=domo_instance,
            parent_class=parent_class,
        )


@gd.route_function
async def search_groups_by_name(
    auth: dmda.DomoAuth,
    search_name: str,
    is_exact_match: bool = True,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    """uses /content/v2/groups/grouplist api -- includes user details"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/grouplist?ascending=true&search={search_name}&sort=name "

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )
    if not is_exact_match:
        return res

    match_group = next(
        (group for group in res.response if group.get("name") == search_name), None
    )
    # print(match_group)

    if not match_group:
        raise SearchGroups_Error(
            status=res.status,
            message=f"There is no exact match for {search_name}",
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )
    res.response = match_group

    return res


# %% ../../nbs/routes/group.ipynb 8
@gd.route_function
async def get_all_groups(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_loop: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    """uses /content/v2/groups/grouplist api -- includes user details"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/grouplist"

    def arr_fn(res):
        return res.response

    res = await gd.looper(
        offset_params={"offset": "offset", "limit": "limit"},
        arr_fn=arr_fn,
        loop_until_end=True,
        limit=30,
        url=url,
        method="GET",
        auth=auth,
        session=session,
        debug_loop=debug_loop,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    return res


# %% ../../nbs/routes/group.ipynb 11
@gd.route_function
async def get_group_by_id(
    auth: dmda.DomoAuth,
    group_id: str,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:

    """uses /content/v2/groups/ api -- does not return details"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/{group_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if res.status == 404 and res.response == "Not Found":
        raise SearchGroups_Error(
            status=res.status,
            message=f"group {group_id} not found",
            domo_instance=auth.domo_instance,
            function_name="get_group_by_id",
        )

    return res


# %% ../../nbs/routes/group.ipynb 13
@gd.route_function
async def toggle_system_group_visibility(
    auth,
    is_hide_system_groups: bool,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
):
    print(
        f"toggling group visiblity in {auth.domo_instance} { 'hiding system groups' if is_hide_system_groups else 'show system groups'}"
    )

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/setVisibility"

    await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body={"type": "system", "hidden": is_hide_system_groups},
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=parent_class,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/groups.system.enabled"

    return await gd.get_data(
        url=url,
        auth=auth,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
        parent_class=parent_class,
    )


# %% ../../nbs/routes/group.ipynb 17
class Group_CRUD_Error(de.DomoError):
    def __init__(
        self,
        status,
        message,
        domo_instance,
        function_name="create_group",
        parent_class: str = None,
    ):
        super().__init__(
            function_name=function_name,
            status=status,
            message=message,
            domo_instance=domo_instance,
            parent_class=parent_class,
        )


class GroupType_Enum(Enum):
    OPEN = "open"
    ADHOC = "adHoc"
    CLOSED = "closed"
    DIRECTORY = "directory"
    DYNAMIC = "dynamic"
    SYSYTEM = "system"


def generate_body_create_group(
    group_name: str, group_type: str = "open", description: str = ""
) -> dict:
    """Generates the body to create group for content_v2_group API"""
    body = {"name": group_name, "type": group_type, "description": description}

    return body


# %% ../../nbs/routes/group.ipynb 20
@gd.route_function
async def create_group(
    auth: dmda.DomoAuth,
    group_name: str,
    group_type: str = "open",
    description: str = "",
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    # body : {"name": "GROUP_NAME", "type": "open", "description": ""}

    body = generate_body_create_group(
        group_name=group_name, group_type=group_type, description=description
    )
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        try:
            group_exists = await search_groups_by_name(
                auth=auth, search_name=group_name, is_exact_match=True
            )

            if group_exists.is_success:
                raise Group_CRUD_Error(
                    status=res.status,
                    message=f"{group_name} already exists. Choose a different group_name",
                    function_name=res.traceback_details.function_name,
                    parent_class=parent_class,
                    domo_instance=auth.domo_instance,
                )

        except SearchGroups_Error as e:
            raise Group_CRUD_Error(
                status=res.status,
                message=res.response,
                domo_instance=auth.domo_instance,
                function_name=res.traceback_details.function_name,
                parent_class=parent_class,
            )

    return res


# %% ../../nbs/routes/group.ipynb 23
@gd.route_function
async def update_group(
    auth: dmda.DomoAuth,
    group_id: int,
    group_name: str = None,
    group_type: str = None,
    description: str = None,
    additional_params: dict = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
) -> rgd.ResponseGetData:

    s = {"groupId": int(group_id)}

    if group_name:
        s.update({"name": group_name})

    if group_type:
        s.update({"type": group_type})

    if description:
        s.update({"description": description})

    if additional_params and isinstance(additional_params, dict):
        s.update({**additional_params})
        pass

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=[s],
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if group_name and res.status == 400:
        raise Group_CRUD_Error(
            status=res.status,
            message="are you trying to create an account with a duplicate name?",
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    if not res.is_success:
        raise Group_CRUD_Error(
            status=res.status,
            message=res.response,
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    res.response = f"updated {group_id} from {auth.domo_instance}"
    return res


# %% ../../nbs/routes/group.ipynb 27
@gd.route_function
async def delete_groups(
    auth: dmda.DomoAuth,
    group_ids: List[str],  # list of group_ids
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    return_raw: bool = False,
) -> rgd.ResponseGetData:

    group_ids = group_ids if isinstance(group_ids, list) else [str(group_ids)]

    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        body=group_ids,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Group_CRUD_Error(
            status=res.status,
            message=f"failed to delete {', '.join(group_ids)}",
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
        )

    res.response = f"deleted {', '.join(group_ids)} from {auth.domo_instance}"
    return res


# %% ../../nbs/routes/group.ipynb 31
@gd.route_function
async def get_group_owners(
    auth: dmda.DomoAuth,
    group_id: str,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:

    # url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/users?group={group_id}"
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/permissions?checkOwnership=true&includeUsers=false"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=[str(group_id)],
        method="POST",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    res.response = res.response[0].get("permissions").get("owners")
    return res


# %% ../../nbs/routes/group.ipynb 34
@gd.route_function
async def get_group_membership(
    auth: dmda.DomoAuth,
    group_id: str,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:

    # url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/users?group={group_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    res.response = res.response.get("groupUserList")
    return res


# %% ../../nbs/routes/group.ipynb 38
def generate_body_update_group_membership_entity(
    user_id: Union[str, int], user_type: str  # USER or GROUP
):
    if user_type == "USER":
        return {"type": "USER", "id": str(user_id)}
    elif user_type == "GROUP":
        return {"type": "GROUP", "id": int(user_id)}


# %% ../../nbs/routes/group.ipynb 39
def generate_body_update_group_membership(
    group_id: str,
    add_member_arr: list[str] = None,
    remove_member_arr: list[str] = None,
    add_owner_arr: list[str] = None,
    remove_owner_arr: list[str] = None,
) -> list[dict]:
    """
    each member or owner obj should be an object of shape {"type", "id"}
    """

    body = {"groupId": int(group_id)}

    if add_owner_arr and len(add_owner_arr) > 0:
        body.update(
            {
                "addOwners": [
                    generate_body_update_group_membership_entity(
                        user_id=obj.get("id"), user_type=obj.get("type")
                    )
                    for obj in add_owner_arr
                ]
            }
        )

    if remove_owner_arr and len(remove_owner_arr) > 0:
        body.update(
            {
                "removeOwners": [
                    generate_body_update_group_membership_entity(
                        user_id=obj.get("id"), user_type=obj.get("type")
                    )
                    for obj in remove_owner_arr
                ]
            }
        )

    if remove_member_arr and len(remove_member_arr) > 0:
        body.update(
            {
                "removeMembers": [
                    generate_body_update_group_membership_entity(
                        user_id=obj.get("id"), user_type=obj.get("type")
                    )
                    for obj in remove_member_arr
                ]
            }
        )
    if add_member_arr and len(add_member_arr) > 0:
        body.update(
            {
                "addMembers": [
                    generate_body_update_group_membership_entity(
                        user_id=obj.get("id"), user_type=obj.get("type")
                    )
                    for obj in add_member_arr
                ]
            }
        )

    return [body]


# %% ../../nbs/routes/group.ipynb 40
gd.route_function


async def update_group_membership(
    auth: dmda.DomoAuth,
    group_id: str,
    add_member_arr: list[dict] = None,
    remove_member_arr: list[dict] = None,
    add_owner_arr: list[dict] = None,
    remove_owner_arr: list[dict] = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
) -> rgd.ResponseGetData:

    """
    each member or owner obj should be an object of shape {"type", "id"}
    """

    body = generate_body_update_group_membership(
        group_id=group_id,
        add_member_arr=add_member_arr,
        remove_member_arr=remove_member_arr,
        add_owner_arr=add_owner_arr,
        remove_owner_arr=remove_owner_arr,
    )

    # body = [{
    #     "groupId":"GROUP_ID",
    #     "removeMembers": [{"type":"USER","id":"USER_ID"}],
    #     "addMembers"   : [{"type":"USER","id":"USER_ID"}]
    # }]
    url = f"https://{auth.domo_instance}.domo.com/api/content/v2/groups/access"

    if debug_api:
        print(url, body)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    return res
