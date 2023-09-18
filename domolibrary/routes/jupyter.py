# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/jupyter.ipynb.

# %% auto 0
__all__ = ['get_jupyter_content', 'generate_update_jupyter_body', 'JupyterApi_Error', 'update_jupyter_file',
           'get_content_recursive']

# %% ../../nbs/routes/jupyter.ipynb 2
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.get_data as gd
import domolibrary.client.DomoError as de
import domolibrary.utils.chunk_execution as ce
import os

# %% ../../nbs/routes/jupyter.ipynb 4
async def get_jupyter_content(
    auth: dmda.DomoAuth,
    content_path: str = "",
    debug_api: bool = False,
    debug_num_stacks_to_drop=1,
    parent_class : str = None
):
    url = f"https://{auth.domo_instance}.{auth.service_location}{auth.service_prefix}api/contents/{content_path}"

    res = await gd.get_data(
        url=f"{url}",
        method="GET",
        auth=auth,
        headers={"authorization": f"Token {auth.jupyter_token}"},
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class = parent_class

    )
    if not res.is_success:
        raise Exception("unable to retrieve content")

    return res

# %% ../../nbs/routes/jupyter.ipynb 8
def generate_update_jupyter_text(body):
    body.update(
        {
            "format": "text",
            "type": "file",
        }
    )
    return body


def generate_update_jupyter_ipynb(body):
    body.update(
        {
            "format": None,
            "type": "notebook",
        }
    )
    return body


def generate_update_jupyter_directory(content_path, body):
    if "/" in content_path:
        new_content_path = "/".join(content_path.split("/")[:-1])
    else:
        new_content_path = ""

    body.update(
        {
            "path": new_content_path,
            "format": None,
            "type": "directory",
        }
    )
    return body

# %% ../../nbs/routes/jupyter.ipynb 9
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

    if content_type == "ipynb":
        return generate_update_jupyter_ipynb(body)

    if content_type == "directory":
        return generate_update_jupyter_directory(content_path, body)

    return generate_update_jupyter_text(body)


generate_update_jupyter_body("hello world", "hi.md")

# %% ../../nbs/routes/jupyter.ipynb 11
class JupyterApi_Error(de.DomoError):
    def __init__(self, status, response, domo_instance, jupyter_token=None):
        super().__init__(
            status=status,
            response=f"Unable to update content - {response}.  Validate your token {jupyter_token}",
        )

# %% ../../nbs/routes/jupyter.ipynb 12
class JupyterApi_Error(de.DomoError):
    def __init__(self, status, response, domo_instance, jupyter_token=None):
        super().__init__(
            status=status,
            message=f"Unable to update content - {response}.  Validate your token {jupyter_token}",
        )


async def update_jupyter_file(
    auth: dmda.DomoJupyterAuth,
    new_content,
    content_path: str = "",  # file name and location in jupyter
    debug_api: bool = False,
    parent_class:str = None,
    debug_num_stacks_to_drop=1,
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
        parent_class = parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise JupyterApi_Error(
            status=res.status,
            response=res.response,
            domo_instance=auth.domo_instance,
            jupyter_token=auth.jupyter_token,
        )

    return res

# %% ../../nbs/routes/jupyter.ipynb 16
async def get_content_recursive_process_obj(
    obj, all_rows, auth, debug_api: bool = False,
    debug_num_stacks_to_drop = 0,
    parent_class = None
):
    content_path = obj["path"]

    if content_path.startswith('recent_executions'):
        return

    if obj["type"] != "directory":
        res = await get_jupyter_content(
            auth=auth,
            content_path=content_path,
            debug_api=debug_api,
            parent_class = parent_class,
            debug_num_stacks_to_drop = debug_num_stacks_to_drop+ 1
        )

        all_rows.append(res.response)

    elif obj["type"] == "directory":
        await get_content_recursive(
            auth=auth,
            content_path=content_path,
            all_rows=all_rows,
            debug_api=debug_api,
            parent_class = parent_class,
            debug_num_stacks_to_drop =debug_num_stacks_to_drop +1
        )

# %% ../../nbs/routes/jupyter.ipynb 17
async def get_content_recursive(
    auth: dmda.DomoJupyterAuth,
    content_path="",
    all_rows=None,  
    debug_api: bool = False,
    return_raw: bool = False,
    is_skip_recent_executions: bool = True,
    debug_num_stacks_to_drop =2,
    parent_class :str = None
):
    dmda.test_is_jupyter_auth(auth)

    all_rows = all_rows or []

    res = await get_jupyter_content(
        auth=auth,
        content_path=content_path,
        debug_api=debug_api,
        parent_class = parent_class,
        debug_num_stacks_to_drop = debug_num_stacks_to_drop
    )

    content_ls = res.response["content"]

    await ce.gather_with_concurrency(
        n=5,
        *[
            get_content_recursive_process_obj(obj, all_rows, 
            auth, debug_api=debug_api, 
            parent_class = parent_class,
            debug_num_stacks_to_drop = debug_num_stacks_to_drop
            ) for index, obj in enumerate(content_ls)
        ]
    )

    if return_raw:
        return res

    res.response = all_rows

    return res