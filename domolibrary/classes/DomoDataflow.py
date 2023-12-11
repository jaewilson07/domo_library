# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoDataflow.ipynb.

# %% ../../nbs/classes/50_DomoDataflow.ipynb 2
from __future__ import annotations

# %% auto 0
__all__ = ['DomoDataflow']

# %% ../../nbs/classes/50_DomoDataflow.ipynb 3
from dataclasses import dataclass, field
from typing import List

import domolibrary.utils.DictDot as util_dd
import domolibrary.utils.chunk_execution as ce

import domolibrary.client.DomoAuth as dmda
import domolibrary.routes.dataflow as dataflow_routes

import httpx
from nbdev.showdoc import patch_to

# %% ../../nbs/classes/50_DomoDataflow.ipynb 4
from .DomoDataflow_Action import DomoDataflow_Action
from domolibrary.classes.DomoDataflow_History import (
    DomoDataflow_History,
    DomoDataflow_ActionResult,
)

# %% ../../nbs/classes/50_DomoDataflow.ipynb 6
@dataclass
class DomoDataflow:
    id: str
    name: str = None
    auth: dmda.DomoAuth = field(default=None, repr=False)
    owner: str = None
    description: str = None
    tags: list[str] = None
    actions: list[DomoDataflow_Action] = None

    version_id: int = None
    version_number: int = None
    versions : List[dict] = None # list of DomoDataflow Versions

    history: DomoDataflow_History = None  # class for managing the history of a dataflow

    def __post_init__(self):
        self.history = DomoDataflow_History(
            dataflow=self, dataflow_id=self.id, auth=self.auth
        )


    @classmethod
    def _from_json(cls, obj, auth, version_id=None, version_number=None):
        dd = util_dd.DictDot(obj)

        domo_dataflow = cls(
            auth=auth,
            id=dd.id,
            name=dd.name,
            description=dd.description,
            owner=dd.owner,
            tags=dd.tags,
            version_id=version_id,
            version_number=version_number,
        )

        if dd.actions:
            domo_dataflow.actions = [
                DomoDataflow_Action._from_json(action) for action in dd.actions
            ]

            [ domo_action.get_parents(domo_dataflow.actions) for domo_action in domo_dataflow.actions]

        return domo_dataflow

# %% ../../nbs/classes/50_DomoDataflow.ipynb 7
@patch_to(DomoDataflow, cls_method=True)
async def get_from_id(
    cls: DomoDataflow,
    dataflow_id: int,
    auth: dmda.DomoAuth = None,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
):
    res = await dataflow_routes.get_dataflow_by_id(
        auth=auth,
        dataflow_id=dataflow_id,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=cls.__name__,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        return None

    return cls._from_json(res.response, auth=auth)

# %% ../../nbs/classes/50_DomoDataflow.ipynb 12
@patch_to(DomoDataflow)
async def execute(
    self: DomoDataflow,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
):
    return await dataflow_routes.execute_dataflow(
        auth=auth or self.auth,
        dataflow_id=self.id,
        parent_class=self.__class__.__name__,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

# %% ../../nbs/classes/50_DomoDataflow.ipynb 16
@patch_to(DomoDataflow, cls_method=True)
async def get_by_version_id(
    cls: DomoDataflow,
    auth: dmda.DomoAuth,
    dataflow_id: int,
    version_id: int,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    res = await dataflow_routes.get_dataflow_by_id_and_version(
        auth=auth,
        dataflow_id=dataflow_id,
        version_id=version_id,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=cls.__name__,
        session = session
    )

    if return_raw:
        return res

    domo_dataflow = cls._from_json(
        res.response["dataFlow"],
        version_id=res.response["id"],
        version_number=res.response["versionNumber"],
        auth=auth,
    )

    return domo_dataflow

# %% ../../nbs/classes/50_DomoDataflow.ipynb 18
@patch_to(DomoDataflow)
async def get_versions(
    self: DomoDataflow,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    res = await dataflow_routes.get_dataflow_versions(
        auth=self.auth, dataflow_id=self.id,
        debug_api = debug_api, session = session,
        debug_num_stacks_to_drop = debug_num_stacks_to_drop,
        parent_class = self.__class__.__name__
    )

    if return_raw:
        return res

    version_ids = [df_obj["id"] for df_obj in res.response]

    self.versions= await ce.gather_with_concurrency(
        *[
            DomoDataflow.get_by_version_id(
                dataflow_id=self.id, version_id=version_id, auth=self.auth,
                session = session,
                debug_api = debug_api,
                debug_num_stacks_to_drop = debug_num_stacks_to_drop

            )
            for version_id in version_ids
        ],
        n=10
    )

    return self.versions
