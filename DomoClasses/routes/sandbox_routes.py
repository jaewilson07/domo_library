import aiohttp

import Library.DomoClasses.DomoAuth as dmda
import Library.utils.ResponseGetData as rgd

from Library.DomoClasses.routes.get_data import get_data


async def get_shared_repos(full_auth: dmda.DomoFullAuth, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/version/v1/repositories/search"
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

    res = await get_data(auth=full_auth,
                         method='POST',
                         url=url,
                         body=body,
                         session=session,
                         debug=debug)

    return res


async def get_repo_from_id(full_auth: dmda.DomoFullAuth,
                           repository_id: str,
                           debug: bool = False) -> rgd.ResponseGetData:

    url = f"https://{full_auth.domo_instance}.domo.com/api/version/v1/repositories/{repository_id}"

    return await get_data(auth=full_auth,
                          method='GET',
                          url=url,
                          debug=debug)


async def get_shared_repos(full_auth: dmda.DomoFullAuth, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/version/v1/repositories/search"
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

    res = await get_data(auth=full_auth,
                         method='POST',
                         url=url,
                         body=body,
                         session=session,
                         debug=debug)

    return res
