import asyncio
import datetime as dt
import io
import json
from dataclasses import dataclass, field
from enum import Enum, auto

import aiohttp
import pandas as pd

from ..utils.chunk_execution import chunk_list
from ..utils.DictDot import DictDot
from . import DomoCertification as dmdc
from .DomoAuth import DomoDeveloperAuth, DomoFullAuth
from .routes import pdp_routes


@dataclass
class PDP_Policy():
    dataset_id: str
    filter_group_id: str
    name: str
    resources: list
    parameters: list

    @classmethod
    def _from_json(cls, json_obj):
        dd = DictDot(json_obj)

        return cls(dataset_id=dd.dataSourceId,
                   filter_group_id=dd.filterGroupId,
                   name=dd.name,
                   resources=dd.resources,
                   parameters=dd.parameters)

    @staticmethod
    def generate_parameter_simple(column_name, column_values_list, operator='EQUALS', ignore_case: bool = True):
        return pdp_routes.generate_policy_parameter_simple(column_name=column_name,
                                                           column_values_list=column_values_list,
                                                           operator=operator,
                                                           ignore_case=ignore_case)

    @staticmethod
    def generate_body(policy_name, dataset_id, parameters_list, policy_id=None, user_ids=None, group_ids=None, virtual_user_ids=None):
        return pdp_routes.generate_policy_body(policy_name=policy_name,
                                               dataset_id=dataset_id,
                                               parameters_list=parameters_list,
                                               policy_id=policy_id,
                                               user_ids=user_ids,
                                               group_ids=group_ids,
                                               virtual_user_ids=virtual_user_ids)

    @classmethod
    async def update_policy(cls, full_auth: DomoFullAuth,
                            dataset_id: str,
                            policy_definition: dict, # body sent to the API (uses camelCase instead of snake_case)
                            debug: bool = False):
        
        print(policy_definition)
        
        if policy_definition.get('filterGroupId'):
            
            res = await pdp_routes.update_policy(full_auth=full_auth,
                                                 dataset_id=dataset_id,
                                                 filter_group_id=policy_definition.get(
                                                     'filterGroupId'),
                                                 body=policy_definition,
                                                 debug=debug)
            return cls._from_json(res.response)
        else:
            res = await pdp_routes.create_policy(full_auth=full_auth,
                                                 dataset_id=dataset_id,
                                                 body=policy_definition,
                                                 debug=debug)

            return cls._from_json(res.response)
    
class Dataset_PDP_Policies:

    def __init__(self, dataset):
        self.dataset = dataset
        self.policies: list = []

    async def get_policies(self, full_auth: DomoFullAuth = None, dataset_id: str = None, debug: bool = False):

        dataset_id = dataset_id or self.dataset.id
        full_auth = full_auth or self.dataset.full_auth

        res = await pdp_routes.get_pdp_policies(full_auth=full_auth, dataset_id=dataset_id, debug=debug)

        if debug:
            print("debug")
            print(res.status)
            print(res.response)

        if res.status == 200:
            domo_policy = [PDP_Policy._from_json(
                policy_obj) for policy_obj in res.response]
            self.policies = domo_policy
            return domo_policy
