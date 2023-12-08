# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/role.ipynb.

# %% auto 0
__all__ = ['Role_NotRetrieved', 'Role_CRUD_Error', 'get_roles', 'get_role_by_id', 'get_role_grants', 'get_role_membership',
           'create_role', 'delete_role', 'get_default_role', 'set_default_role', 'update_role_metadata',
           'set_role_grants', 'role_membership_add_users']

# %% ../../nbs/routes/role.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/role.ipynb 4
class Role_NotRetrieved(de.DomoError):
    def __init__(
        self,
        domo_instance,
        function_name,
        status,
        message,
        role_id=None,
    ):
        super().__init__(
            domo_instance=domo_instance,
            entity_id=role_id,
            function_name=function_name,
            status=status,
            message=message,
        )


# | export
class Role_CRUD_Error(de.DomoError):
    def __init__(
        self,
        domo_instance,
        function_name,
        status,
        message,
        role_id=None,
    ):
        super().__init__(
            domo_instance=domo_instance,
            entity_id=role_id,
            function_name=function_name,
            status=status,
            message=message,
        )

# %% ../../nbs/routes/role.ipynb 5
@gd.route_function
async def get_roles(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if not res.is_success:
        raise Role_NotRetrieved(
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            status=res.status,
            message=res.response,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/role.ipynb 8
@gd.route_function
async def get_role_by_id(
    auth: dmda.DomoAuth,
    role_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_NotRetrieved(
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            status=res.status,
            message=res.response,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/role.ipynb 10
@gd.route_function
async def get_role_grants(
    auth: dmda.DomoAuth,
    role_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if len(res.response) == 0:
        role_res = await get_roles(auth=auth)

        domo_role = [role for role in role_res.response if role.get("id") == role_id]

        if not domo_role:
            raise Role_NotRetrieved(
                domo_instance=auth.domo_instance,
                function_name=res.traceback_details.function_name,
                message=f"role {role_id} does not exist",
                status=res.status,
                parent_class=parent_class,
            )

    return res

# %% ../../nbs/routes/role.ipynb 13
@gd.route_function
async def get_role_membership(
    auth: dmda.DomoAuth,
    role_id: str,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if len(res.response.get("users")) == 0:
        role_res = await get_roles(auth)

        domo_role = next(
            (role for role in role_res.response if role.get("id") == role_id), None
        )

        if not domo_role:
            raise Role_NotRetrieved(
                domo_instance=auth.domo_instance,
                function_name=res.traceback_details.function_name,
                message=f"role {role_id} does not exist or cannot be retrieved",
                status=res.status,
                parent_class=parent_class,
            )

    if return_raw:
        return res

    res.response = res.response.get("users")

    return res

# %% ../../nbs/routes/role.ipynb 17
@gd.route_function
async def create_role(
    auth: dmda.DomoAuth,
    name: str,
    description: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles"

    body = {"name": name, "description": description}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_CRUD_Error(
            domo_instance=auth.domo_auth,
            function_name=res.traceback_deails.function_name,
            status=res.status,
            message=res.response,
        )

    return res

# %% ../../nbs/routes/role.ipynb 18
@gd.route_function
async def delete_role(
    auth: dmda.DomoAuth,
    role_id: int,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_CRUD_Error(
            domo_instance=auth.domo_auth,
            function_name=res.traceback_deails.function_name,
            status=res.status,
            message=res.response,
        )

    res.response = f"role {role_id} deleted or doesn't exist"

    return res

# %% ../../nbs/routes/role.ipynb 22
@gd.route_function
async def get_default_role(
    auth,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default"

    params = {"defaultValue": 2, "ignoreCache": True}

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_NotRetrieved(
            domo_instance=auth.domo_auth,
            function_name=res.traceback_deails.function_name,
            status=res.status,
            message=res.response,
        )

    res.response = res.response.get("value")

    return res

# %% ../../nbs/routes/role.ipynb 25
@gd.route_function
async def set_default_role(
    auth: dmda.DomoAuth,
    role_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class=None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/user.roleid.default"

    body = {"name": "user.roleid.default", "value": role_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        debug_api=debug_api,
        body=body,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise Role_CRUD_Error(
            domo_instance=auth.domo_auth,
            function_name=res.traceback_deails.function_name,
            status=res.status,
            message=res.response,
        )

    return res

# %% ../../nbs/routes/role.ipynb 27
@gd.route_function
async def update_role_metadata(
    auth: dmda.DomoAuth,
    role_id,
    role_name,
    role_description: str = None,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop : int = 1,
    parent_class : str = None
):
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}"

    body = {"name": role_name, "description": role_description, "id": role_id}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop = debug_num_stacks_to_drop,
        parent_class = parent_class
    )

    if not res.is_success:
        raise Role_CRUD_Error(domo_instance = auth.domo_auth,
                 function_name = res.traceback_deails.function_name,
                 status = res.status,
                 message = res.response)

    return res

# %% ../../nbs/routes/role.ipynb 30
@gd.route_function
async def set_role_grants(
    auth: dmda.DomoAuth, role_id: str, 
    role_grant_ls: list[str], 
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop : int = 1,
    parent_class : str = None
    
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/authorities"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth, url=url, method="PUT", 
        body=role_grant_ls,
        session=session,
        debug_api=debug_api,
        parent_class = parent_class,
        num_stacks_to_drop = debug_num_stacks_to_drop 
    )

    if not res.is_success:
        raise Role_CRUD_Error(domo_instance = auth.domo_auth,
                 function_name = res.traceback_deails.function_name,
                 status = res.status,
                 message = res.response)

    return res

# %% ../../nbs/routes/role.ipynb 31
@gd.route_function
async def role_membership_add_users(
    auth: dmda.DomoAuth,
    role_id: str,
    user_list: list[str],  # list of user ids
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop : int = 1,
    parent_class :str = None
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/authorization/v1/roles/{role_id}/users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=user_list,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop = debug_num_stacks_to_drop,
        parent_class = parent_class
    )

    if not res.is_success:
        raise Role_CRUD_Error(domo_instance = auth.domo_auth,
                 function_name = res.traceback_deails.function_name,
                 status = res.status,
                 message = res.response)

    return res
