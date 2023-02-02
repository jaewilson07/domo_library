# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/dataflow.ipynb.

# %% auto 0
__all__ = ['get_dataflow_by_id']

# %% ../../nbs/routes/dataflow.ipynb 2
import httpx
import pandas as pd
import io
from pprint import pprint

import utils.DictDot as dd
import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/routes/dataflow.ipynb 3
async def get_dataflow_by_id(dataflow_id: int,
                            auth: dmda.DomoAuth,
                            debug_api: bool = False) -> rgd.ResponseGetData:
    domo_instance = auth.domo_instance

    url = f'https://{domo_instance}.domo.com/api/dataprocessing/v1/dataflows/{dataflow_id}'

    return await gd.get_data(
        auth=auth,
        url=url,
        method='GET',
        debug_api=debug_api,
    )
