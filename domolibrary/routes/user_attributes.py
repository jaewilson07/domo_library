# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/user_attributes.ipynb.

# %% auto 0
__all__ = [
    "UserAttributes_IssuerType",
    "UserAttributes_GET_Error",
    "UserAttributes_CRUD_Error",
    "get_user_attributes",
    "get_user_attribute_by_id",
    "clean_attribute_id",
    "generate_create_user_attribute_body",
    "create_user_attribute",
    "update_user_attribute",
    "delete_user_attribute",
]

# %% ../../nbs/routes/user_attributes.ipynb 2
from enum import Enum
from typing import List

import datetime as dt

import re

import httpx
import domolibrary.client.get_data as gd
import domolibrary.client.DomoError as de

import domolibrary.client.DomoAuth as dmda


# %% ../../nbs/routes/user_attributes.ipynb 4
class UserAttributes_IssuerType(Enum):
    IDP = "idp"
    SYSTEM = "domo-defined"
    CUSTOM = "customer-defined"


class UserAttributes_GET_Error(de.DomoError):
    def __init__(
        self,
        status,
        message,
        domo_instance,
        parent_class: str = None,
        function_name: str = None,
    ):
        super().__init__(
            status=status,
            message=message,
            parent_class=parent_class,
            domo_instance=domo_instance,
            function_name=function_name,
        )


class UserAttributes_CRUD_Error(de.DomoError):
    def __init__(
        self,
        status,
        message,
        domo_instance,
        parent_class: str = None,
        function_name: str = None,
    ):
        super().__init__(
            status=status,
            message=message,
            parent_class=parent_class,
            domo_instance=domo_instance,
            function_name=function_name,
        )


# %% ../../nbs/routes/user_attributes.ipynb 6
@gd.route_function
async def get_user_attributes(
    auth: dmda.DomoAuth,
    issuer_type_ls: List[
        UserAttributes_IssuerType
    ] = None,  # use `UserAttributes_IssuerType` enum
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    """retrieves user attributes from Domo
    user attributes can be `UserAttributes_IssuerType` -- idp, domo, or user-generated
    API does not filter on the issuer type (despite API accepting filter parameter)
    """
    issuer_type_ls = issuer_type_ls or [member for member in UserAttributes_IssuerType]

    issuer_types = ",".join([member.value for member in issuer_type_ls])

    params = {"issuerTypes": issuer_types}

    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        params=params,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise UserAttributes_GET_Error(
            status=res.status,
            message=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
        )

    res.response = [
        obj
        for obj in res.response
        if obj["keyspace"] in [member.value for member in issuer_type_ls]
    ]

    return res


# %% ../../nbs/routes/user_attributes.ipynb 9
@gd.route_function
async def get_user_attribute_by_id(
    auth: dmda.DomoAuth,
    attribute_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    """retrieves user attributes from Domo
    user attributes can be `UserAttributes_IssuerType` -- idp, domo, or user-generated
    API does not filter on the issuer type (despite API accepting filter parameter)
    """

    res = await get_user_attributes(auth=auth, session=session)

    if not res.is_success:
        raise UserAttributes_GET_Error(
            status=res.status,
            message=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=domo_instance,
        )

    res.response = next(
        (obj for obj in res.response if obj["key"] == attribute_id), None
    )

    if not res.response:
        raise UserAttributes_GET_Error(
            status=res.status,
            message=f"attribute {attribute_id} not found",
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
        )

    return res


# %% ../../nbs/routes/user_attributes.ipynb 12
def clean_attribute_id(text):
    return re.sub(r"[^A-Za-z0-9]", "", text)


# %% ../../nbs/routes/user_attributes.ipynb 13
def generate_create_user_attribute_body(
    attribute_id: str,
    name: str = None,
    description: str = None,
    issuer_type: UserAttributes_IssuerType = None,
    security_voter: str = None,
    data_type: str = None,
):
    s = {"key": attribute_id}

    if issuer_type:
        s.update({"keyspace": issuer_type.value})

    if security_voter:
        s.update({"securityVoter": security_voter})

    if data_type:
        s.update({"validator": data_type})

    if name:
        s.update({"title": name})

    if description:
        s.update({"description": description})

    return s


@gd.route_function
async def create_user_attribute(
    auth: dmda.DomoAuth,
    attribute_id,
    name=None,
    description=None,
    data_type: str = None,
    security_voter=None,
    issuer_type: UserAttributes_IssuerType = None,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    name = name or attribute_id
    attribute_id = clean_attribute_id(attribute_id)
    description = (
        description
        or f"updated via domolibrary {dt.datetime.now().strftime('%Y-%m-%d - %H:%M')}"
    )
    data_type = data_type or "ANY_VALUE"
    security_voter = security_voter or "FULL_VIS_ADMIN_IDP"
    issuer_type = issuer_type or UserAttributes_IssuerType.CUSTOM

    body = generate_create_user_attribute_body(
        attribute_id=attribute_id,
        issuer_type=issuer_type,
        name=name,
        data_type=data_type,
        security_voter=security_voter,
        description=description,
    )

    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys/{attribute_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="POST",
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise UserAttributes_CRUD_Error(
            status=res.status,
            message=f"Bad Request - does attribute {attribute_id} already exist?",
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
        )

    res.response = f"created {attribute_id}"

    return res


# %% ../../nbs/routes/user_attributes.ipynb 15
@gd.route_function
async def update_user_attribute(
    auth: dmda.DomoAuth,
    attribute_id,
    name=None,
    description=None,
    issuer_type: UserAttributes_IssuerType = UserAttributes_IssuerType.CUSTOM,
    data_type: str = None,
    security_voter=None,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    """body must include all attribute parameters,
    this route wil use the `get_user_attribute_by_id` function to retrieve existing values (and throw an error if not found)
    to construct an update statement"""

    body = generate_create_user_attribute_body(
        attribute_id=attribute_id,
        issuer_type=issuer_type,
        name=name,
        description=description,
        data_type=data_type,
        security_voter=security_voter,
    )

    res = await get_user_attribute_by_id(attribute_id=attribute_id, auth=auth)

    body = {**res.response, **body}

    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys/{attribute_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise UserAttributes_CRUD_Error(
            status=res.status,
            message=f"Bad Request - error updating {attribute_id}",
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
        )

    res.response = f"updated {attribute_id}"

    return res


# %% ../../nbs/routes/user_attributes.ipynb 18
@gd.route_function
async def delete_user_attribute(
    auth: dmda.DomoAuth,
    attribute_id,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/user/v1/properties/meta/keys/{attribute_id}"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="DELETE",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise UserAttributes_CRUD_Error(
            status=res.status,
            message=f"Bad Request - failed to delete {attribute_id}",
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            domo_instance=auth.domo_instance,
        )

    res.response = f"deleted {attribute_id}"

    return res
