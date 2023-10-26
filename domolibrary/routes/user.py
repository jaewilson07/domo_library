# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/user.ipynb.

# %% auto 0
__all__ = ['User_CrudError', 'GetUser_Error', 'ResetPassword_PasswordUsed', 'SearchUser_NoResults', 'DownloadAvatar_Error',
           'get_all_users', 'get_by_id', 'search_users', 'search_users_by_id', 'search_users_by_email',
           'search_virtual_user_by_subscriber_instance', 'create_user', 'set_user_landing_page', 'reset_password',
           'request_password_reset', 'UserProperty_Type', 'UserProperty', 'generate_patch_user_property_body',
           'update_user', 'download_avatar']

# %% ../../nbs/routes/user.ipynb 2
import os
from enum import Enum
import httpx
import asyncio

import domolibrary.utils.DictDot as dd
import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

import domolibrary.utils.chunk_execution as ce


# %% ../../nbs/routes/user.ipynb 4
class User_CrudError(de.DomoError):
    def __init__(
        self,
        domo_instance,
        function_name,
        status,
        message,
        parent_class=None,
        entity_id=None,
    ):
        super().__init__(
            domo_instance=domo_instance,
            function_name=function_name,
            status=status,
            message=message,
            entity_id=entity_id,
            parent_class=parent_class,
        )


class GetUser_Error(de.DomoError):
    def __init__(
        self, domo_instance, status, response, function_name=None, parent_class=None
    ):
        super().__init__(
            message=response,
            status=status,
            function_name=function_name,
            parent_class=parent_class,
            domo_instance=domo_instance,
        )


class ResetPassword_PasswordUsed(de.DomoError):
    def __init__(
        self,
        status,
        domo_instance,
        entity_id=None,
        message="Password used previously",
        function_name=None,
        parent_class=None,
    ):
        super().__init__(
            message=message,
            status=status,
            function_name=function_name,
            entity_id=entity_id,
            domo_instance=domo_instance,
            parent_class=parent_class,
        )


class SearchUser_NoResults(de.DomoError):
    def __init__(
        self, domo_instance, 
        search_criteria=None, 
        function_name=None, parent_class=None,
        status = None
    ):
        search_str = f"- {search_criteria}" if search_criteria else ""

        super().__init__(
            message=f"query {search_str} returned no users",
            function_name=function_name,
            parent_class=parent_class,
            domo_instance=domo_instance,
            status = status
        )


class DownloadAvatar_Error(de.DomoError):
    def __init__(
        self,
        status,
        response,
        user_id,
        domo_instance,
        function_name=None,
        parent_class=None,
    ):
        super().__init__(
            status=status,
            message=f"unable to download {user_id} - {response}",
            domo_instance=domo_instance,
            parent_class=parent_class,
            function_name=function_name,
        )


# %% ../../nbs/routes/user.ipynb 6
async def get_all_users(
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class=None,
) -> rgd.ResponseGetData:
    """retrieves all users from Domo"""
    url = f"https://{ auth.domo_instance}.domo.com/api/content/v2/users"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise GetUser_Error(
            domo_instance=domo_instance,
            status=res.status,
            response=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/user.ipynb 10
async def get_by_id(
    user_id,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=1,
    parent_class=None,
):
    # does not include role_id
    v2_url = f"https://{auth.domo_instance}.domo.com/api/content/v2/users/{user_id}"

    v3_url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users/{user_id}"

    params = {"includeDetails": True}

    res_v2, res_v3 = await asyncio.gather(
        gd.get_data(
            url=v2_url,
            method="GET",
            auth=auth,
            debug_api=debug_api,
            session=session,
            params=params,
            num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class,
        ),
        gd.get_data(
            url=v3_url,
            method="GET",
            auth=auth,
            debug_api=debug_api,
            session=session,
            params=params,
            num_stacks_to_drop=debug_num_stacks_to_drop,
            parent_class=parent_class,
        ),
    )

    if return_raw:
        return res_v2, res_v3

    if res_v2.status == 200 and res_v2.response == '':
        raise SearchUser_NoResults(
            search_criteria=f"user_id {user_id} not found",
            domo_instance=auth.domo_instance,
            status=res_v2.status,
            function_name=f"{res_v2.traceback_details.function_name}-v2_url",
            parent_class=parent_class,
        )

    if not res_v2.is_success:
        raise GetUser_Error(
            domo_instance=auth.domo_instance,
            status=res_v2.status,
            response=res_v2.response,
            function_name=f"{res_v2.traceback_details.function_name}-v2_url",
            parent_class=parent_class,
        )

    if res_v3.status == '404' and res_v3.response == 'Not Found':
        raise SearchUser_NoResults(
            domo_instance=auth.domo_instance,
            status=res_v3.status,
            search_criteria=f"user_id {user_id} not found",
            function_name=f"{res_v3.traceback_details.function_name}-v3_url",
            parent_class=parent_class,
        )
    if (not res_v3.status == '404' and not res_v3.response == 'Not Found') and not res_v3.is_success:
        raise GetUser_Error(
            domo_instance=auth.domo_instance,
            status=res_v3.status,
            response=res_v3.response,
            function_name=f"{res_v3.traceback_details.function_name}-v3_url",
            parent_class=parent_class,
        )

    res_v2.response.update({"roleId": res_v3.response.get("roleId")})

    return res_v2


# %% ../../nbs/routes/user.ipynb 15
def process_v1_search_users(
    v1_user_ls: list[dict],  # list of users from v1_users_search API
) -> list[dict]:  # sanitized list of users.
    """sanitizes the response from v1_users_search API and removes unecessary attributes"""

    clean_users = []

    for obj_user in v1_user_ls:
        dd_user = dd.DictDot(obj_user)

        clean_users.append(
            {
                "id": dd_user.id,
                "displayName": dd_user.displayName,
                "roleId": dd_user.roleId,
                "userName": dd_user.userName,
                "emailAddress": dd_user.emailAddress,
            }
        )

    return clean_users

# %% ../../nbs/routes/user.ipynb 16
async def search_users(
    auth: dmda.DomoAuth,
    body: dict,
    debug_api: bool = False,
    return_raw: bool = False,
    suppress_no_results_error: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class=None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/search"

    res = await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body=body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise GetUser_Error(
            domo_instance=domo_instance,
            status=res.status,
            response=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    if not suppress_no_results_error and len(res.response.get("users")) == 0:
        raise SearchUser_NoResults(
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    res.response = process_v1_search_users(res.response.get("users"))
    return res


# %% ../../nbs/routes/user.ipynb 17
async def search_users_by_id(
    user_ids: list[str],  # list of user ids to search
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    return_raw: bool = False,
    suppress_no_results_error: bool = False,
    debug_num_stacks_to_drop=2,
    parent_class=None,
) -> dict:  # dict to pass to search v1_users_search_api
    """search v1_users_search_api"""

    user_cn = ce.chunk_list(user_ids, 1000)

    res_ls = await ce.gather_with_concurrency(
        n=6,
        *[
            search_users(
                auth=auth,
                body={
                    # "showCount": true,
                    # "count": false,
                    "includeDeleted": False,
                    "includeSupport": False,
                    "filters": [
                        {
                            "field": "id",
                            "filterType": "value",
                            "values": user_ls,
                            "operator": "EQ",
                        }
                    ],
                },
                debug_api=debug_api,
                return_raw=return_raw,
                suppress_no_results_error=suppress_no_results_error,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                parent_class=parent_class,
            )
            for user_ls in user_cn
        ]
    )

    res = res_ls[-1]
 
    res.response = [ row for ls in [ _.response for _ in res_ls] for row in ls ]

    return res



# %% ../../nbs/routes/user.ipynb 18
async def search_users_by_email(
    user_email_ls: list[
        str
    ],  # list of user emails to search.  Note:  search does not appear to be case sensitive
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    return_raw: bool = False,
    suppress_no_results_error: bool = False,
    debug_num_stacks_to_drop=2,
    parent_class=None,
) -> dict:  # dict to pass to search v1_users_search_api
    """search v1_users_search_api"""

    user_cn = ce.chunk_list(user_email_ls, 1000)

    res_ls = await ce.gather_with_concurrency(
        n=6,
        *[
            search_users(
                auth=auth,
                body={
                    # "showCount": true,
                    # "count": false,
                    "includeDeleted": False,
                    "includeSupport": False,
                    "limit": 200,
                    "offset": 0,
                    "sort": {"field": "displayName", "order": "ASC"},
                    "filters": [
                        {
                            "filterType": "text",
                            "field": "emailAddress",
                            "text": " ".join(user_email_ls),
                        }
                    ],
                },
                debug_api=debug_api,
                return_raw=return_raw,
                suppress_no_results_error=suppress_no_results_error,
                debug_num_stacks_to_drop=debug_num_stacks_to_drop,
                parent_class=parent_class,
            )
            for user_ls in user_cn
        ]
    )

    res = res_ls[-1]

    res.response = [ row for ls in [ _.response for _ in res_ls] for row in ls ]
    return res

# %% ../../nbs/routes/user.ipynb 22
async def search_virtual_user_by_subscriber_instance(
    auth: dmda.DomoAuth,  # domo auth object
    subscriber_instance_ls: list[str],  # list of subscriber domo instances
    debug_api: bool = False,  # debug API requests
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:  # list of virtual domo users
    """retrieve virtual users for subscriber instances tied to one publisher"""

    url = f"https://{auth.domo_instance}.domo.com/api/publish/v2/proxy_user/domain/"

    body = {
        "domains": [
            f"{subscriber_instance}.domo.com"
            for subscriber_instance in subscriber_instance_ls
        ]
    }

    return await gd.get_data(
        url=url,
        method="POST",
        auth=auth,
        body=body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )


# %% ../../nbs/routes/user.ipynb 26
async def create_user(
    auth: dmda.DomoAuth,
    display_name: str,
    email_address: str,
    role_id: int,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop: int = 1,
    parent_class: str = None,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/users"

    body = {
        "displayName": display_name,
        "detail": {"email": email_address},
        "roleId": role_id,
    }

    res = await gd.get_data(
        url=url,
        method="POST",
        body=body,
        auth=auth,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )

    if res.status == 400 and res.response == "Bad Request":
        raise User_CrudError(
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            status=res.status,
            message=f"{res.response} - does this user (email) already exist?",
        )

    if not res.is_success:
        raise User_CrudError(
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
            status=res.status,
            message=res.response,
        )

    res.is_success = True
    return res


# %% ../../nbs/routes/user.ipynb 29
async def set_user_landing_page(
    auth: dmda.DomoAuth,
    user_id: str,
    page_id: str,
    debug_api: bool = False,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/landings/target/DESKTOP/entity/PAGE/id/{page_id}/{user_id}"

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        # body = body,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if not res.is_success:
        raise User_CrudError(
            domo_instance=auth.domo_instance,
            entity_id=user_id,
            status=res.status,
            message=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/user.ipynb 30
async def reset_password(
    auth: dmda.DomoAuth,
    user_id: str,
    new_password: str,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/password"

    body = {"domoUserId": user_id, "password": new_password}

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=body,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if (
        res.status == 200
        and res.response.get("description", None)
        == "Password has been used previously."
    ):
        raise ResetPassword_PasswordUsed(
            status=res.status,
            entity_id=user_id,
            domo_instance=auth.domo_instance,
            message=res.response["description"].replace(".", ""),
        )

    return res


# %% ../../nbs/routes/user.ipynb 33
async def request_password_reset(
    domo_instance: str,
    email: str,
    locale="en-us",
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    url = f"https://{domo_instance}.domo.com/api/domoweb/auth/sendReset"

    params = {"email": email, "local": locale}

    return await gd.get_data(
        url=url,
        method="GET",
        params=params,
        auth=None,
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/routes/user.ipynb 35
class UserProperty_Type(Enum):
    display_name = "displayName"
    email_address = "emailAddress"
    phone_number = "phoneNumber"
    title = "title"
    department = "department"
    web_landing_page = "webLandingPage"
    web_mobile_landing_page = "webMobileLandingPage"
    role_id = "roleId"
    employee_id = "employeeId"
    employee_number = "employeeNumber"
    hire_date = "hireDate"
    reports_to = "reportsTo"


class UserProperty:
    property_type: UserProperty_Type
    values: str

    def __init__(self,
                 property_type: UserProperty_Type,
                 values: list):
        self.property_type = property_type
        self.values = self._value_to_list(values)

    @staticmethod
    def _value_to_list(values):
        return values if isinstance(values, list) else [values]

    def to_json(self):
        return {
            "key": self.property_type.value,
            "values": self._value_to_list(self.values),
        }


# %% ../../nbs/routes/user.ipynb 37
def generate_patch_user_property_body(user_property_ls: [UserProperty]):
    return {
        "attributes": [user_property.to_json() for user_property in user_property_ls]
    }


# %% ../../nbs/routes/user.ipynb 40
async def update_user(
    user_id: str,
    user_property_ls: [UserProperty],
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class: str = None,
    debug_num_stacks_to_drop: int = 1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/users/{user_id}"

    body = (
        generate_patch_user_property_body(user_property_ls)
        if isinstance(user_property_ls[0], UserProperty)
        else user_property_ls
    )

    res = await gd.get_data(
        url=url,
        method="PATCH",
        auth=auth,
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise User_CrudError(
            domo_instance=auth.domo_instance,
            entity_id=user_id,
            status=res.status,
            message=res.response,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res

# %% ../../nbs/routes/user.ipynb 43
async def download_avatar(
    user_id,
    auth: dmda.DomoAuth,
    pixels: int = 300,
    folder_path="./images",
    img_name=None,
    is_download_image: bool = True,
    debug_api: bool = False,
    return_raw: bool = False,
    parent_class: str = None,
    debug_num_Stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/avatar/USER/{user_id}?size={pixels}"

    res = await gd.get_data_stream(
        url=url,
        method="GET",
        auth=auth,
        debug_api=debug_api,
        headers={"accept": "image/png;charset=utf-8"},
        num_stacks_to_drop=debug_num_Stacks_to_drop,
        parent_class=parent_class,
    )

    if return_raw:
        return res

    if res.status != 200:
        raise DownloadAvatar_Error(
            status=res.status,
            response=res.response,
            user_id=user_id,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    if is_download_image:
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        if img_name:
            img_name = img_name.replace(".png", "")

        img_name = f"{img_name or user_id}.png"

        file_path = os.path.join(folder_path, img_name)

        with open(file_path, "wb") as out_file:
            out_file.write(res.response)

    res.is_success = True

    return res
