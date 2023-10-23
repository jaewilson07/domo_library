# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/account.ipynb.

# %% auto 0
__all__ = ['AccountConfig_InvalidDataProvider', 'Route_Get_Accounts_Error', 'Route_Update_Account_Name_Error',
           'Route_Delete_Account_Error', 'get_accounts', 'GetAccount_NoMatch', 'get_account_from_id',
           'get_account_config', 'UpdateAccount_Error', 'update_account_config', 'update_account_name',
           'create_account', 'delete_account', 'ShareAccount', 'ShareAccount_V1_AccessLevel',
           'ShareAccount_V2_AccessLevel', 'generate_share_account_payload_v1', 'generate_share_account_payload_v2',
           'share_account_v2', 'share_account_v1', 'get_share_account_v2']

# %% ../../nbs/routes/account.ipynb 3
from typing import Union
from enum import Enum
import httpx
import asyncio

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/account.ipynb 5
class AccountConfig_InvalidDataProvider(de.DomoError):
    def __init__(self, account_id, domo_instance, status= None, parent_class :str = None, function_name :str = None):
        message = f"account {account_id} with data_provider_type '{data_provider_type}' does not return a config"

        super().__init__(message = message, status = status, function_name = function_name , domo_instance = domo_instance, parent_class = parent_class)

class Route_Get_Accounts_Error(de.DomoError):
    def __init__(self, 
        parent_class :str=None,
        function_name :str=None):
        super().__init__(
            parent_class=parent_class,
            function_name=function_name)
        
class Route_Update_Account_Name_Error(de.DomoError):
    def __init__(self,
        parent_class :str=None,
        function_name :str=None):
        super().__init__(
            parent_class=parent_class,
            function_name=function_name)
        
class Route_Delete_Account_Error(de.DomoError):
    def __init__(self,
        parent_class :str=None,
        function_name :str=None):
        super().__init__(
            parent_class=parent_class,
            function_name=function_name)

# %% ../../nbs/routes/account.ipynb 7
async def get_accounts(auth: dmda.DomoAuth,
                       debug_api: bool = False, 
                       parent_class :str = None,
                       debug_num_stacks_to_drop = 1,
                       session: Union[httpx.AsyncClient, httpx.AsyncClient, None] = None) -> rgd.ResponseGetData:
    """retrieve a list of all the accounts the user has read access to.  Note users with "Manage all accounts" will retrieve all account objects"""
    
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        session=session
    )
    if res.status != 200:
        res.is_sucess = False

        raise Route_Get_Accounts_Error(
            status=res.status,
            domo_instance=auth.domo_instance,
            message=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class
        )

    res.is_success = True
    return res

# %% ../../nbs/routes/account.ipynb 10
class GetAccount_NoMatch(de.DomoError):
    def __init__(self, account_id, domo_instance, status= None, function_name = 'get_account_from_id'):

        message = f"account_id {account_id} not found"
        
        super().__init__(message = message, status = status, function_name = function_name , domo_instance = domo_instance)
    
async def get_account_from_id(auth: dmda.DomoAuth, account_id: int,
                              debug_api: bool = False, parent_class :str = None, debug_num_stacks_to_drop = 1, session: httpx.AsyncClient = None) -> rgd.ResponseGetData:
    """retrieves metadata about an account"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        session=session, 
        timeout = 20 # occasionally this API has a long response time
    )

    if not res.is_success and (res.response == 'Forbidden' or res.response == 'Not Found'):
        raise GetAccount_NoMatch(
            account_id=account_id, domo_instance=auth.domo_instance, status=res.status)
    
    return res




# %% ../../nbs/routes/account.ipynb 14
async def get_account_config(auth: dmda.DomoAuth,
                             account_id: int,
                             data_provider_type: str ,
                             debug_api: bool = False, 
                             parent_class :str = None,
                             debug_num_stacks_to_drop = 1,
                             session: Union[httpx.AsyncClient, httpx.AsyncClient, None] = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        session=session
    )

    if res.response == {} and res.is_success:
        raise AccountConfig_InvalidDataProvider(account_id= account_id, data_provider_type= data_provider_type, domo_instance=auth.domo_instance, status = res.status)
    
    return res

# %% ../../nbs/routes/account.ipynb 18
class UpdateAccount_Error(de.DomoError):
    def __init__(self, status, response, account_id,
                 domo_instance,
                 info=None,
                 ):

        message = f"unable to update account {account_id} - {response} { (' - ' + info) or ''}"

        super().__init__(status=status, message=message, domo_instance=domo_instance)


async def update_account_config(auth: dmda.DomoAuth,
                                account_id: int,
                                config_body: dict,
                                data_provider_type: str,
                                debug_api: bool = False,
                                parent_class :str = None,
                                debug_num_stacks_to_drop = 1,
                                session: httpx.AsyncClient = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        body=config_body,
        debug_api=debug_api,
        session=session
    )

    if res.status == 400 and res.response == 'Bad Request':
        raise UpdateAccount_Error(status=res.status, response=res.response,
                                  account_id=account_id,
                                  info='updating config | use debug_api to check the URL - ', domo_instance=auth.domo_instance)

        res.is_success = False

    if res.status != 200:
        raise UpdateAccount_Error(status=res.status, response=res.response,
                                  account_id=account_id,
                                  info='updating account config', domo_instance=auth.domo_instance)

        res.is_success = False

    return res


# %% ../../nbs/routes/account.ipynb 21
async def update_account_name(auth: dmda.DomoAuth,
                              account_id: int,
                              account_name: str,
                              debug_api: bool = False, 
                              parent_class :str = None,
                              debug_num_stacks_to_drop = 1,
                              session: httpx.AsyncClient = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/name"
    
    if debug_api:
        print(url)

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        body=account_name,
        content_type = "text/plain",
        debug_api=debug_api,
        session=session
    )
    if res.status != 200:
        res.is_sucess = False

        raise Route_Update_Account_Name_Error(
            status=res.status,
            domo_instance=auth.domo_instance,
            message=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class
        )

    res.is_success = True
    return res

# %% ../../nbs/routes/account.ipynb 22
async def create_account(auth:dmda.DomoAuth, config_body:dict,
                         debug_api: bool = False, parent_class :str = None,
debug_num_stacks_to_drop = 1, session: httpx.AsyncClient = None) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug_api:
        print(url)

    attempt = 1
    res = None

    while attempt <= 3:
        res = await gd.get_data(
            auth=auth,
            url=url,
            method='POST',
            num_stacks_to_drop=debug_num_stacks_to_drop,
            body = config_body,
            debug_api=debug_api,
            session=session
        )

        if res.is_success:
            return res
        
        attempt += 1
        await asyncio.sleep(3)
    
    return res

# %% ../../nbs/routes/account.ipynb 23
async def delete_account(auth:dmda.DomoAuth,
                         account_id: str,
                         debug_api: bool = False, 
                         parent_class :str = None,
                         debug_num_stacks_to_drop = 1,
                         session: httpx.AsyncClient = None) -> rgd.ResponseGetData:
    
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"

    if debug_api:
        print(url)

    return await gd.get_data(
        auth=auth,
        url=url,
        method='DELETE',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        session=session
    )

    if res.status != 200:
        res.is_sucess = False
        
        raise Route_Delete_Account_Error(
            status=res.status,
            domo_instance=auth.domo_instance,
            message=f"Failed to delete account...res: '{res.response}'",
            function_name=res.traceback_details.function_name,
            parent_class=parent_class
        )

    res.is_success = True
    return res

# %% ../../nbs/routes/account.ipynb 25
class ShareAccount():
    pass


class ShareAccount_V1_AccessLevel(ShareAccount, Enum):
    CAN_VIEW = 'READ'


class ShareAccount_V2_AccessLevel(ShareAccount, Enum):
    CAN_VIEW = 'CAN_VIEW'
    CAN_EDIT = 'CAN_EDIT'
    CAN_SHARE = 'CAN_SHARE'


def generate_share_account_payload_v1(
    access_level: ShareAccount,
    user_id: int = None,
    group_id: int = None
):
    if user_id:
        return {"type": "USER", "id": int(user_id), "permissions": [access_level.value]}
    if group_id:
        return {"type": "GROUP", "id": int(group_id), "permissions": [access_level.value]}


def generate_share_account_payload_v2(
    access_level: ShareAccount,
    user_id: int = None,
    group_id: int = None
):

    if user_id:
        return {"type": "USER", "id": int(user_id), "accessLevel": access_level.value}

    if group_id:
        return {"type": "GROUP", "id": int(group_id), "accessLevel": access_level.value}


# %% ../../nbs/routes/account.ipynb 27
async def share_account_v2(auth: dmda.DomoAuth,
                           account_id: str,
                           share_payload: dict,
                           debug_api: bool = False,
                           parent_class :str = None,
                           debug_num_stacks_to_drop = 1,
                           session: httpx.AsyncClient = None
                           ):

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        body=share_payload,
        debug_api=debug_api,
        session=session
    )

    if res.status != 200:
        res.is_sucess = False
        return res.response 

#v1 may have been deprecated.  used to be tied to group beta
async def share_account_v1(auth: dmda.DomoAuth,
                           account_id: str,
                           share_payload: dict,
                           debug_api: bool = False,
                           parent_class :str = None,
                           debug_num_stacks_to_drop = 1,
                           session: httpx.AsyncClient = None
                           ):

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/share"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='PUT',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        body=share_payload,
        debug_api=debug_api,
        session=session
    )

    if res.status != 200: # cause why not. 
        res.is_sucess = False
        return res.response 

# %% ../../nbs/routes/account.ipynb 28
async def get_share_account_v2(auth: dmda.DomoAuth,
                           account_id: str,
                           debug_api: bool = False,
                           parent_class :str = None,
                           debug_num_stacks_to_drop = 1,
                           session: httpx.AsyncClient = None
                           ):

    url = f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"

    return await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        session=session
    )

    if res.status != 200:
        res.is_sucess = False
        return res.response 
