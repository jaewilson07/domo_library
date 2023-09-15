# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/bootstrap.ipynb.

# %% auto 0
__all__ = ['get_bootstrap', 'get_bootstrap_features', 'get_bootstrap_pages']

# %% ../../nbs/routes/bootstrap.ipynb 3
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/routes/bootstrap.ipynb 4
async def get_bootstrap(
    auth: dmda.DomoFullAuth, ## only works with DomoFullAuth authentication, do not use TokenAuth
    debug_api: bool = False, 
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    parent_class = None,
    debug_num_stacks_to_drop = 1
) -> rgd.ResponseGetData:
    """get bootstrap data"""

    dmda.test_is_full_auth(auth, num_stacks_to_drop=1)

    # url = f"https://{auth.domo_instance}.domo.com/api/domoweb/bootstrap?v2Navigation=false"
    url = f"https://{auth.domo_instance}.domo.com/api/domoweb/bootstrap?v2Navigation=true"

    res = await gd.get_data(
        url=url, method="GET", auth=auth, debug_api=debug_api, session=session, is_follow_redirects = True, num_stacks_to_drop = debug_num_stacks_to_drop, parent_class = parent_class
    )

    if res.response == '' and not return_raw:
        raise Exception('BSR_Features:  no features returned - is there a VPN?')

    return res


# %% ../../nbs/routes/bootstrap.ipynb 8
async def get_bootstrap_features(
    auth: dmda.DomoAuth, session: httpx.AsyncClient = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_num_stacks_to_drop = 2,
    parent_class = None
) -> rgd.ResponseGetData:

    res = await get_bootstrap(auth=auth, session=session, debug_api=debug_api, return_raw=return_raw, debug_num_stacks_to_drop = debug_num_stacks_to_drop, parent_class= parent_class)

    if return_raw:
        return res

    if not res.is_success:
        return None

    res.response = res.response.get("data").get("features")
    return res


# %% ../../nbs/routes/bootstrap.ipynb 11
async def get_bootstrap_pages(
    auth: dmda.DomoAuth, session: httpx.AsyncClient = None, debug_api: bool = False, return_raw: bool = False, debug_num_stacks_to_drop= 2, parent_class = None
) -> rgd.ResponseGetData:
    res = await get_bootstrap(auth=auth, session=session, debug_api=debug_api, debug_num_stacks_to_drop= debug_num_stacks_to_drop, parent_class = parent_class)

    if return_raw:
        return res
        
    if not res.is_success:
        return None

    res.response = res.response.get("data").get("pages")
    return res

