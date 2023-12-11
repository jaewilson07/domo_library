# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoDataflow_Action.ipynb.

# %% ../../nbs/classes/50_DomoDataflow_Action.ipynb 2
from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import List

import datetime as dt
import domolibrary.utils.DictDot as util_dd
import domolibrary.utils.convert as ct

from nbdev.showdoc import  patch_to

# %% auto 0
__all__ = ['DomoDataflow_Action_Type', 'DomoAction', 'DomoDataflow_Action', 'DomoDataflow_ActionResult']

# %% ../../nbs/classes/50_DomoDataflow_Action.ipynb 4
class DomoDataflow_Action_Type(Enum):
    LoadFromVault = "LoadFromVault"
    PublishToVault = "PublishToVault"
    GenerateTableAction = "GenerateTableAction"

@dataclass 
class DomoAction:
    id: str
    type: str = None
    name: str = None

@dataclass
class DomoDataflow_Action(DomoAction):
    datasource_id: str  = None
    sql: str = None

    depends_on : List[str] = None
    parent_actions : List[dict] = None


    @classmethod
    def _from_json(cls, obj: dict):
        dd = obj

        if isinstance(dd, dict):
            dd = util_dd.DictDot(obj)

        tbl_name = dd.dataSource.name if dd.dataSource else None
        ds_id = dd.dataSource.guid if dd.dataSource else None

        return  cls(
            type=dd.type,
            id=dd.id,
            name=dd.name or dd.targetTableName or dd.tableName or tbl_name,
            depends_on = dd.dependsOn,
            
            datasource_id=dd.dataSourceId or ds_id,
            sql=dd.selectStatement or dd.query,
        )



# %% ../../nbs/classes/50_DomoDataflow_Action.ipynb 5
@patch_to(DomoDataflow_Action)
def get_parents(self: DomoDataflow_Action, domo_actions: List[DomoDataflow_Action]):
    if self.depends_on and len(self.depends_on) > 0:
        self.parent_actions = [
            parent_action
            for depends_id in self.depends_on
            for parent_action in domo_actions
            if parent_action.id == depends_id
        ]
    
    if self.parent_actions:
        [parent.get_parents(domo_actions ) for parent in self.parent_actions if parent.depends_on]
            

    return self.parent_actions

# %% ../../nbs/classes/50_DomoDataflow_Action.ipynb 8
@dataclass
class DomoDataflow_ActionResult(DomoAction):
    is_success : bool = None
    rows_processed : int = None
    begin_time : dt.datetime = None
    end_time : dt.datetime = None
    duration_in_sec : int  = None

    def __post_init__(self):
        if self.begin_time and self.end_time:
            self.duration_in_sec =  (self.end_time - self.begin_time).total_seconds()
            
    @classmethod
    def _from_json(cls, obj: dict):
        return  cls(
            id=obj.get('actionId'),
            type = obj.get('type'),
            is_success = obj.get('wasSuccessful'),
            begin_time = ct.convert_epoch_millisecond_to_datetime(obj.get('beginTime', None)),
            end_time = ct.convert_epoch_millisecond_to_datetime(obj.get('endTime', None)),
            rows_processed =  obj.get('rowsProcessed', None),
        )

