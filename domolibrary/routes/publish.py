# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/publish.ipynb.

# %% auto 0
__all__ = ['search_publications', 'get_publication_by_id', 'generate_publish_body', 'create_publish_job', 'udpate_publish_job',
           'get_subscription_summaries', 'get_subscription_invititations', 'accept_invite_by_id',
           'accept_invite_by_id_v2', 'refresh_publish_jobs']

# %% ../../nbs/routes/publish.ipynb 2
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/routes/publish.ipynb 4
async def search_publications(
    auth: dmda.DomoAuth,
    search_term: str = None,
    limit=100,
    offset=0,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/summaries"

    params = {"limit": limit, "offset": offset}

    if search_term:
        params.update({"searchTerm": search_term})

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        session=session,
        debug_api=debug_api,
    )

    return res

# %% ../../nbs/routes/publish.ipynb 6
async def get_publication_by_id(
    auth: dmda.DomoAuth,
    publication_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    timeout=10,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}"

    res = await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        session=session,
        timeout=timeout,
        debug_api=debug_api,
    )

    return res


# generate publish body

# %% ../../nbs/routes/publish.ipynb 8
def generate_publish_body(
    url: str,
    sub_domain_ls: [str],
    content_ls: [str],
    name: str,
    description: str,
    unique_id: str,
    is_new: bool,
):
    if not sub_domain_ls:
        sub_domain_ls = []

    if not content_ls:
        content_ls = []

    body = {
        "id": unique_id,
        "name": name,
        "description": description,
        "domain": url,
        "content": content_ls,
        "subscriberDomain": sub_domain_ls,
        "new": str(is_new).lower(),
    }

    return body

# %% ../../nbs/routes/publish.ipynb 10
# Creating publish job for a specific subscriber
async def create_publish_job(
    auth: dmda.DomoAuth,
    body: dict,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication"

    if debug_api:
        print(body)
    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
    )

    return res

# %% ../../nbs/routes/publish.ipynb 11
# Updating existing publish job with content
async def udpate_publish_job(
    auth: dmda.DomoAuth,
    publication_id: str,
    body: dict,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}"

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
    )
    return res


# # finds all jobs waiting to be accepted within the subscriber

# %% ../../nbs/routes/publish.ipynb 13
async def get_subscription_summaries(
    auth: dmda.DomoAuth, session: httpx.AsyncClient = None, debug_api: bool = False
) -> rgd.ResponseGetData:
    """retrieves a summary of existing subscriptions"""
    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/summaries"

    res = await gd.get_data(
        auth=auth, method="GET", url=url, session=session, debug_api=debug_api
    )
    return res

# %% ../../nbs/routes/publish.ipynb 15
async def get_subscription_invititations(
    auth: dmda.DomoAuth, session: httpx.AsyncClient = None, debug_api: bool = False
) -> rgd.ResponseGetData:
    """retrieves a list of subscription invitations"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/invites"

    res = await gd.get_data(
        auth=auth, method="GET", url=url, session=session, debug_api=debug_api
    )
    return res

# %% ../../nbs/routes/publish.ipynb 18
async def accept_invite_by_id(
    auth: dmda.DomoAuth,
    subscription_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    """this takes get_subscription_invites_list into account and accepts - not instant"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscription/{subscription_id}"

    res = await gd.get_data(
        auth=auth, method="POST", url=url, session=session, debug_api=debug_api
    )
    return res

# %% ../../nbs/routes/publish.ipynb 19
async def accept_invite_by_id_v2(
    auth: dmda.DomoAuth,
    publication_id: str,
    owner_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    """this takes get_subscription_invites_list into account and accepts - not instant"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/subscriptions/v2"

    body = {
        "publicationId": publication_id,
        "customerId": "",
        "domain": "",
        "groupIds": [],
        "userId": owner_id,
        "userIds": [],
    }

    res = await gd.get_data(
        auth=auth,
        method="POST",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
    )
    return res

# %% ../../nbs/routes/publish.ipynb 20
async def refresh_publish_jobs(
    auth: dmda.DomoAuth,
    publish_ids: list,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    """Refreshing list of publish jobs. Typically "instance" = publisher instance"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/publication/refresh"

    body = {"publicationIds": publish_ids}

    res = await gd.get_data(
        auth=auth,
        method="PUT",
        url=url,
        body=body,
        session=session,
        debug_api=debug_api,
    )
    return res
