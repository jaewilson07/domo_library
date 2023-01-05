import aiohttp
import pandas as pd
import io
from pprint import pprint

from .get_data import get_data, looper
from ..DomoAuth import DomoDeveloperAuth, DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_pdp_policies(full_auth: DomoFullAuth, dataset_id: str, debug: bool = False) -> ResponseGetData:
    url = f'http://{full_auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
    )
    return res


####  PDP ####
def generate_policy_parameter_simple(column_name, column_values_list, operator='EQUALS', ignore_case: bool = True):
    return {
        "type": "COLUMN",
        "name": column_name,
        "values": column_values_list,
        "operator": operator,
        "ignoreCase": ignore_case
    }


def generate_policy_body(policy_name, dataset_id, parameters_list, policy_id=None, user_ids=None,
                         group_ids=None, virtual_user_ids=None):
    if not user_ids:
        user_ids = []

    if not group_ids:
        group_ids = []
    
    if not virtual_user_ids:
        virtual_user_ids = []

    body = {
        "name": policy_name,
        "dataSourceId": dataset_id,
        "userIds": user_ids,
        "virtualUserIds": virtual_user_ids,
        "groupIds": group_ids,
        "dataSourcePermissions": False,
        "parameters": parameters_list
    }

    if policy_id:
        body.update({'filterGroupId': policy_id})

    return body


async def create_policy(full_auth: DomoFullAuth, dataset_id: str, body: dict, debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups'
    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='POST',
        body=body,
        debug=debug)

    return res


async def update_policy(full_auth: DomoFullAuth, dataset_id: str, filter_group_id, body: dict,
                        debug: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/{filter_group_id}'
    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        debug=debug
    )

    return res

