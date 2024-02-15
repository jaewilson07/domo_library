# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/auth_accesstoken.ipynb.

# %% auto 0
__all__ = ['get_access_tokens', 'AccessToken_GenerationError', 'generate_access_token', 'AccessToken_RevokeError',
           'revoke_access_token']

# %% ../../nbs/routes/auth_accesstoken.ipynb 2
import datetime as dt
import time

from dataclasses import dataclass, field
import httpx

import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.get_data as gd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# import domolibrary.client.Logger as lg

# %% ../../nbs/routes/auth_accesstoken.ipynb 5
@gd.route_function
async def get_access_tokens(
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class=None,
    session: httpx.AsyncClient = None,
    return_raw: bool = False
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accesstokens"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    [token.update({'expires':  dt.datetime.utcfromtimestamp(token['expires']/1000)}) for token in res.response]

    return res

# %% ../../nbs/routes/auth_accesstoken.ipynb 7
def generate_expiration_unixtimestamp(duration_in_days: int = 90, debug_prn: bool = False):

    today = dt.datetime.today() 
    expiration_date = today + dt.timedelta(days=duration_in_days)

    if debug_prn:
        print(f"expiration_date is {duration_in_days} from today {expiration_date}")

    return int(time.mktime(expiration_date.timetuple())* 1000)


# %% ../../nbs/routes/auth_accesstoken.ipynb 9
class AccessToken_GenerationError(de.DomoError):
    def __init__(self, user_id, domo_instance, parent_class, 
    function_name,
    message = None, 
    ):
        super().__init__(
            domo_instance=domo_instance,
            message=message or f"failure to generate access_token for {user_id}",
            function_name=function_name,
            parent_class=parent_class,
        )


@gd.route_function
async def generate_access_token(
    auth: dmda.DomoAuth,
    token_name: str,
    user_id,
    duration_in_days: 90,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class=None,
    session: httpx.AsyncClient = None,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accesstokens"

    expiration_timestamp = generate_expiration_unixtimestamp(
        duration_in_days=duration_in_days
    )

    body = {"name": token_name, "ownerId": user_id, "expires": expiration_timestamp}

    res = await gd.get_data(
        url=url,
        method="POST",
        body=body,
        auth=auth,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if res.status == 400:
        raise AccessToken_GenerationError(
            user_id=user_id,
            message = f"unable to generate access_token for {user_id} || did you pass a valid user_id",
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    if not res.is_success or not res.response["token"]:
        raise AccessToken_GenerationError(
            user_id=user_id,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res

# %% ../../nbs/routes/auth_accesstoken.ipynb 11
class AccessToken_RevokeError(de.DomoError):
    def __init__(self, access_token_id, domo_instance, parent_class, 
    function_name,
    ):
        super().__init__(
            domo_instance=domo_instance,
            message=f"failure to revoke token {access_token_id}",
            function_name=function_name,
            parent_class=parent_class,
        )

@gd.route_function
async def revoke_access_token(
    auth : dmda.DomoAuth,
    access_token_id : int,
    debug_api : bool = False,
    debug_num_stacks_to_drop=1,
    parent_class=None,
    session : httpx.AsyncClient = None,
):
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/accesstokens/{access_token_id}"

    res = await gd.get_data(
        url = url,
        method = 'DELETE',
        auth = auth,
        debug_api = debug_api,
        parent_class = parent_class,
        num_stacks_to_drop = debug_num_stacks_to_drop
    )

    if not res.is_success:
        raise AccessToken_RevokeError(
            access_token_id = access_token_id,
            domo_instance = auth.domo_instance,
            parent_class = parent_class,
            function_name = res.traceback_details.function_Name,
        )

    return res
