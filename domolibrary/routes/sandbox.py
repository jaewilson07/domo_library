# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/sandbox.ipynb.

# %% auto 0
__all__ = ['get_shared_repos', 'get_repo_from_id']

# %% ../../nbs/routes/sandbox.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/routes/sandbox.ipynb 3
async def get_shared_repos(auth: dmda.DomoAuth, 
                           session: httpx.AsyncClient = None,
                           debug_api: bool = False) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/search"
    
    body = {
        "query": {
            "offset": 0,
            "limit": 50,
            "fieldSearchMap": {},
            "sort": "lastCommit",
            "order": "desc",
            "filters": {
                "userId": None
            },
            "dateFilters": {}
        },
        "shared": False
    }

    res = await gd.get_data(auth=auth,
                         method='POST',
                         url=url,
                         body=body,
                         session=session,
                         debug_api=debug_api)

    return res

# %% ../../nbs/routes/sandbox.ipynb 6
async def get_repo_from_id(auth: dmda.DomoFullAuth,
                           repository_id: str,
                           debug_api: bool = False) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/version/v1/repositories/{repository_id}"

    return await gd.get_data(auth=auth,
                          method='GET',
                          url=url,
                          debug_api=debug_api)

