import aiohttp

from ...DomoClasses import DomoAuth as dmda
from . import get_data as gd


async def get_accounts(full_auth: dmda.DomoFullAuth,
                       debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )


async def get_account_config(full_auth: dmda.DomoFullAuth,
                             account_id: int,
                             data_provider_type: bool = False,
                             debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )


async def update_account_config(full_auth: dmda.DomoFullAuth,
                                account_id: int,
                                config_body: dict,
                                data_provider_type: str,
                                debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=config_body,
        log_results=log_results,
        debug=debug,
        session=session
    )

async def update_account_name(full_auth: dmda.DomoFullAuth,
                              account_id: int,
                              account_name: str,
                              debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/name"
    
    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=account_name,
        log_results=log_results,
        content_type = "text/plain",
        debug=debug,
        session=session
    )





async def get_account_config(full_auth: dmda.DomoFullAuth,
                             account_id: int,
                             data_provider_type: bool = False,
                             debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )


async def get_account_from_id(full_auth: dmda.DomoFullAuth, account_id: int,
                              debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}?unmask=true"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session=session
    )


async def create_account(full_auth:dmda.DomoFullAuth, config_body:dict,
                         debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):
    
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='POST',
        body = config_body,
        log_results=log_results,
        debug=debug,
        session=session
    )

async def delete_account(full_auth:dmda.DomoFullAuth,
                         account_id: str,
                         debug: bool = False, 
                         log_results: bool = False, session: aiohttp.ClientSession = None):
    
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"

    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='DELETE',
        log_results=log_results,
        debug=debug,
        session=session
    )

def generate_share_account_payload_v1( user_id: int ):
    return {"type":"USER","id":user_id,"permissions":['READ']}

def generate_share_account_payload_v2( user_id: int,
                                   access_level: str = 'CAN_VIEW' # CAN_VIEW, CAN_EDIT, CAN_SHARE
                                  ):
    return {"type":"USER","id":user_id,"accessLevel":access_level }



async def share_account_v2(full_auth : dmda.DomoFullAuth,
                        account_id : str,
                        share_payload: dict,
                        debug: bool = False,
                        log_results :bool = False,
                        session : aiohttp.ClientSession = None
                       ):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"
    
    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body = share_payload,
        log_results=log_results,
        debug=debug,
        session=session
    )

async def share_account_v1(full_auth : dmda.DomoFullAuth,
                        account_id : str,
                        share_payload: dict,
                        debug: bool = False,
                        log_results :bool = False,
                        session : aiohttp.ClientSession = None
                       ):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/share"
    
    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body = share_payload,
        log_results=log_results,
        debug=debug,
        session=session
    )



