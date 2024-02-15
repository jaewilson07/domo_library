# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/sandbox.ipynb.

# %% auto 0
__all__ = [
    "get_is_allow_same_instance_promotion_enabled",
    "Sandbox_ToggleSameInstancePromotion_Error",
    "toggle_allow_same_instance_promotion",
    "get_shared_repos",
    "get_repo_from_id",
]

# %% ../../nbs/routes/sandbox.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de


# %% ../../nbs/routes/sandbox.ipynb 4
@gd.route_function
async def get_is_allow_same_instance_promotion_enabled(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_num_stacks_to_drop: int = 1,
    debug_api: bool = False,
    parent_class: str = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/settings"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    res.response = {
        "name": "allow_same_instance_promotion",
        "is_enabled": res.response["allowSelfPromotion"],
    }

    return res


# %% ../../nbs/routes/sandbox.ipynb 6
class Sandbox_ToggleSameInstancePromotion_Error(de.DomoError):
    def __init__(
        self, domo_instance, message, status, parent_class=None, function_name=None
    ):
        super().__init__(
            self,
            domo_instance=domo_instance,
            status=status,
            parent_class=parent_class,
            message=message,
            function_name=function_name,
        )


@gd.route_function
async def toggle_allow_same_instance_promotion(
    is_enabled: bool,
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop: int = 1,
    debug_api: bool = False,
    parent_class: str = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/settings"

    body = {"allowSelfPromotion": is_enabled}

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise Sandbox_ToggleSameInstancePromotion_Error(
            domo_instance=auth.domo_instance,
            message=res.response,
            status=res.status,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res


# %% ../../nbs/routes/sandbox.ipynb 8
@gd.route_function
async def get_shared_repos(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/search"

    body = {
        "query": {
            "offset": 0,
            "limit": 50,
            "fieldSearchMap": {},
            "sort": "lastCommit",
            "order": "desc",
            "filters": {"userId": None},
            "dateFilters": {},
        },
        "shared": False,
    }

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    return res


# %% ../../nbs/routes/sandbox.ipynb 11
@gd.route_function
async def get_repo_from_id(
    auth: dmda.DomoFullAuth,
    repository_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/{repository_id}"

    return await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        parent_class=parent_class,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )
