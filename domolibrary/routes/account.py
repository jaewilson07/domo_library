# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/account.ipynb.

# %% auto 0
__all__ = ['get_accounts', 'GetAccount_NoMatch', 'GetAccount_NoConfigRetrieved', 'DeleteAccount_Error', 'get_account_from_id',
           'get_account_config', 'get_user_access', 'UpdateAccount_Error', 'update_account_config',
           'update_account_name', 'create_account', 'delete_account', 'ShareAccount_Error', 'DomoAccount_AccessLevel',
           'DomoAccount_AccessLevel_V1', 'DomoAccount_AccessLevel_V2', 'generate_share_account_payload_v1',
           'generate_share_account_payload_v2', 'share_account_v2', 'get_account_accesslist_for_v2', 'share_account_v1']

# %% ../../nbs/routes/account.ipynb 3
from typing import Union
from enum import Enum
import httpx
import asyncio
import datetime as dt

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

import domolibrary.classes.DomoAccount_Config as dmac

# %% ../../nbs/routes/account.ipynb 7
@gd.route_function
async def get_accounts(
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:
    """retrieve a list of all the accounts the user has read access to.  Note users with "Manage all accounts" will retrieve all account objects"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
    return res

# %% ../../nbs/routes/account.ipynb 11
class GetAccount_NoMatch(de.DomoError):
    def __init__(
        self,
        domo_instance,
        account_id=None,
        status=None,
        function_name=None,
        parent_class=None,
    ):
        message = f"account_id {account_id} not found"

        super().__init__(
            message=message,
            status=status,
            function_name=function_name,
            parent_class=parent_class,
            domo_instance=domo_instance,
        )


class GetAccount_NoConfigRetrieved(de.DomoError):
    def __init__(
        self,
        account_id,
        domo_instance,
        status=None,
        function_name=None,
        parent_class=None,
    ):
        message = f"account_id {account_id} did not return a config.  update `DomoAccount_Config` if it uses OAuth, otherwise this is probably an error"

        super().__init__(
            message=message,
            status=status,
            function_name=function_name,
            parent_class=parent_class,
            domo_instance=domo_instance,
        )


class DeleteAccount_Error(de.DomoError):
    def __init__(
        self,
        entity_id,
        domo_instance,
        status,
        message,
        function_name=None,
        parent_class=None,
    ):
        super().__init__(
            entity_id=entity_id,
            domo_instance=domo_instance,
            status=status,
            message=message,
            function_name=function_name,
            parent_class=parent_class,
        )

# %% ../../nbs/routes/account.ipynb 12
@gd.route_function
async def get_account_from_id(
    auth: dmda.DomoAuth,
    account_id: int,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:
    """retrieves metadata about an account"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        timeout=20,  # occasionally this API has a long response time
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=None,
    )

    if not res.is_success and (
        res.response == "Forbidden" or res.response == "Not Found"
    ):
        raise GetAccount_NoMatch(
            account_id=account_id,
            domo_instance=auth.domo_instance,
            status=res.status,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res

# %% ../../nbs/routes/account.ipynb 16
@gd.route_function
async def get_account_config(
    auth: dmda.DomoAuth,
    account_id: int,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: Union[httpx.AsyncClient, httpx.AsyncClient, None] = None,
) -> rgd.ResponseGetData:
    res = await get_account_from_id(
        auth=auth,
        account_id=account_id,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    data_provider_type = res.response.get("dataProviderType")
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GetAccount_NoMatch(
            account_id=account_id,
            domo_instance=auth.domo_instance,
            status=res.status,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    res.response.update(
        {
            "_search_metadata": {
                "account_id": account_id,
                "data_provider_type": data_provider_type,
            }
        }
    )

    return res

# %% ../../nbs/routes/account.ipynb 21
@gd.route_function
async def get_user_access(
    auth: dmda.DomoAuth,
    account_id: int,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: Union[httpx.AsyncClient, httpx.AsyncClient, None] = None,
) -> rgd.ResponseGetData:
    res = await get_account_from_id(
        auth=auth,
        account_id=account_id,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    data_provider_type = res.response.get("dataProviderType")
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}?unmask=true"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GetAccount_NoMatch(
            account_id=account_id,
            domo_instance=auth.domo_instance,
            status=res.status,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    res.response.update(
        {
            "_search_metadata": {
                "account_id": account_id,
                "data_provider_type": data_provider_type,
            }
        }
    )

    return res

# %% ../../nbs/routes/account.ipynb 23
class UpdateAccount_Error(de.DomoError):
    def __init__(
        self,
        status,
        response,
        account_id,
        domo_instance,
        info=None,
        function_name: str = None,
        parent_class: str = None,
    ):
        message = f"unable to update account {account_id} - {response} { (' - ' + info) or ''}"

        super().__init__(
            status=status,
            message=message,
            domo_instance=domo_instance,
            parent_class=parent_class,
            function_name=function_name,
        )


@gd.route_function
async def update_account_config(
    auth: dmda.DomoAuth,
    account_id: int,
    config_body: dict,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:
    # get the data_provider_type, which is necessare for updating the config setting
    res = await get_account_from_id(
        auth=auth,
        account_id=account_id,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
    data_provider_type = res.response.get("dataProviderType")
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/providers/{data_provider_type}/account/{account_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=config_body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if res.status == 400 and res.response == "Bad Request":
        raise UpdateAccount_Error(
            status=res.status,
            response=res.response,
            account_id=account_id,
            info="updating config | use debug_api to check the URL - ",
            domo_instance=auth.domo_instance,
        )

    if res.status != 200:
        raise UpdateAccount_Error(
            status=res.status,
            response=res.response,
            account_id=account_id,
            info="updating account config",
            domo_instance=auth.domo_instance,
        )

    return res

# %% ../../nbs/routes/account.ipynb 26
@gd.route_function
async def update_account_name(
    auth: dmda.DomoAuth,
    account_id: int,
    account_name: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:
    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/name"
    )

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=account_name,
        content_type="text/plain",
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if res.status != 200:
        raise UpdateAccount_Error(
            status=res.status,
            response=res.response,
            account_id=account_id,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            info="error updating account_name",
        )

    return res

# %% ../../nbs/routes/account.ipynb 29
@gd.route_function
async def create_account(
    auth: dmda.DomoAuth,
    config_body: dict,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts"

    if debug_api:
        print(url)

    attempt = 1
    res = None

    while attempt <= 3:
        res = await gd.get_data(
            auth=auth,
            url=url,
            method="POST",
            body=config_body,
            debug_api=debug_api,
            session=session,
        )

        if res.is_success:
            return res

        attempt += 1
        await asyncio.sleep(3)

    if not res.is_success:
        raise CreateAccount_Error(
            entity_id=account_name,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res

# %% ../../nbs/routes/account.ipynb 30
@gd.route_function
async def delete_account(
    auth: dmda.DomoAuth,
    account_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise DeleteAccount_Error(
            entity_id=self.id,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res

# %% ../../nbs/routes/account.ipynb 32
class ShareAccount_Error(de.DomoError):
    def __init__(
        self, account_id, status, response, domo_instance, function_name, parent_class
    ):
        super().__init__(
            status=status,
            entity_id=account_id,
            message=response,
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )


class DomoAccount_AccessLevel:
    pass


class DomoAccount_AccessLevel_V1(DomoAccount_AccessLevel, Enum):
    CAN_VIEW = "READ"


class DomoAccount_AccessLevel_V2(DomoAccount_AccessLevel, Enum):
    CAN_VIEW = "CAN_VIEW"
    CAN_EDIT = "CAN_EDIT"
    CAN_SHARE = "CAN_SHARE"


def generate_share_account_payload_v1(
    access_level: DomoAccount_AccessLevel, user_id: int = None, group_id: int = None
):
    if user_id:
        return {"type": "USER", "id": int(user_id), "permissions": [access_level.value]}
    if group_id:
        return {
            "type": "GROUP",
            "id": int(group_id),
            "permissions": [access_level.value],
        }


def generate_share_account_payload_v2(
    access_level: DomoAccount_AccessLevel, user_id: int = None, group_id: int = None
):
    if user_id:
        return {"type": "USER", "id": int(user_id), "accessLevel": access_level.value}

    if group_id:
        return {"type": "GROUP", "id": int(group_id), "accessLevel": access_level.value}

# %% ../../nbs/routes/account.ipynb 34
@gd.route_function
async def share_account_v2(
    auth: dmda.DomoAuth,
    account_id: str,
    share_payload: dict,
    debug_api: bool = False,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
    session: httpx.AsyncClient = None,
):
    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=share_payload,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        session=session,
    )

    if res.status == 500 and res.response == "Internal Server Error":
        raise ShareAccount_Error(
            account_id=account_id,
            status=res.status,
            response=f'ℹ️ - {res.response + "| User may already have access to account."}',
            domo_instance=self.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    if not res.status == 200:
        raise ShareAccount_Error(
            account_id=account_id,
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/account.ipynb 35
@gd.route_function
async def get_account_accesslist_for_v2(
    auth: dmda.DomoAuth,
    account_id: str,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
):
    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v2/accounts/share/{account_id}"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if not res.status == 200:
        GetAccount_NoMatch(
            domo_instance=auth.domo_instance,
            status=res.status,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/account.ipynb 38
# v1 may have been deprecated.  used to be tied to group beta
@gd.route_function
async def share_account_v1(
    auth: dmda.DomoAuth,
    account_id: str,
    share_payload: dict,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
):
    url = (
        f"https://{auth.domo_instance}.domo.com/api/data/v1/accounts/{account_id}/share"
    )

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=share_payload,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        debug_api=debug_api,
        session=session,
    )

    if res.status == 500 and res.response == "Internal Server Error":
        raise ShareAccount_Error(
            account_id=account_id,
            status=res.status,
            response=f'ℹ️ - {res.response + "| User may already have access to account OR may need to execute v2 share API."}',
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    if not res.status == 200:
        raise ShareAccount_Error(
            account_id=account_id,
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res
