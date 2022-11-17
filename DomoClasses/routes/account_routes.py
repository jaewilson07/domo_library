import aiohttp
import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.routes.get_data as gd

async def get_accounts(full_auth : dmda.DomoFullAuth, 
                       debug:bool = False, log_results:bool = False, session : aiohttp.ClientSession = None):
     
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts"
    
    if debug:
        print(url)
    
    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session = session
    )

async def get_account_from_id(full_auth:dmda.DomoFullAuth, account_id:int, 
                              debug:bool = False, log_results:bool = False, session : aiohttp.ClientSession = None):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}?unmask=true"
    
    if debug:
        print(url)

    return await gd.get_data(
        auth=full_auth,
        url=url,
        method='GET',
        log_results=log_results,
        debug=debug,
        session = session
    )