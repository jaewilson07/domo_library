import aiohttp

import Library.DomoClasses.DomoAuth as dmda
import Library.utils.ResponseGetData as rgd

from Library.DomoClasses.routes.get_data import get_data


async def search_publications(full_auth: dmda.DomoFullAuth, search_term: str = None, limit=100, offset=0, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication/summaries"

    params = {'limit': limit, 'offset': offset}

    if search_term:
        params.update({'searchTerm': search_term})

    res = await get_data(auth=full_auth,
                         method='GET',
                         url=url,
                         params=params,
                         session=session,
                         debug=debug)

    return res


async def get_publication_by_id(full_auth: dmda.DomoFullAuth, publication_id: str, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}"

    res = await get_data(auth=full_auth,
                         method='GET',
                         url=url,
                         session=session,
                         debug=debug)

    return res


# generate publish body
def generate_publish_body(url: str, sub_domain_ls: [str], content_ls: [str], name: str, description: str, unique_id: str, is_new: bool):
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
        "new": str(is_new).lower()
    }

    return body

# Creating publish job for a specific subscriber

async def create_publish_job(full_auth: dmda.DomoFullAuth, body : dict, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication'

    print (body)
    res = await get_data(auth=full_auth,
                         method='POST',
                         url=url,
                         body=body,
                         session=session,
                         debug=debug)

    return res

# Updating existing publish job with content

async def udpate_publish_job(full_auth: dmda.DomoFullAuth, publication_id: str, body: dict, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:

    url = f'https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}'
    
    res = await get_data(auth=full_auth,
                         method='PUT',
                         url=url,
                         body=body,
                         session=session,
                         debug=debug)
    return res

# finds all jobs waiting to be accepted within the subscriber

async def get_subscription_invites_list(full_auth: dmda.DomoFullAuth, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:

    url = f'https://{full_auth.domo_instance}.domo.com/api/publish/v2/subscription/invites'

    res = await get_data(auth=full_auth,
                         method='GET',
                         url=url,
                         session=session,
                         debug=debug)
    return res

# this takes get_subscription_invites_list into account and accepts - not instant


async def accept_invite_by_id(full_auth: dmda.DomoFullAuth, subscription_id: str, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:

    url = f'https://{full_auth.domo_instance}.domo.com/api/publish/v2/subscription/{subscription_id}'

    res = await get_data(auth=full_auth,
                         method='POST',
                         url=url,
                         session=session,
                         debug=debug)
    return res


# Refreshing list of publish jobs. Typically "instance" = publisher instance


async def refresh_publish_jobs(full_auth: dmda.DomoFullAuth, publish_ids: list, session: aiohttp.ClientSession = None, debug: bool = False) -> rgd.ResponseGetData:

    url = f'https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication/refresh'

    body = {
        'publicationIds': publish_ids
    }

    res = await get_data(auth=dev_auth,
                         method='PUT',
                         url=url,
                         body=body,
                         session=session,
                         debug=debug)
    return res
