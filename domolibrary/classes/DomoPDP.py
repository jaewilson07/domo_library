# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoPDP.ipynb.

# %% auto 0
__all__ = ['PDP_Parameter', 'PDP_Policy', 'Dataset_PDP_Policies', 'SearchPDP_NotFound']

# %% ../../nbs/classes/50_DomoPDP.ipynb 2
import asyncio
import datetime as dt
import io
import json

import httpx
import pandas as pd

from fastcore.basics import patch_to

from dataclasses import dataclass, field
from enum import Enum, auto

import domolibrary.utils.DictDot as util_dd
import domolibrary.utils.chunk_execution as ce

import domolibrary.routes.pdp as pdp_routes

import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

#from ..utils.chunk_execution import chunk_list
#from . import DomoCertification as dmdc



# %% ../../nbs/classes/50_DomoPDP.ipynb 4
@dataclass
class PDP_Parameter:
    column_name: str
    column_values_ls: list
    operator: str = 'EQUALS' or 'GREATER_THAN' or 'LESS_THAN' or 'GREATER_THAN_EQUAL' or 'LESS_THAN_EQUAL' or 'BETWEEN'
    ignore_case: bool = True
    type: str = 'COLUMN' or 'DYNAMIC' #column sets parameter on data vs dynamic creates on Domo Trusted Attribute


# %% ../../nbs/classes/50_DomoPDP.ipynb 5
@patch_to(PDP_Parameter)
def generate_parameter_simple(obj):

        return pdp_routes.generate_policy_parameter_simple(column_name=obj.name,
                                                           type=obj.type,
                                                           column_values_ls=obj.values,
                                                           operator=obj.operator,
                                                           ignore_case=obj.ignoreCase
                                                           )

@patch_to(PDP_Parameter)
def generate_body_from_parameter(self):

        return pdp_routes.generate_policy_parameter_simple(column_name=self.column_name,
                                                           type=self.type,
                                                           column_values_ls=self.column_values_ls,
                                                           operator=self.operator,
                                                           ignore_case=self.ignore_case
                                                           )

# %% ../../nbs/classes/50_DomoPDP.ipynb 8
@dataclass
class PDP_Policy:
    dataset_id: str
    filter_group_id: str
    name: str
    # resources: list
    parameters_ls: list[dict]
    user_ls: list[str]
    group_ls: list[str]
    virtual_user_ls: list[str]

    @classmethod
    async def _from_json(cls, obj, auth: dmda.DomoAuth):
        dd = util_dd.DictDot(obj)

        import domolibrary.classes.DomoUser as dmu
        import domolibrary.classes.DomoGroup as dmg

        return cls(dataset_id=dd.dataSourceId,
                   filter_group_id=dd.filterGroupId,
                   name=dd.name,
                   # resources=dd.resources,
                   parameters_ls=dd.parameters,
                   user_ls=await ce.gather_with_concurrency(n = 60, * [dmu.DomoUser.get_by_id(user_id=id, auth=auth) for id in dd.userIds]) if dd.userIds else None,
                   group_ls=await ce.gather_with_concurrency(n = 60, *[dmg.DomoGroup.get_by_id(group_id=id, auth=auth) for id in dd.groupIds]) if dd.groupIds else None,
                   
                                                                                                                      
                   virtual_user_ls=dd.virtualUserIds)

    @ classmethod
    async def upsert_policy(cls,
                            auth: dmda.DomoAuth,
                            dataset_id: str,
                            # body sent to the API (uses camelCase instead of snake_case)
                            policy_definition: dict,
                            debug_api: bool=False,
                            debug_prn: bool=False
                            ):

        # print(policy_definition)
        policy_id=policy_definition.get('filterGroupId')
        if policy_id:
            if debug_prn:
                print(f'Updating policy {policy_id} in {auth.domo_instance}')
            res=await pdp_routes.update_policy(auth=auth,
                                                 dataset_id=dataset_id,
                                                 policy_id=policy_id,
                                                 body=policy_definition,
                                                 debug_api=debug_api)
            return res
        else:
            if debug_prn:
                print(
                    f'Policy does not exist. Creating policy in {auth.domo_instance}')
            res=await pdp_routes.create_policy(auth=auth,
                                                 dataset_id=dataset_id,
                                                 body=policy_definition,
                                                 debug_api=debug_api)
            return res


# %% ../../nbs/classes/50_DomoPDP.ipynb 10
@patch_to(PDP_Policy)
def generate_body_from_policy(
        self: PDP_Policy
        #params: list[dict] = ''
        ):
        if not self.parameters_ls:
                raise Exception('generate_body_from_policy: no parameters')
                
        self.parameters_ls = [PDP_Parameter.generate_parameter_simple(param) for param in self.parameters_ls]

        
        return pdp_routes.generate_policy_body(policy_name=self.name,
                                               dataset_id=self.dataset_id,
                                               parameters_ls=self.parameters_ls,
                                               policy_id=self.filter_group_id,
                                               user_ids=self.user_ls,
                                               group_ids=self.group_ls,
                                               virtual_user_ids=self.virtual_user_ls)

# %% ../../nbs/classes/50_DomoPDP.ipynb 12
class Dataset_PDP_Policies:

    dataset = None  # domo dataset class
    policies: list[PDP_Policy] = None 
    auth = None 

    def __init__(self, dataset):
        self.dataset = dataset
        self.policies = []

# %% ../../nbs/classes/50_DomoPDP.ipynb 14
@patch_to(Dataset_PDP_Policies)
async def get_policies(
        self: Dataset_PDP_Policies,
        include_all_rows : bool = True, 
        auth: dmda.DomoAuth = None, 
        dataset_id: str = None, 
        return_raw: bool = False,
        debug_api: bool = False
    ):
        
        dataset_id = dataset_id or self.dataset.id
        auth = auth or self.dataset.auth

        res = await pdp_routes.get_pdp_policies(auth=auth, dataset_id=dataset_id, debug_api=debug_api, include_all_rows=include_all_rows)

        if return_raw:
              return res

        if res.status == 200:
            domo_policy = await ce.gather_with_concurrency(n =60, *[PDP_Policy._from_json(
                policy_obj, auth = auth) for policy_obj in res.response])
            self.policies = domo_policy
            return domo_policy

# %% ../../nbs/classes/50_DomoPDP.ipynb 23
class SearchPDP_NotFound(de.DomoError):
    def __init__(self, 
                 domo_instance,
                 dataset_id,
                 message='not found',
                 function_name='search_pdp'):

        super().__init__(domo_instance=domo_instance, entity_id=dataset_id, message=message, function_name=function_name)
         
@patch_to(Dataset_PDP_Policies, cls_method=True)
async def search_pdp_policies(
    cls: Dataset_PDP_Policies,
    auth: dmda.DomoAuth,
    search: str,
    dataset_id: str = None,
    search_method: str = 'id' or 'name',
    is_exact_match: bool = True,
    return_raw: bool = False, 
    debug_api: bool = False,
    session: httpx.AsyncClient = None
):
    
    all_pdp_policies = await Dataset_PDP_Policies(cls).get_policies(
        auth = auth,
        dataset_id = dataset_id,
        debug_api=debug_api
    )
    
    if return_raw:
        return all_pdp_policies

    if search_method == 'name':
        if is_exact_match:
            policy_search = next((policy for policy in all_pdp_policies if policy.name == search), None)
            #print(policy_search)   
            
            if not policy_search:
                raise SearchPDP_NotFound(
                    dataset_id=dataset_id,
                    message=f'There is no policy named "{search}" on dataset_id {dataset_id}',
                    domo_instance=auth.domo_instance
                )  
            
            return policy_search
        else:
            policy_search = [policy for policy in all_pdp_policies if search.lower() in policy.name.lower()]
            if not policy_search:
                raise SearchPDP_NotFound(
                    dataset_id=dataset_id,
                    message=f'There is no policy name containing "{search}" on dataset_id {dataset_id}',
                    domo_instance=auth.domo_instance
                )  
            
            return policy_search
    else:
        policy_search = next((policy for policy in all_pdp_policies if policy.filter_group_id == search), None)
         
    if not policy_search:
        raise SearchPDP_NotFound(
            dataset_id=dataset_id,
            message=f'There is no policy id "{search}" on dataset_id {dataset_id}',
            domo_instance=auth.domo_instance
        )  
          
    return policy_search    
    

# %% ../../nbs/classes/50_DomoPDP.ipynb 27
@patch_to(PDP_Policy)
async def delete_policy(
    self: PDP_Policy, 
    auth: dmda.DomoAuth, 
    policy_id: str = None,
    dataset_id: str = None, 
    debug_api: bool = False
):

    dataset_id = dataset_id or self.dataset_id
    policy_id = policy_id or self.filter_group_id

    res = await pdp_routes.delete_policy(auth=auth, dataset_id=dataset_id, policy_id=policy_id, debug_api=debug_api)
    
    return res

# %% ../../nbs/classes/50_DomoPDP.ipynb 31
@patch_to(Dataset_PDP_Policies)
async def toggle_dataset_pdp(
    self: Dataset_PDP_Policies,
    auth: dmda.DomoAuth = None,
    dataset_id: str = None,
    is_enable: bool = True, # True will enable pdp, False will disable pdp
    debug_api: bool = False,
    session: httpx.AsyncClient = None
):
    auth = auth or self.dataset.auth


    return await pdp_routes.toggle_pdp(
        auth=auth,
        dataset_id=dataset_id or self.dataset.id,
        is_enable=is_enable,
        debug_api=debug_api,
        session=session
    )


