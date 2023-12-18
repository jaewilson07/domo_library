# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/page.ipynb.

# %% auto 0
__all__ = ['PageRetrieval_byId_Error', 'get_page_by_id', 'get_page_definition', 'get_page_access_test', 'get_page_access_list',
           'get_pages_adminsummary', 'update_page_layout', 'put_writelock', 'delete_writelock', 'add_page_owner']

# %% ../../nbs/routes/page.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de


# %% ../../nbs/routes/page.ipynb 5
class PageRetrieval_byId_Error(de.DomoError):
    def __init__(
        self,
        status,
        domo_instance,
        page_id,
        response,
        function_name=None,
        parent_class=None,
    ):
        super().__init__(
            status=status,
            function_name=function_name,
            parent_class=parent_class,
            message=f"failed to retrieve page_id: {page_id}",
            domo_instance = domo_instance
        )

# %% ../../nbs/routes/page.ipynb 8
async def get_page_by_id(
    auth: dmda.DomoAuth,
    page_id: str,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    include_layout: bool = False,  # passes parameter to return page layout information
    debug_num_stacks_to_drop: int = 1,  # for traceback_details.  use 1 for route functions, 2 for class method
    parent_class: str = None,  # pass in self.__class__.__name__ into function
) -> rgd.ResponseGetData:  # returns ResponseGetData on success or raise Exception on error
    """retrieves a page or throws an error"""

    # 9/21/2023 - the domo UI uses /cards to get page info
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/stacks/{page_id}/cards"

    if include_layout:
        url += "?includeV4PageLayouts=true"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if (
        not res.is_success
        or not isinstance(res.response, dict)
        or not res.response.get("id", None)
    ):
        raise PageRetrieval_byId_Error(
            status=res.status,
            page_id=page_id,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
            response=res.response,
        )

    return res

# %% ../../nbs/routes/page.ipynb 12
async def get_page_definition(
    auth: dmda.DomoAuth,
    page_id: int,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/stacks/{page_id}/cards"

    params = {
        "includeV4PageLayouts": "true",
        "parts": "metadata,datasources,library,drillPathURNs,certification,owners,dateInfo,subscriptions,slicers",
    }

    res = await gd.get_data(
        url,
        method="GET",
        auth=auth,
        session=session,
        params=params,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if (
        not res.is_success
        or not isinstance(res.response, dict)
        or not res.response.get("id", None)
    ):
        raise PageRetrieval_byId_Error(
            status=res.status,
            page_id=page_id,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
            response=res.response,
        )

    return res

# %% ../../nbs/routes/page.ipynb 16
async def get_page_access_test(
    auth,
    page_id,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
):
    """retrieves accesslist, which users and groups a page is shared with"""
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/pages/{page_id}/access"

    res = await gd.get_data(
        url,
        method="GET",
        auth=auth,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    return res

# %% ../../nbs/routes/page.ipynb 19
async def get_page_access_list(
    auth,
    page_id,
    is_expand_users: bool = True,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
):
    """retrieves accesslist, which users and groups a page is shared with"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/share/accesslist/page/{page_id}?expandUsers={is_expand_users}"

    res = await gd.get_data(
        url,
        method="GET",
        auth=auth,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    res.response["explicitSharedUserCount"] = len(res.response.get("users"))
    for user in res.response.get("users"):
        user.update({"isExplicitShare": True})

    # add group members to users response
    if is_expand_users:
        group_users = [
            {**user, "isExplicitShare": False}
            for group in res.response.get("groups")
            for user in group.get("users")
        ]
        users = res.response.get("users") + [
            group_user
            for group_user in group_users
            if group_user.get("id")
            not in [user.get("id") for user in res.response.get("users")]
        ]
        res.response.update({"users": users})

    return res

# %% ../../nbs/routes/page.ipynb 22
async def get_pages_adminsummary(
    auth: dmda.DomoAuth,
    debug_loop: bool = False,
    debug_api: bool = False,
    limit=35,
    session: httpx.AsyncClient = None,
):
    """retrieves all pages in instance user is able to see (but may not have been explicitly shared)"""

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/pages/adminsummary"

    offset_params = {
        "offset": "skip",
        "limit": "limit",
    }

    body = {"orderBy": "pageTitle", "ascending": True}

    def arr_fn(res) -> list[dict]:
        return res.response.get("pageAdminSummaries")

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        session=session,
        loop_until_end=True,
        body=body,
        limit=limit,
        debug_loop=debug_loop,
        debug_api=debug_api,
    )
    return res


# %% ../../nbs/routes/page.ipynb 24
async def update_page_layout(
    auth: dmda.DomoAuth, layout_id: str, body: dict, debug_api: bool = False
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v4/pages/layouts/{layout_id}"

    res = await gd.get_data(
        auth=auth, url=url, body=body, method="PUT", debug_api=debug_api
    )

    if debug_api:
        print(res)

    return res


async def put_writelock(
    auth: dmda.DomoAuth,
    layout_id: str,
    user_id: str,
    epoch_time: int,
    debug_api: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v4/pages/layouts/{layout_id}/writelock"
    body = {
        "layoutId": layout_id,
        "lockHeartbeat": epoch_time,
        "lockTimestamp": epoch_time,
        "userId": user_id,
    }

    res = await gd.get_data(
        auth=auth, url=url, body=body, method="PUT", debug_api=debug_api
    )

    if debug_api:
        print(res)

    return res


async def delete_writelock(
    auth: dmda.DomoAuth, layout_id: str, debug_api: bool = False
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v4/pages/layouts/{layout_id}/writelock"
    res = await gd.get_data(auth=auth, url=url, method="DELETE", debug_api=debug_api)

    if debug_api:
        print(res)

    return res


# %% ../../nbs/routes/page.ipynb 25
async def add_page_owner(auth: dmda.DomoAuth,
                        page_id_ls : [],
                        group_id_ls: [],
                        user_id_ls:[],
                        note: str = "",
                        send_email: bool = False,
                        session: httpx.AsyncClient = None, debug_api: bool = False) -> rgd.ResponseGetData:


    url = f'https://{auth.domo_instance}.domo.com/api/content/v1/pages/bulk/owners'
    owners = []
    for group in group_id_ls:
        owners.append({"id":group,"type":"GROUP"})
    for user in user_id_ls:
        owners.append({"id":user,"type":"USER"})
    

    body = {"pageIds":page_id_ls,  
            "owners": owners, 
            "note": note,
            "sendEmail": send_email
             }
    
    res = await gd.get_data(auth=auth,
                        method='PUT',
                        url=url,
                        body = body,
                        session=session,
                        debug_api=debug_api)
    return res



