# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/jupyter.ipynb.

# %% auto 0
__all__ = [
    "JupyterAPI_Error",
    "JupyterAPI_WorkspaceStarted",
    "get_jupyter_workspace_by_id",
    "parse_instance_service_location_and_prefix",
    "get_workspace_auth_token_params",
    "get_jupyter_workspaces",
    "start_jupyter_workspace",
    "get_jupyter_content",
    "generate_update_jupyter_body_factory",
    "generate_update_jupyter_body",
    "update_jupyter_file",
    "get_content",
]

# %% ../../nbs/routes/jupyter.ipynb 2
from enum import Enum

import os
import httpx
from functools import partial

import urllib

import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.get_data as gd

import domolibrary.client.DomoError as de
import domolibrary.utils.chunk_execution as ce


# %% ../../nbs/routes/jupyter.ipynb 5
class JupyterAPI_Error(de.DomoError):
    def __init__(
        self, status, response, domo_instance, parent_class=None, function_name=None
    ):
        super().__init__(
            status=status,
            message=response,
            domo_instance=domo_instance,
            parent_class=parent_class,
            function_name=function_name,
        )


class JupyterAPI_WorkspaceStarted(de.DomoError):
    def __init__(
        self, status, response, domo_instance, parent_class=None, function_name=None
    ):
        super().__init__(
            status=status,
            message=response,
            domo_instance=domo_instance,
            parent_class=parent_class,
            function_name=function_name,
        )


# %% ../../nbs/routes/jupyter.ipynb 6
@gd.route_function
async def get_jupyter_workspace_by_id(
    auth,
    workspace_id,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
):
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}"

    res = await gd.get_data(
        url=url,
        method="GET",
        auth=auth,
        parent_class=parent_class,
        session=session,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
    )

    if not res.is_success:
        raise JupyterAPI_Error(
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res


# %% ../../nbs/routes/jupyter.ipynb 8
def parse_instance_service_location_and_prefix(instance: dict, domo_instance):
    url = instance["url"]

    query = urllib.parse.unquote(urllib.parse.urlparse(url).query)
    query = urllib.parse.urlparse(query.split("&")[1].replace("next=", ""))

    return {
        "service_location": query.netloc.replace(domo_instance, "")[1:],
        "service_prefix": query.path,
    }


async def get_workspace_auth_token_params(workspace_id, auth, return_raw: bool = False):
    """
    params are needed for authenticating requests inside the workspace environment
    Note: you'll also need a internally generated jupyter_token to authenticate requests
    returns { service_location , service_prefix}
    """
    res = await get_jupyter_workspace_by_id(workspace_id=workspace_id, auth=auth)

    open_instances = res.response.get("instances")

    if return_raw:
        return open_instances

    if not open_instances:
        raise JupyterAPI_WorkspaceStarted(
            status=res.status,
            response="There are no open instances. Do you need to start the workspace?",
            domo_instance=auth.domo_instance,
            function_name=res.traceback_details.function_name,
        )

    return parse_instance_service_location_and_prefix(
        open_instances[0], auth.domo_instance
    )


# %% ../../nbs/routes/jupyter.ipynb 10
@gd.route_function
async def get_jupyter_workspaces(
    auth: dmda.DomoAuth,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=1,
    debug_api: bool = False,
    debug_loop: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/search/workspaces"

    body = {
        "limit": 50,
        "offset": 0,
        "sortFieldMap": {"CREATED": "DESC"},
        "filters": [],
    }

    def arr_fn(res):
        return res.response["workspaces"]

    offset_params = {"limit": "limit", "offset": "offset"}

    res = await gd.looper(
        url=url,
        method="POST",
        limit=50,
        body=body,
        auth=auth,
        arr_fn=arr_fn,
        offset_params_in_body=True,
        offset_params=offset_params,
        parent_class=parent_class,
        session=session,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        debug_api=debug_api,
        debug_loop=debug_loop,
    )
    if not res.is_success:
        raise JupyterAPI_Error(
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res


# %% ../../nbs/routes/jupyter.ipynb 13
@gd.route_function
async def start_jupyter_workspace(
    workspace_id,
    auth: dmda.DomoAuth,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=1,
    debug_api: bool = False,
    return_raw: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/datascience/v1/workspaces/{workspace_id}/instances"

    try:
        res = await gd.get_data(
            url=url,
            method="POST",
            auth=auth,
            parent_class=parent_class,
            session=session,
            num_stacks_to_drop=debug_num_stacks_to_drop,
            debug_api=debug_api,
        )

        if return_raw:
            return res

    except RuntimeError as e:
        return rgd.ResponseGetData(
            status=500,
            response=f"starting workspace, please wait - {e}",
            is_success=False,
        )

    if res.status == 500 or res.status == 403:
        raise JupyterAPI_Error(
            status=res.status,
            response=f"you may not have access to this workspace {workspace_id}, is it shared with you? || OR may already be started -- {res.response}",
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    if not res.is_success:
        raise JupyterAPI_Error(
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    res.response = "workspace started"
    return res


# %% ../../nbs/routes/jupyter.ipynb 15
@gd.route_function
async def get_jupyter_content(
    auth: dmda.DomoAuth,
    content_path: str = "",
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
):
    url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/{content_path}"

    res = await gd.get_data(
        url=f"{url}",
        method="GET",
        auth=auth,
        headers={"authorization": f"Token {auth.jupyter_token}"},
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
    if not res.is_success:
        raise JupyterAPI_Error(
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
            function_name=res.traceback_details.function_name,
        )

    return res


# %% ../../nbs/routes/jupyter.ipynb 20
def generate_update_jupyter_body__new_content_path(content_path):
    if not content_path:
        return None

    if "/" in content_path:
        return "/".join(content_path.split("/")[:-1])
    else:
        return ""


def generate_update_jupyter_body__text(body, content_path=None):
    body.update(
        {
            "format": "text",
            "type": "file",
            "path": generate_update_jupyter_body__new_content_path(content_path),
        }
    )
    return body


def generate_update_jupyter_body__ipynb(body, content_path=None):

    body.update(
        {
            "format": None,
            "type": "notebook",
            "path": generate_update_jupyter_body__new_content_path(content_path),
        }
    )
    return body


def generate_update_jupyter_body__directory(content_path, body):
    body.update(
        {
            "path": generate_update_jupyter_body__new_content_path(content_path),
            "format": None,
            "type": "directory",
        }
    )
    return body


# %% ../../nbs/routes/jupyter.ipynb 21
class generate_update_jupyter_body_factory(Enum):
    IPYNB = partial(generate_update_jupyter_body__ipynb)
    DIRECTORY = partial(generate_update_jupyter_body__directory)
    TEXT = partial(generate_update_jupyter_body__text)

    @classmethod
    def from_text(cls, value):
        try:
            return cls[value.upper()].value
        except:
            return cls.TEXT.value


def generate_update_jupyter_body(
    new_content, content_path: str  # my_folder/datatypes.ipynb
):
    """factory to construct properly formed body"""

    content_name = os.path.normpath(content_path).split(os.sep)[-1]

    if "." in content_path:
        content_type = content_path.split(".")[-1]
    else:
        content_type = "directory"

    body = {
        "name": content_name,
        "content": new_content,
        "path": content_path,
    }
    return generate_update_jupyter_body_factory.from_text(content_type)(
        body=body, content_path=content_path
    )


# %% ../../nbs/routes/jupyter.ipynb 25
@gd.route_function
async def update_jupyter_file(
    auth: dmda.DomoJupyterAuth,
    new_content,
    content_path: str = "",  # file name and location in jupyter
    debug_api: bool = False,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
    session: httpx.AsyncClient = None,
):
    dmda.test_is_jupyter_auth(auth)

    body = generate_update_jupyter_body(new_content, content_path)

    content_path_split = os.path.normpath(content_path).split(os.sep)

    url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/{'/'.join(content_path_split)}"

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        body=body,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        session=session,
    )

    if not res.is_success:
        raise JupyterAPI_Error(
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            parent_class=parent_class,
        )

    return res


# %% ../../nbs/routes/jupyter.ipynb 29
async def get_content_recursive(
    auth,
    all_rows,
    content_path,
    logs,
    res: rgd.ResponseGetData,
    obj: dict = None,
    is_recursive: bool = True,
    is_skip_recent_executions: bool = True,
    is_skip_default_files: bool = True,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop=0,
    parent_class=None,
    session: httpx.AsyncClient = None,
):
    # set path (on initial execution there is no object)

    res = await get_jupyter_content(
        auth=auth,
        content_path=content_path,
        debug_api=debug_api,
        parent_class=parent_class,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        session=session,
    )
    if return_raw:
        return res

    obj = res.response
    obj_name = obj["name"]
    obj_type = obj["type"]
    obj_path = obj["path"]
    obj_content = obj["content"] or []

    s = {"content_path": obj_path, "type": obj_type, "name": obj_name}

    if (is_skip_recent_executions and obj_path.startswith("recent_executions")) or (
        is_skip_default_files and obj_path.startswith("domo_jupyter_examples")
    ):
        res.response = all_rows
        res.logs = logs
        return res

    all_rows.append(obj)
    s.update({"is_append": True})
    logs.append(s)

    res.response = all_rows
    res.logs = logs

    if obj["type"] != "directory":
        return res

    s.update({"content": len(obj_content), "all_rows": len(all_rows)})
    logs.append(s)

    res.response = all_rows
    res.logs = logs

    if not is_recursive:
        return res

    if len(obj_content) > 0:
        await ce.gather_with_concurrency(
            *[
                get_content_recursive(
                    auth=auth,
                    content_path=content["path"],
                    all_rows=all_rows,
                    logs=logs,
                    res=res,
                    is_skip_recent_executions=is_skip_recent_executions,
                    is_skip_default_files=is_skip_default_files,
                    debug_api=debug_api,
                    debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
                    parent_class=parent_class,
                    session=session,
                )
                for content in obj_content
            ],
            n=5,
        )

    return res


# %% ../../nbs/routes/jupyter.ipynb 30
@gd.route_function
async def get_content(
    auth: dmda.DomoJupyterAuth,
    content_path="",
    is_recursive: bool = True,
    is_skip_recent_executions: bool = True,
    is_skip_default_files: bool = True,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    parent_class: str = None,
    session: httpx.AsyncClient = None,
):
    dmda.test_is_jupyter_auth(auth)

    all_rows = []
    logs = []
    res = None

    return await get_content_recursive(
        auth=auth,
        content_path=content_path,
        all_rows=all_rows,
        logs=logs,
        res=res,
        is_recursive=is_recursive,
        is_skip_recent_executions=is_skip_recent_executions,
        is_skip_default_files=is_skip_default_files,
        return_raw=return_raw,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
        session=session,
    )
