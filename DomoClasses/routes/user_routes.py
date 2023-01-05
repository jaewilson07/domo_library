from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def create_user(full_auth: DomoFullAuth, display_name, email, role_id, debug: bool = False,
                      log_results: bool = False):
    url = f"https://{full_auth.domo_instance}.domo.com/api/content/v3/users"

    body = {"displayName": display_name, "detail": {
        "email": email}, "roleId": role_id}

    res = await get_data(url=url, method='POST', auth=full_auth, body=body, log_results=log_results, debug=debug)
    return res


async def get_all_users(full_auth: DomoFullAuth, log_results: bool = False, debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v2/users'

    if log_results:
        print(f'Getting users from - {url}')

    res = await get_data(url=url, method='GET', auth=full_auth, log_results=log_results, debug=debug)

    return res


def generate_search_users_body_by_id(ids: list[str]) -> dict:
    return {
        # "showCount": true,
        # "count": false,
        "includeDeleted": False,
        "includeSupport": False,
        "filters": [
            {
                "field": "id",
                "filterType": "value",
                "values": ids,
                "operator": "EQ"

            }
        ]
    }


def generate_search_users_body_by_email(email_address) -> dict:
    """search does not appear to be case sensitive"""

    body = {
        # "showCount": true,
        # "count": false,
        "includeDeleted": False,
        "includeSupport": False,
        "limit": 200,
        "offset": 0,
        "sort": {
            "field": "displayName",
            "order": "ASC"
        },
        "filters": [
            {
                "filterType": "text",
                "field": "emailAddress",
                "text": email_address
            }
        ]

    }
    return body


async def search_virtual_user_by_subscriber_instance(full_auth: DomoFullAuth, subscriber_instance, debug: False,
                                                     log_results: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/publish/v2/proxy_user/domain/'

    body = {"domains": [f"{subscriber_instance}.domo.com"]}

    res = await get_data(url=url, method='POST', auth=full_auth, body=body, log_results=log_results, debug=debug)
    return res


async def search_users(full_auth: DomoFullAuth, body: dict, log_results: bool = False,
                       debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/identity/v1/users/search'

    if log_results:
        print(f'Getting users from - {url}')

    res = await get_data(url=url, method='POST', auth=full_auth, body=body, log_results=log_results, debug=debug)

    return res


async def reset_password(full_auth: DomoFullAuth, user_id: str, new_password: str, log_results: bool = False,
                         debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/identity/v1/password'

    body = {
        "domoUserId": user_id,
        "password": new_password}

    if debug:
        print(url)
        print(body)

    res = await get_data(url=url, method='PUT', auth=full_auth, body=body, log_results=log_results, debug=debug)

    return res


async def request_password_reset(domo_instance: str, email: str, locale='en-us', debug: bool = False):
    url = f'https://{domo_instance}.domo.com/api/domoweb/auth/sendReset'

    params = {'email': email,
              'local': locale}

    return await get_data(url=url,
                          method='GET',
                          auth=None,
                          params=params, debug=debug)


async def set_user_landing_page( full_auth: DomoFullAuth, user_id: str,
                             page_id:str,
                             debug:bool = False ):
    
    url = f'https://{full_auth.domo_instance}.domo.com/api/content/v1/landings/target/DESKTOP/entity/PAGE/id/{page_id}/{user_id}'
        
    return await get_data(url=url,
                          method='PUT',
                          auth=full_auth,
                          # body = body,
                          debug=debug)

                             
                             