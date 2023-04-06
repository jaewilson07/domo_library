# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/pdp.ipynb.

# %% auto 0
__all__ = ['PDP_NotRetrieved', 'get_pdp_policies', 'SearchPDP_Error', 'search_pdp_policies_by_name',
           'generate_policy_parameter_simple', 'generate_policy_body', 'CreatePolicy_Error', 'create_policy',
           'update_policy', 'toggle_pdp']

# %% ../../nbs/routes/pdp.ipynb 2
import httpx
import pandas as pd
import io

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

# %% ../../nbs/routes/pdp.ipynb 3
class PDP_NotRetrieved(de.DomoError):
    def __init__(
        self,
        domo_instance,
        function_name,
        status,
        message,
        pdp_id=None,
    ):

        super().__init__(
            domo_instance=domo_instance,
            entity_id=pdp_id,
            function_name=function_name,
            status=status,
            message=message,
        )

# %% ../../nbs/routes/pdp.ipynb 4
async def get_pdp_policies(
    auth: dmda.DomoAuth,
    dataset_id: str,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    url = f"http://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth, 
        url=url, 
        method="GET", 
        debug_api=debug_api, 
        # headers= {'accept': 'application/json'},
        # params = {'options':'load_associations,load_filters,include_open_policy'},
        is_follow_redirects=True
    )

    if len(res.response) == 0 or not res.is_success:
        raise PDP_NotRetrieved(
            domo_instance=auth.domo_instance,
            function_name="get_pdp_policies",
            status=res.status,
            message="failed to retrieve pdp policies",
        )

    return res

# %% ../../nbs/routes/pdp.ipynb 7
class SearchPDP_Error(de.DomoError):
    def __init__(self, status, message, domo_instance, function_name = "search_pdp_by_name"):
        super().__init__(function_name = function_name, status = status, message = message , domo_instance = domo_instance)
        
def search_pdp_policies_by_name(
        # used to return pdp policy info, search by name
        search_name: str,
        result_list: list[dict], # this is the res.response from get_pdp_policies -- should be list of dict
        is_exact_match: bool = True
        ):
    
    if is_exact_match:
        policy_search = next((policy for policy in result_list if policy.get('name') == search_name), None)
        #print(policy_search)   
         
        if not policy_search:
            raise SearchPDP_Error(
                status='',
                message=f'There is no policy named "{search_name}"',
                domo_instance=''
            )  
          
        return policy_search
    else:
        policy_search = [policy for policy in result_list if search_name.lower() in policy.get('name').lower()]
        if not policy_search:
            raise SearchPDP_Error(
                status='',
                message=f'There is no policy name containing "{search_name}"',
                domo_instance=''
            )  
        
        return policy_search

# %% ../../nbs/routes/pdp.ipynb 11
def generate_policy_parameter_simple(
    column_name: str,
    column_values_ls: list[str] = None,
    operator="EQUALS",
    ignore_case: bool = True,
):
    if not isinstance(column_values_ls, list):
        column_values_ls = [column_values_ls]

    return {
        "type": "COLUMN",
        "name": column_name,
        "values": column_values_ls,
        "operator": operator,
        "ignoreCase": ignore_case,
    }

# %% ../../nbs/routes/pdp.ipynb 12
def generate_policy_body(
    policy_name: str,
    dataset_id: str,
    parameters_ls: dict,  # generated by generate_policy_parameter_simple method
    policy_id: str = None,  # only included if updating existing policy
    user_ids: list[str] = None,
    group_ids: list[str] = None,
    virtual_user_ids: list[str] = None,
):
    if not user_ids:
        user_ids = []

    if not group_ids:
        group_ids = []

    if not virtual_user_ids:
        virtual_user_ids = []

    if not isinstance(parameters_ls, list):
        parameters_ls = [parameters_ls]


    body = {
        "name": policy_name,
        "dataSourceId": dataset_id,
        "userIds": user_ids,
        "virtualUserIds": virtual_user_ids,
        "groupIds": group_ids,
        "dataSourcePermissions": False,
        "parameters": parameters_ls,
    }

    if policy_id:
        body.update({"filterGroupId": policy_id})

    return body

# %% ../../nbs/routes/pdp.ipynb 14
class CreatePolicy_Error(de.DomoError):
    def __init__(self, status, message, domo_instance, function_name = "create_policy"):
        super().__init__(function_name = function_name, status = status, message = message , domo_instance = domo_instance)

async def create_policy(
    auth: dmda.DomoAuth,
    dataset_id: str,
    body: dict,  # generated using generate_policy_parameter_simple & generate_policy_body
    session: httpx.AsyncClient = None,
    override_same_name: bool = False,
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups"

    if debug_api:
        print(url)
    
    if override_same_name:
        print(f'Creating policy...')
        res = await gd.get_data(
            auth=auth,
            url=url,
            method="POST",
            body=body,
            debug_api=debug_api,
            session=session,
        )
    else:
        existing_policies = await get_pdp_policies(auth=auth, dataset_id=dataset_id) 
        
        if existing_policies.is_success:
            try:
                policy_exists = search_pdp_policies_by_name(search_name=body.get('name'), result_list=existing_policies.response, is_exact_match=True)
            except:
                policy_exists = False
            
            if policy_exists:
                raise CreatePolicy_Error(
                    status='',
                    message= f'Policy name already exists--avoid creating pdp policies with the same name..To override, rerun and set "override_same_name=True"',
                    domo_instance=auth.domo_instance,
                )
            else:
                print(f'Creating policy...')
                res = await gd.get_data(
                auth=auth,
                url=url,
                method="POST",
                body=body,
                debug_api=debug_api,
                session=session,
            )

    return res

# %% ../../nbs/routes/pdp.ipynb 18
async def update_policy(
    auth: dmda.DomoAuth,
    dataset_id: str,
    policy_id: str,
    body: dict,  # generated using generate_policy_parameter_simple & generate_policy_body
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}/filter-groups/{policy_id}"

    if debug_api:
        print(url)

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
    )

    return res

# %% ../../nbs/routes/pdp.ipynb 21
async def toggle_pdp(
        auth: dmda.DomoAuth,
        dataset_id: str,
        is_enable: bool = True,
        debug_api: bool = False,
        session: httpx.AsyncClient = None
    )-> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/data-control/{dataset_id}"

    if debug_api:
        print(url)

    body = {"enabled": is_enable,
            "external": False  # not sure what this parameter does
            }

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
    )

    return res

