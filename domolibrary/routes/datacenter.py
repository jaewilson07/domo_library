# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/datacenter.ipynb.

# %% auto 0
__all__ = ['Datacenter_Enum', 'Dataflow_Type_Filter_Enum', 'Datacenter_Filter_Field_Enum', 'generate_search_datacenter_filter',
           'generate_search_datacenter_filter_search_term', 'generate_search_datacenter_body',
           'generate_search_datacenter_account_body', 'SearchDatacenter_NoResultsFound', 'search_datacenter',
           'get_lineage_upstream', 'ShareResource_Enum', 'share_resource']

# %% ../../nbs/routes/datacenter.ipynb 2
from enum import Enum
from typing import Union
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoError as de
import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/routes/datacenter.ipynb 3
class Datacenter_Enum(Enum):
    ACCOUNT = "ACCOUNT"
    CARD = "CARD"
    DATAFLOW = "DATAFLOW"
    DATASET = "DATASET"
    GROUP = "GROUP"
    PAGE = "PAGE"
    USER = "USER"


class Dataflow_Type_Filter_Enum(Enum):
    ADR = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "ADR",
        "name": "ADR",
        "not": False,
    }

    MYSQL = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "MYSQL",
        "name": "MYSQL",
        "not": False,
    }

    REDSHIFT = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "MYSQL",
        "name": "MYSQL",
        "not": False,
    }

    MAGICV2 = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "MAGIC",
        "name": "Magic ETL v2",
        "not": False,
    }

    MAGIC = {
        "filterType": "term",
        "field": "data_flow_type",
        "value": "ETL",
        "name": "Magic ETL",
        "not": False,
    }

# %% ../../nbs/routes/datacenter.ipynb 4
class Datacenter_Filter_Field_Enum(Enum):
    DATAPROVIDER = "dataprovidername_facet"


def generate_search_datacenter_filter(
    field,  # use Datacenter_Filter_Field_Enum
    value,
    is_not: bool = False,  # to handle exclusion
):
    return {
        "filterType": "term",
        "field": field,
        "value": value,
        "not": is_not,
    }

# %% ../../nbs/routes/datacenter.ipynb 6
def generate_search_datacenter_filter_search_term(search_term):
    # if not "*" in search_term:
    #     search_term = f"*{search_term}*"

    return {"field": "name_sort", "filterType": "wildcard", "query": search_term}

# %% ../../nbs/routes/datacenter.ipynb 9
def generate_search_datacenter_body(
    search_text: str = None,
    entity_type: Union[
        str, list
    ] = "DATASET",  # can accept one entity_type or a list of entity_types
    additional_filters_ls: list[dict] = None,
    combineResults: bool = True,
    limit: int = 100,
    offset: int = 0,
):
    filters_ls = (
        [generate_search_datacenter_filter_search_term(search_text)]
        if search_text
        else []
    )

    if not isinstance(entity_type, list):
        entity_type = [entity_type]

    if additional_filters_ls:
        if not isinstance(additional_filters_ls, list):
            additional_filters_ls = [additional_filters_ls]

        filters_ls += additional_filters_ls

    return {
        "entities": entity_type,
        "filters": filters_ls or [],
        "combineResults": combineResults,
        "query": "*",
        "count": limit,
        "offset": offset,
    }

# %% ../../nbs/routes/datacenter.ipynb 12
def generate_search_datacenter_account_body(
    search_str: str, is_exact_match: bool = True
):
    return {
        # "count": 100,
        # "offset": 0,
        "combineResults": False,
        "query": search_str if is_exact_match else f"*{search_str}*",
        "filters": [],
        "facetValuesToInclude": [
            "DATAPROVIDERNAME",
            "OWNED_BY_ID",
            "VALID",
            "USED",
            "LAST_MODIFIED_DATE",
        ],
        "queryProfile": "GLOBAL",
        "entityList": [["account"]],
        "sort": {"fieldSorts": [{"field": "display_name_sort", "sortOrder": "ASC"}]},
    }

# %% ../../nbs/routes/datacenter.ipynb 13
class SearchDatacenter_NoResultsFound(de.DomoError):
    def __init__(self, body, domo_instance):
        super().__init__(message=body, domo_instance=domo_instance)


async def search_datacenter(
    auth: dmda.DomoAuth,
    maximum: int = None,
    body: dict = None,  # either pass a body or generate a body in the function using search_text, entity_type, and additional_filters parameters
    search_text=None,
    entity_type: Union[
        str, list
    ] = "dataset",  # can accept one value or a list of values
    additional_filters_ls=None,
    arr_fn: callable = None,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_loop: bool = False

) -> rgd.ResponseGetData:
    
    limit = 100  # api enforced limit

    if not body:
        body = generate_search_datacenter_body(
            entity_type=entity_type,
            additional_filters_ls=additional_filters_ls,
            search_text=search_text,
            combineResults=False,
            limit=limit,
        )

    if not arr_fn:

        def arr_fn(res):
            return res.response.get("searchObjects")

    url = f"https://{auth.domo_instance}.domo.com/api/search/v1/query"

    res = await gd.looper(
        auth=auth,
        session=session,
        url=url,
        loop_until_end=True if not maximum else False,
        body=body,
        offset_params_in_body=True,
        offset_params={"offset": "offset", "limit": "count"},
        arr_fn=arr_fn,
        method="POST",
        maximum=maximum,
        limit=limit,
        debug_api=debug_api,
        debug_loop = debug_loop
    )

    if res.is_success and len(res.response) == 0:
        raise SearchDatacenter_NoResultsFound(
            body=body, domo_instance=auth.domo_instance
        )

    return res

# %% ../../nbs/routes/datacenter.ipynb 16
async def get_lineage_upstream(
    auth: dmda.DomoAuth,
    entity_type: str,
    entity_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
):
    url = f"https://{auth.domo_instance}.domo.com/api/data/v1/lineage/{entity_type}/{entity_id}"

    params = {"traverseDown": "false"}

    return await gd.get_data(
        auth=auth,
        method="GET",
        url=url,
        params=params,
        session=session,
        debug_api=debug_api,
    )


# %% ../../nbs/routes/datacenter.ipynb 19
class ShareResource_Enum(Enum):
    PAGE = "page"
    CARD = "badge"


async def share_resource(
    auth: dmda.DomoAuth,
    resource_ids: list,
    resource_type: ShareResource_Enum,
    group_ids: list = None,
    user_ids: list = None,
    message: str = None,  # email to user
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    """shares page or card with users or groups

    body format:  {
        "resources": [
            {
                "type": "page",
                "id": {oage_id}
            }
        ],
        "recipients": [
            {
                "type": "group",
                "id": "{group_id}"
            }
        ],
        "message": "I thought you might find this page interesting."
    }"""

    resource_ids = resource_ids if isinstance(resource_ids, list) else [resource_ids]
    if group_ids: group_ids = group_ids and group_ids if isinstance(group_ids, list) else [group_ids]
    
    if user_ids: user_ids = user_ids if isinstance(user_ids, list) else [user_ids]

    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/share?sendEmail=false"

    recipient_ls = []

    if group_ids:
        [recipient_ls.append({"type": "group", "id": str(id)}) for id in group_ids]

    if user_ids:
        [recipient_ls.append({"type": "user", "id": str(id)}) for id in user_ids]

    resource_ls = [{"type": resource_type.value, "id": str(id)} for id in resource_ids]

    body = {
        "resources": resource_ls,
        "recipients": recipient_ls,
        "message": message,
    }

    res = await gd.get_data(
        url, method="POST", auth=auth, body=body, session=session, debug_api=debug_api
    )

    if res.is_success:
        res.response = f"{resource_type.value} {','.join([resource['id'] for resource in  resource_ls])} successfully shared with {', '.join([recipient['id'] for recipient in recipient_ls])}"
    
    return res
