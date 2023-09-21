# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoJupyter.ipynb.

# %% auto 0
__all__ = ['DomoJupyter_Content', 'DomoJupyter']

# %% ../../nbs/classes/50_DomoJupyter.ipynb 2
import os
import json

from dataclasses import dataclass, field
from typing import Union
import datetime as dt
import domolibrary.utils.DictDot as util_dd
from dateutil.parser import parse

import domolibrary.client.DomoAuth as dmda
import domolibrary.routes.jupyter as jupyter_routes

# import domolibrary.client.DomoError as de
# import domolibrary.utils.chunk_execution as ce

# %% ../../nbs/classes/50_DomoJupyter.ipynb 4
@dataclass
class DomoJupyter_Content:
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

    def export_content(
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
            content_patuh = f"{jupyter_folder}/{jupyter_file_name}"

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

# %% ../../nbs/classes/50_DomoJupyter.ipynb 5
@dataclass
class DomoJupyter:
    auth: dmda.DomoJupyterAuth = field(repr=False)
    content: [DomoJupyter_Content] = field(default=None)

    jupyter_token = None
    service_location = None
    service_prefix = None

    def __post_init__(self):
        dmda.test_is_jupyter_auth(self.auth)

        if hasattr(self.auth, "domo_password") and not isinstance(
            self.auth, dmda.DomoJupyterFullAuth
        ):
            self.auth = DomoJupyterFullAuth.convert_auth(
                full_auth=self.auth,
                jupyter_token=self.jupyter_token,
                service_location=self.service_location,
                service_prefix=self.service_prefix,
            )
        if hasattr(self.auth, "developer_token") and not isinstance(
            self.auth, DomoJupyterDeveloperToken
        ):
            self.auth = dmda.DomoJupyterTokenAuth.convert_auth(
                auth=self.auth,
                jupyter_token=self.jupyter_token,
                service_location=self.service_location,
                service_prefix=self.service_prefix,
            )

    async def get_content(
        self,
        debug_api: bool = False,
        return_raw: bool = False,
        is_recursive: bool = True,
        content_path: str = "",
    ):
        if is_recursive:
            res = await jupyter_routes.get_content_recursive(
                auth=self.auth,
                debug_api=False,
                content_path=content_path,
                debug_num_stacks_to_drop=3,
                parent_class=self.__class__.__name__,
            )
            content_ls = res.response

        else:
            res = await jupyter_routes.get_jupyter_content(
                auth=self.auth,
                debug_api=False,
                content_path=content_path,
                debug_num_stacks_to_drop=2,
                parent_class=self.__class__.__name__,
            )

            content_ls = res.response["content"]

        if return_raw:
            return res

        return [
            DomoJupyter_Content._from_json(obj, auth=self.auth) for obj in content_ls
        ]
