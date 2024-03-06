# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/auth.ipynb.

# %% auto 0
__all__ = ['InvalidCredentialsError', 'AccountLockedError', 'InvalidAuthTypeError', 'InvalidInstanceError',
           'NoAccessTokenReturned', 'get_full_auth', 'get_developer_auth', 'who_am_i']

# %% ../../nbs/routes/auth.ipynb 2
import datetime as dt
import time

from dataclasses import dataclass, field
from typing import Optional, Union
from urllib.parse import urlparse

import httpx

import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.Logger as lg
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/auth.ipynb 5
class InvalidCredentialsError(de.DomoError):
    """return invalid credentials sent to API"""

    def __init__(
        self,
        function_name: Optional[str] = None,
        parent_class: str = None,
        status: Optional[int] = None,  # API request status
        message="invalid credentials",
        domo_instance: Optional[str] = None,
    ):
        super().__init__(
            status=status,
            message=message,
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )


class AccountLockedError(de.DomoError):
    """return invalid credentials sent to API"""

    def __init__(
        self,
        function_name: Optional[str] = None,
        status: Optional[int] = None,  # API request status
        message="invalid credentials",
        domo_instance: Optional[str] = None,
        parent_class: str = None,
    ):
        super().__init__(
            status=status,
            message=message,
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )


class InvalidAuthTypeError(de.DomoError):
    """return invalid Auth type sent to API"""

    def __init__(
        self,
        required_auth_type: dict = None,
        required_auth_type_ls: list = None,
        function_name: Optional[str] = None,
        parent_class: str = None,
        domo_instance: Optional[str] = None,
    ):
        message = f"This API rquires {required_auth_type.__name__ if required_auth_type else ', '.join([auth_type.__name__ for auth_type in required_auth_type_ls])}"

        super().__init__(
            message=message,
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )


class InvalidInstanceError(de.DomoError):
    """return if invalid domo_instance sent to API"""

    def __init__(
        self,
        function_name: Optional[str] = None,
        parent_class: str = None,
        status: Optional[int] = None,
        message="invalid instance",
        domo_instance: Optional[str] = None,
    ):
        super().__init__(
            status=status,
            message=message,
            domo_instance=domo_instance,
            parent_class=parent_class,
            function_name=function_name,
        )


class NoAccessTokenReturned(de.DomoError):
    def __init__(
        self,
        function_name: Optional[str] = None,
        status: Optional[int] = None,
        message: str = "No AccessToken returned",
        domo_instance: Optional[str] = None,
        parent_class: str = None,
    ):
        super().__init__(
            status=status,
            message=message,
            domo_instance=domo_instance,
            function_name=function_name,
            parent_class=parent_class,
        )

# %% ../../nbs/routes/auth.ipynb 7
async def get_full_auth(
    domo_instance: str,  # domo_instance.domo.com
    domo_username: str,  # email address
    domo_password: str,
    session: Optional[httpx.AsyncClient] = None,
    debug_api: bool = False,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    """uses username and password authentication to retrieve a full_auth access token"""

    is_close_session = False

    if not session:
        is_close_session = True
        session = httpx.AsyncClient()

    url = f"https://{domo_instance}.domo.com/api/content/v2/authentication"

    tokenHeaders = {"Content-Type": "application/json"}

    body = {
        "method": "password",
        "emailAddress": domo_username,
        "password": domo_password,
    }

    if debug_api:
        print(body, url)

    res = await session.request(method="POST", url=url, headers=tokenHeaders, json=body)

    if is_close_session:
        await session.aclose()

    traceback_details = lg.get_traceback()

    res = rgd.ResponseGetData._from_httpx_response(
        res, traceback_details=traceback_details, parent_class=parent_class
    )

    if (
        res.is_success
        and isinstance(res.response, dict)
        and res.response.get("reason", None)
    ):
        if res.response.get("reason") == "INVALID_CREDENTIALS":
            res.is_success = False
            raise InvalidCredentialsError(
                function_name=res.traceback_details.function_name,
                parent_class=parent_class,
                status=res.status,
                message=res.response["reason"],
                domo_instance=domo_instance,
            )
        if (
            isinstance(res.response, dict)
            and res.response.get("reason") == "ACCOUNT_LOCKED"
        ):
            res.is_success = False
            raise AccountLockedError(
                function_name=res.traceback_details.function_name,
                parent_class=parent_class,
                status=res.status,
                message=str(res.response.get("reason")),
                domo_instance=domo_instance,
            )

        if res.response == {} or res.response == "":  # no access token
            res.is_success = False
            raise NoAccessTokenReturned(
                function_name=res.traceback_details.function_name,
                parent_class=parent_class,
                status=res.status,
                domo_instance=domo_instance,
            )

    if res.status == 403 and res.response == "Forbidden":
        res.is_success = False
        raise InvalidInstanceError(
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            status=res.status,
            message=res.response,
            domo_instance=domo_instance,
        )

    if not res.is_success or not (
        isinstance(res.response, dict) and res.response.get("sessionToken")
    ):
        raise InvalidCredentialsError(
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            status=res.status,
            message=res.response,
            domo_instance=domo_instance,
        )

    return res

# %% ../../nbs/routes/auth.ipynb 15
async def get_developer_auth(
    domo_client_id: str,
    domo_client_secret: str,
    session: Optional[httpx.AsyncClient] = None,
    debug_api: bool = False,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    """
    only use for authenticating against apis documented under developer.domo.com
    """
    is_close_session = False

    if not session:
        is_close_session = True
        session = httpx.AsyncClient(
            auth=httpx.BasicAuth(domo_client_id, domo_client_secret)
        )

    url = "https://api.domo.com/oauth/token?grant_type=client_credentials"

    if debug_api:
        print(url, domo_client_id, domo_client_secret)

    res = await session.request(method="GET", url=url)

    traceback_details = lg.get_traceback()

    if is_close_session:
        await session.aclose()

    res = rgd.ResponseGetData._from_httpx_response(
        res, traceback_details=traceback_details, parent_class=parent_class
    )

    if res.status == 401 and res.response == "Unauthorized":
        res.is_success = False
        raise InvalidCredentialsError(
            function_name=res.traceback_details.function_name,
            status=res.status,
            message=res.response,
        )

    return res

# %% ../../nbs/routes/auth.ipynb 19
async def who_am_i(
    auth_header: dict,
    domo_instance: str,  # <domo_instance>.domo.com
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop=0,
    debug_api: bool = False,
    return_raw: bool = False,
):
    """
    will attempt to validate against the 'me' API.
    This is the same authentication test the Domo Java CLI uses.
    """

    is_close_session = False

    if not session:
        is_close_session = True
        session = httpx.AsyncClient()

    url = f"https://{domo_instance}.domo.com/api/content/v2/users/me"

    if debug_api:
        print(url, auth_header)

    res = await session.request(method="GET", headers=auth_header, url=url)

    if is_close_session:
        await session.aclose()

    if return_raw:
        return res

    traceback_details = lg.get_traceback(num_stacks_to_drop=debug_num_stacks_to_drop)

    res = rgd.ResponseGetData._from_httpx_response(
        res, traceback_details=traceback_details, parent_class=parent_class
    )

    if res.status == 401 and res.response == "Unauthorized":
        res.is_sucess = False

        raise InvalidCredentialsError(
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            status=res.status,
            message=res.response,
            domo_instance=domo_instance,
        )

    return res
