# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoJupyter.ipynb.

# %% auto 0
__all__ = ['DomoJupyterWorkspace_Content', 'DomoJupyterWorkspace']

# %% ../../nbs/classes/50_DomoJupyter.ipynb 2
from ..routes.jupyter import JupyterAPI_Error

# %% ../../nbs/classes/50_DomoJupyter.ipynb 3
import os
import json

from dataclasses import dataclass, field
from typing import List
import datetime as dt

import httpx

import domolibrary.utils.DictDot as util_dd
from dateutil.parser import parse

import domolibrary.client.DomoAuth as dmda
import domolibrary.routes.jupyter as jupyter_routes


# import domolibrary.client.DomoError as de
# import domolibrary.utils.chunk_execution as ce

from nbdev.showdoc import patch_to

# %% ../../nbs/classes/50_DomoJupyter.ipynb 5
@dataclass
class DomoJupyterWorkspace_Content:
    name: str
    folder: str
    last_modified: dt.datetime
    file_type: str
    content: str

    auth: dmda.DomoJupyterAuth = field(repr=False)

    default_export_folder: str = "export"

    def __post_init__(self):
        dmda.test_is_jupyter_auth(self.auth)

        if self.folder.endswith(self.name):
            self.folder = self.folder.replace(self.name, "")

    @classmethod
    def _from_json(cls, obj: dict, auth: dmda.DomoJupyterAuth):
        dd = util_dd.DictDot(obj) if not isinstance(obj, util_dd.DictDot) else obj

        dc = cls(
            name=dd.name,
            folder=dd.path,
            last_modified=parse(dd.last_modified),
            file_type=dd.type,
            auth=auth,
            content=obj.get("content"),
        )

        return dc

    def export(
        self,
        output_folder: str = None,
        file_name: str = None,
    ):
        output_folder = output_folder or os.path.join(
            self.default_export_folder, self.folder
        )

        file_name = file_name or self.name

        if not os.path.exists(output_folder):
            print(output_folder)
            os.makedirs(output_folder)

        content_str = self.content
        if isinstance(self.content, dict):

            content_str = json.dumps(self.content)

        output_path = os.path.join(output_folder, file_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content_str)
            f.close()

        return output_path

    async def update(
        self,
        jupyter_folder: str = None,
        jupyter_file_name: str = None,
        debug_api: bool = False,
    ):
        if jupyter_folder and jupyter_file_name:
            content_path = f"{jupyter_folder}/{jupyter_file_name}"

        if len(self.folder) > 0:
            content_path = f"{self.folder}/{self.name}"

        else:
            content_path = self.name

            if content_path.lower().startswith(self.default_export_folder.lower()):
                content_path = content_path.replace(self.default_export_folder, "")

        content_path = "/".join(os.path.normpath(content_path).split(os.sep))

        return await jupyter_routes.update_jupyter_file(
            auth=self.auth,
            content_path=content_path,
            new_content=self.content,
            debug_api=debug_api,
            debug_num_stacks_to_drop=2,
            parent_class=self.__class__.__name__,
        )

# %% ../../nbs/classes/50_DomoJupyter.ipynb 7
@dataclass
class DomoJupyterWorkspace:
    auth: dmda.DomoJupyterAuth = field(repr=False)
    id: str
    name: str
    description: str

    created_dt: dt.datetime
    updated_dt: dt.datetime
    last_run_dt: dt.datetime

    # owner
    # cpu
    # memory

    instances: List[dict] = None
    input_configuration: list[dict] = None
    output_configuration: list[dict] = None
    account_configuration: list[dict] = None
    collection_configuration: list[dict] = None
    fileshare_configuration: list[dict] = None

    content: List[DomoJupyterWorkspace_Content] = field(default=None)

    jupyter_token: str = None
    service_location: str = None
    service_prefix: str = None

    def __post_init__(self):
        self._update_auth_params()

    def _update_auth_params(self):
        if self.instances:
            res = jupyter_routes.parse_instance_service_location_and_prefix(
                self.instances[0], self.auth.domo_instance
            )
            self.service_location = res["service_location"]
            self.service_prefix = res["service_prefix"]

        if self.service_location and self.service_prefix and self.jupyter_token:
            self.update_auth()

    def update_auth(
        self, service_location=None, service_prefix=None, jupyter_token=None
    ):

        self.service_location = service_location or self.service_location
        self.service_prefix = service_prefix or self.service_prefix
        self.jupyter_token = jupyter_token or self.jupyter_token

        if isinstance(self.auth, dmda.DomoFullAuth):
            self.auth = dmda.DomoJupyterFullAuth.convert_auth(
                auth=self.auth,
                service_location=self.service_location,
                jupyter_token=self.jupyter_token,
                service_prefix=self.service_prefix,
            )

        if isinstance(self.auth, dmda.DomoTokenAuth):
            self.auth = dmda.DomoJupyterTokenAuth.convert_auth(
                auth=self.auth,
                service_location=self.service_location,
                jupyter_token=self.jupyter_token,
                service_prefix=self.service_prefix,
            )

        self.auth.service_location = self.service_location
        self.auth.service_prefix = self.service_prefix
        self.auth.jupyter_token = self.jupyter_token

    @classmethod
    def _from_json(
        cls,
        obj,
        auth,
        jupyter_token: str = None,
    ):
        domo_workspace = cls(
            auth=auth,
            id=obj["id"],
            name=obj["name"],
            description=obj["description"],
            created_dt=obj["created"],
            updated_dt=obj["updated"],
            last_run_dt=obj["lastRun"],
            instances=obj["instances"],
            output_configuration=obj["outputConfiguration"],
            account_configuration=obj["accountConfiguration"],
            fileshare_configuration=obj["collectionConfiguration"],
            jupyter_token=jupyter_token,
        )
        return domo_workspace

# %% ../../nbs/classes/50_DomoJupyter.ipynb 8
@patch_to(DomoJupyterWorkspace, cls_method=True)
async def get_by_id(
    cls,
    workspace_id,
    auth: dmda.DomoAuth,  # this API does not require the jupyter_token, but activities inside the workspace will require additional authentication
    jupyter_token=None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):

    res = await jupyter_routes.get_jupyter_workspace_by_id(
        workspace_id=workspace_id,
        auth=auth,
        session=session,
        debug_api=debug_api,
        parent_class=cls.__name__,
    )

    if return_raw:
        return res

    return cls._from_json(auth=auth, obj=res.response, jupyter_token=jupyter_token)

# %% ../../nbs/classes/50_DomoJupyter.ipynb 10
@patch_to(DomoJupyterWorkspace)
async def get_content(
    self,
    debug_api: bool = False,
    return_raw: bool = False,
    is_recursive: bool = True,
    content_path: str = "",
):
    res = await jupyter_routes.get_content(
        auth=self.auth,
        debug_api=debug_api,
        content_path=content_path,
        debug_num_stacks_to_drop=2,
        parent_class=self.__class__.__name__,
        is_recursive=is_recursive,
        return_raw=return_raw,
    )

    if return_raw:
        return res

    return [
        DomoJupyterWorkspace_Content._from_json(obj, auth=self.auth)
        for obj in res.response
    ]
