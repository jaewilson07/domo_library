# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoDatacenter.ipynb.

# %% auto 0
__all__ = ['DomoDatacenter']

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 2
import asyncio
from dataclasses import dataclass
from typing import Union
from enum import Enum

import httpx

from fastcore.basics import patch_to

import domolibrary.utils.chunk_execution as ce

import domolibrary.client.DomoAuth as dmda
import domolibrary.classes.DomoDataset as dmds
import domolibrary.classes.DomoAccount as dma
import domolibrary.classes.DomoCard as dmc 

import domolibrary.routes.datacenter as datacenter_routes
import domolibrary.routes.card as card_routes


# %% ../../nbs/classes/50_DomoDatacenter.ipynb 4
@dataclass
class DomoDatacenter:
    "class for quering entities in the datacenter"
    auth: dmda.DomoAuth = None

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 5
@patch_to(DomoDatacenter, cls_method=True)
async def search_datacenter(
    cls,
    auth: dmda.DomoAuth,
    maximum: int = None,  # maximum number of results to return
    body: dict = None,  # either pass a body or generate a body in the function using search_text, entity_type, and additional_filters parameters
    search_text=None,
    # can accept one value or a list of values
    entity_type: Union[str, list] = "dataset",
    additional_filters_ls=None,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
) -> list:

    res = await datacenter_routes.search_datacenter(
        auth=auth,
        maximum=maximum,
        body=body,
        session=session,
        search_text=search_text,
        entity_type=entity_type,
        additional_filters_ls=additional_filters_ls,
        debug_api=debug_api,
    )

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 9
@patch_to(DomoDatacenter, cls_method=True)
async def search_datasets(
    cls,
    auth=dmda.DomoAuth,
    maximum: int = None,  # maximum number of results to return
    search_text=None,
    # can accept one value or a list of values
    additional_filters_ls=None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
) -> list[dmds.DomoDataset]:

    json_list = await cls.search_datacenter(
        auth=auth,
        maximum=maximum,
        search_text=search_text,
        entity_type=datacenter_routes.Datacenter_Enum.DATASET.value,
        additional_filters_ls=additional_filters_ls,
        return_raw=return_raw,
        session=session,
        debug_api=debug_api,
    )

    if return_raw or len(json_list) == 0:
        return json_list

    return await ce.gather_with_concurrency( n = 60,
        *[
            dmds.DomoDataset.get_from_id(
                dataset_id=json_obj.get("databaseId"),
                auth=auth,
                debug_api=debug_api,
                session=session,
            )
            for json_obj in json_list
        ]
    )

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 12
@patch_to(DomoDatacenter, cls_method=True)
async def get_accounts(
    cls,
    auth=dmda.DomoAuth,
    maximum: int = None,  # maximum number of results to return
    # can accept one value or a list of values
    additional_filters_ls=None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
) -> list[dma.DomoAccount]:
    """search Domo Datacenter account api.
Note: at the time of this writing 7/18/2023, the datacenter api does not support searching accounts by name"""
    
    json_list = await cls.search_datacenter(
        auth=auth,
        maximum=maximum,
        entity_type=datacenter_routes.Datacenter_Enum.ACCOUNT.value,
        additional_filters_ls=additional_filters_ls,
        return_raw=return_raw,
        session=session,
        debug_api=debug_api,
    )

    if return_raw or len(json_list) == 0:
        return json_list

    domo_account_ls = [
            dma.DomoAccount._from_json(
                json_obj,
                auth=auth ) for json_obj in json_list
        ]
    
    return domo_account_ls

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 16
class LineageTypes_Enum(Enum):
    DomoDataset = 'DATA_SOURCE'
    DomoDataflow = 'DATAFLOW'


@patch_to(DomoDatacenter, cls_method=True)
async def get_lineage_upstream(
    cls,
    auth: dmda.DomoAuth,
    domo_entity, # DomoDataset or DomoDataflow
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_prn: bool = False):

    import domolibrary.classes.DomoDataset as dmds
    import domolibrary.classes.DomoDataflow as dmdf

    if not session:
        session = httpx.AsyncClient()
        is_close_session = True


    res = await datacenter_routes.get_lineage_upstream(
        auth=auth,
        entity_type= LineageTypes_Enum[domo_entity.__class__.__name__].value,
        entity_id=domo_entity.id,
        session=session,
        debug_api=debug_api,
    )

    if return_raw or res.status != 200:
        await session.aclose()
        return res

    obj = res.response

    domo_obj = []
    for key, item in obj.items():
        if item.get("type") == "DATA_SOURCE":
            domo_obj.append(
                await dmds.DomoDataset.get_from_id(auth=auth, dataset_id=item.get("id"), session= session)
            )

        if item.get("type") == "DATAFLOW":
            # print(item.get('id'))
            domo_obj.append(
                await dmdf.DomoDataflow.get_from_id(
                    auth=auth, dataflow_id=item.get("id"), session = session
                    
                )
            )
            pass

    await session.aclose()
    return domo_obj
    

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 18
@patch_to(DomoDatacenter, cls_method=True)
async def search_cards(
    cls,
    auth=dmda.DomoAuth,
    maximum: int = None,  # maximum number of results to return
    search_text=None,
    # can accept one value or a list of values
    additional_filters_ls=None,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
) -> list[dmds.DomoDataset]:

    json_list = await cls.search_datacenter(
        auth=auth,
        maximum=maximum,
        search_text=search_text,
        entity_type=datacenter_routes.Datacenter_Enum.CARD.value,
        additional_filters_ls=additional_filters_ls,
        return_raw=return_raw,
        session=session,
        debug_api=debug_api,
    )

    if return_raw or len(json_list) == 0:
        return json_list

    return await ce.gather_with_concurrency( n = 60,
        *[
            dmc.DomoCard.get_by_id(
                card_id=json_obj.get("databaseId"),
                auth=auth,
                debug_api=debug_api,
                session=session,
            )
            for json_obj in json_list
        ]
    )

# %% ../../nbs/classes/50_DomoDatacenter.ipynb 20
@patch_to(DomoDatacenter, cls_method=True)
async def get_cards_admin_summary(
    cls,
    auth=dmda.DomoAuth,
    page_ids: [str] = None,
    card_search_text: str = None,
    page_search_text: str = None,

    maximum: int = None,  # maximum number of results to return
    # can accept one value or a list of values
    return_raw: bool = False,
    debug_api: bool = False,
    debug_loop: bool = False,
    session: httpx.AsyncClient = None,
) -> list[dmc.DomoCard]:
    """search Domo Datacenter card api."""

    search_body = card_routes.generate_body_search_cards_admin_summary(page_ids = page_ids,
                                             card_search_text = card_search_text,
                                             page_search_text = page_search_text)

    res = await card_routes.search_cards_admin_summary(
        auth=auth,
        body = search_body,
        maximum=maximum,
        debug_api=debug_api,
        debug_loop=debug_loop,
        session=session,
        wait_sleep = 5
    )

    if return_raw or len(res.response) == 0:
        return res

    domo_account_ls = await ce.gather_with_concurrency(n=60,*[
            dmc.DomoCard._from_json(
                json_obj,
                auth=auth ) for json_obj in res.response
        ])

    return domo_account_ls

