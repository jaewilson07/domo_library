# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoDataflow.ipynb.

# %% auto 0
__all__ = ['DomoDataflow']

# %% ../../nbs/classes/50_DomoDataflow.ipynb 2
from fastcore.basics import patch_to

from enum import Enum
from dataclasses import dataclass, field
import httpx

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.dataflow as dataflow_routes

# %% ../../nbs/classes/50_DomoDataflow.ipynb 3
class DomoDataflow_Action_Type(Enum):
    LoadFromVault = "LoadFromVault"
    PublishToVault = "PublishToVault"
    GenerateTableAction = "GenerateTableAction"


@dataclass
class DomoDataflow_Action:
    type: str
    id: str
    name: str
    data_source_id: str
    sql: str

    @classmethod
    def _from_obj(cls, obj: dict):
        dd = obj
        if isinstance(dd, dict):
            dd = util_dd.DictDot(obj)

        tbl_name = dd.dataSource.name if dd.dataSource else None
        ds_id = dd.dataSource.guid if dd.dataSource else None

        return cls(
            type=dd.type,
            id=dd.id,
            name=dd.name or dd.targetTableName or dd.tableName or tbl_name,
            data_source_id=dd.dataSourceId or ds_id,
            sql=dd.selectStatement or dd.query,
        )

# %% ../../nbs/classes/50_DomoDataflow.ipynb 6
@dataclass
class DomoDataflow:
    id: str
    name: str = None
    auth: dmda.DomoAuth = field(default=None)
    owner: str = None
    description: str = None
    tags: list[str] = None
    actions: list[DomoDataflow_Action] = None

# %% ../../nbs/classes/50_DomoDataflow.ipynb 7
@patch_to(DomoDataflow, cls_method=True)
async def get_from_id(
    cls: DomoDataflow,
    dataflow_id: int,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None
):
    res = await dataflow_routes.get_dataflow_by_id(
        auth=auth, dataflow_id=dataflow_id, debug_api=debug_api,
        session=session
    )

    if return_raw:
        return res

    if not res.is_success:
        return None

    dd = util_dd.DictDot(res.response)
    domo_dataflow = cls(
        auth=auth,
        id=dd.id,
        name=dd.name,
        description=dd.description,
        owner=dd.owner,
        tags=dd.tags,
    )

    if dd.actions:
        domo_dataflow.actions = [
            DomoDataflow_Action._from_obj(action) for action in dd.actions
        ]

    return domo_dataflow


# %% ../../nbs/classes/50_DomoDataflow.ipynb 10
@patch_to(DomoDataflow)
async def execute(
    self: DomoDataflow, auth: dmda.DomoAuth = None, debug_api: bool = False
):
    return await dataflow_routes.execute_dataflow(
        auth=auth or self.auth, dataflow_id=self.id, debug_api=debug_api
    )
