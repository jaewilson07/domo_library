# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/dataset.ipynb.

# %% auto 0
__all__ = ['DatasetNotFoundError', 'QueryRequestError', 'query_dataset_public', 'query_dataset_private', 'get_dataset_by_id',
           'get_schema', 'set_dataset_tags', 'UploadDataError', 'upload_dataset_stage_1', 'upload_dataset_stage_2_file',
           'upload_dataset_stage_2_df', 'upload_dataset_stage_3', 'index_dataset', 'index_status',
           'generate_list_partitions_body', 'list_partitions']

# %% ../../nbs/routes/dataset.ipynb 3
from typing import Optional

import io
import pandas as pd

import aiohttp

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda

# %% ../../nbs/routes/dataset.ipynb 5
class DatasetNotFoundError(Exception):
    def __init__(self, dataset_id, domo_instance):
        message = f"dataset - {dataset_id} not found in {domo_instance}"

        super().__init__(message)

# %% ../../nbs/routes/dataset.ipynb 6
class QueryRequestError(Exception):
    def __init__(self, dataset_id, domo_instance, sql):
        message = f"dataset - {dataset_id} in {domo_instance} received a bad request.  Check your SQL \n {sql}"

        super().__init__(message)

# typically do not use
async def query_dataset_public(
    dev_auth: dmda.DomoDeveloperAuth,
    dataset_id: str,
    sql: str,
    session: aiohttp.ClientSession,
    debug_api: bool = False,
):

    """query for hitting public apis, requires client_id and secret authentication"""

    url = f"https://api.domo.com/v1/datasets/query/execute/{dataset_id}?IncludeHeaders=true"

    body = {"sql": sql}

    return await gd.get_data(
        auth=dev_auth, url=url, method="POST", body=body, session=session, debug_api=debug_api)
        

        
async def query_dataset_private(
    auth: dmda.DomoAuth,  # DomoFullAuth or DomoTokenAuth
    dataset_id: str,
    sql: str,
    session: Optional[aiohttp.ClientSession] = None,
    loop_until_end: bool = False,  # retrieve all available rows
    limit=100,  # maximum rows to return per request.  refers to PAGINATION
    skip=0,
    maximum=100,  # equivalent to the LIMIT or TOP clause in SQL, the number of rows to return total
    debug_api: bool = False,
    debug_loop: bool = False,
):
    """execute SQL queries against private APIs, requires DomoFullAuth or DomoTokenAuth"""

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/execute/{dataset_id}"

    offset_params = {
        "offset": "offset",
        "limit": "limit",
    }

    def body_fn(skip, limit):
        return {"sql": f"{sql} limit {limit} offset {skip}"}

    def arr_fn(res) -> pd.DataFrame:
        rows_ls = res.response.get("rows")
        columns_ls = res.response.get("columns")
        output = []
        for row in rows_ls:
            new_row = {}
            for index, column in enumerate(columns_ls):
                new_row[column] = row[index]
            output.append(new_row)
            # pd.DataFrame(data=res.response.get('rows'), columns=res.response.get('columns'))
        return output

    res = await gd.looper(
        auth=auth,
        method="POST",
        url=url,
        arr_fn=arr_fn,
        offset_params=offset_params,
        limit=limit,
        skip=skip,
        maximum=maximum,
        session=session,
        body_fn=body_fn,
        debug_api=debug_api,
        debug_loop=debug_loop,
        loop_until_end=loop_until_end
    )

    if res.status == 404 and res.response == 'Not Found':
        raise DatasetNotFoundError(dataset_id=dataset_id , domo_instance=auth.domo_instance)
    
    if res.status == 400 and res.response == 'Bad Request':
        raise QueryRequestError(dataset_id=dataset_id , domo_instance=auth.domo_instance, sql = sql)
    
    return res


# %% ../../nbs/routes/dataset.ipynb 9
async def get_dataset_by_id(
    dataset_id: str, # dataset id from URL
    auth: Optional[dmda.DomoAuth] = None, # requires full authentication
    debug_api: bool = False, # for troubleshooting API request
    session: Optional[aiohttp.ClientSession] = None
) -> rgd.ResponseGetData: # returns metadata about a dataset
    """retrieve dataset metadata"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}"

    res= await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api, session = session
    )

    if res.status == 404 and res.response == 'Not Found':
        raise DatasetNotFoundError(dataset_id=dataset_id, domo_instance=auth.domo_instance)

    return res

# %% ../../nbs/routes/dataset.ipynb 12
async def get_schema(
    auth: dmda.DomoAuth, dataset_id: str, debug_api: bool = False
) -> rgd.ResponseGetData:
    """retrieve the schema for a dataset"""

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/schema/indexed?includeHidden=false"

    return await gd.get_data(auth=auth, url=url, method="GET", debug_api=debug_api)


# %% ../../nbs/routes/dataset.ipynb 16
async def set_dataset_tags(auth: dmda.DomoFullAuth,
                           tag_ls: [str], # complete list of tags for dataset
                           dataset_id: str,
                           debug_api: bool = False,
                           session: Optional[aiohttp.ClientSession] = None,
                           return_raw : bool = False
                           ):
    
    """REPLACE tags on this dataset with a new list"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/ui/v3/datasources/{dataset_id}/tags"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method='POST',
        debug_api=debug_api,
        body=tag_ls,
        session=session,
        return_raw = return_raw
    )

    if return_raw:
        return res

    if res.status == 200:
        res.set_response (response = f'Dataset {dataset_id} tags updated to [{ ", ".join(tag_ls) }]')
    
    return res


# %% ../../nbs/routes/dataset.ipynb 19
class UploadDataError(Exception):
    """raise if unable to upload data to Domo"""
    
    def __init__(self, stage_num : int, dataset_id : str, domo_instance : str):
        message = f"error uploading data to {dataset_id} during Stage { stage_num} in {domo_instance}"
        super().__init__(message)

# %% ../../nbs/routes/dataset.ipynb 20
async def upload_dataset_stage_1(auth: dmda.DomoAuth,
                                 dataset_id: str,
                                 #  restate_data_tag: str = None, # deprecated
                                 partition_tag: str = None,  # synonymous with data_tag
                                 session: Optional[aiohttp.ClientSession] = None,
                                 debug_api: bool = False,
                                 ) -> rgd.ResponseGetData:

    """preps dataset for upload by creating an upload_id (upload session key) pass to stage 2 as a parameter"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads"

    # base body assumes no paritioning
    body = {
        "action": None,
        "appendId": None
    }

    params = None

    if partition_tag:
        # params = {'dataTag': restate_data_tag or data_tag} # deprecated
        params = {'dataTag': partition_tag}
        body.update({'appendId': 'latest'})

    res = await gd.get_data(auth=auth,
                         url=url, method='POST',
                         body=body,
                         session=session,
                         debug_api=debug_api,
                         params=params)

    if not res.is_success:
        raise UploadDataError(
            stage_num=1, dataset_id=dataset_id, domo_instance=auth.domo_instance)

    return res


# %% ../../nbs/routes/dataset.ipynb 21
async def upload_dataset_stage_2_file(
    auth: dmda.DomoAuth,
    dataset_id: str,
    upload_id: str,  # must originate from  a stage_1 upload response
    data_file: Optional[io.TextIOWrapper] = None,
    session: Optional[aiohttp.ClientSession] = None,
    # only necessary if streaming multiple files into the same partition (multi-part upload)
    part_id: str = 2,
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/parts/{part_id}"

    body = data_file

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        content_type="text/csv",
        body=body,
        session=session,
        debug_api=debug_api,
    )
    if not res.is_success:
        raise UploadDataError(stage_num = 2 , dataset_id = dataset_id, domo_instance = auth.domo_instance)

    res.upload_id = upload_id
    res.dataset_id = dataset_id
    res.part_id = part_id

    return res

# %% ../../nbs/routes/dataset.ipynb 22
async def upload_dataset_stage_2_df(
    auth: dmda.DomoAuth,
    dataset_id: str,
    upload_id: str,  # must originate from  a stage_1 upload response
    upload_df: pd.DataFrame,
    session: Optional[aiohttp.ClientSession] = None,
    part_id: str = 2,  # only necessary if streaming multiple files into the same partition (multi-part upload)
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/parts/{part_id}"

    body = upload_df.to_csv(header=False, index=False)

    # if debug:
    #     print(body)

    res = await gd.get_data(
        url=url,
        method="PUT",
        auth=auth,
        content_type="text/csv",
        body=body,
        session=session,
        debug_api=debug_api,
    )

    if not res.is_success:
        raise UploadDataError(stage_num = 2 , dataset_id = dataset_id, domo_instance = auth.domo_instance)

    res.upload_id = upload_id
    res.dataset_id = dataset_id
    res.part_id = part_id

    return res

# %% ../../nbs/routes/dataset.ipynb 23
async def upload_dataset_stage_3(
    auth: dmda.DomoAuth,
    dataset_id: str,
    upload_id: str,  # must originate from  a stage_1 upload response
    session: Optional[aiohttp.ClientSession] = None,
    update_method: str = "REPLACE",  # accepts REPLACE or APPEND
    #  restate_data_tag: str = None, # deprecated
    partition_tag: str = None,  # synonymous with data_tag
    is_index: bool = False,  # index after uploading
    debug_api: bool = False,
) -> rgd.ResponseGetData:

    """commit will close the upload session, upload_id.  this request defines how the data will be loaded into Adrenaline, update_method
    has optional flag for indexing dataset.
    """

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/commit"

    body = {"index": is_index, "action": update_method}

    if partition_tag:

        body.update(
            {
                "action": "APPEND",
                #  'dataTag': restate_data_tag or data_tag,
                #  'appendId': 'latest' if (restate_data_tag or data_tag) else None,
                "dataTag": partition_tag,
                "appendId": "latest" if partition_tag else None,
                "index": is_index,
            }
        )

    res = await gd.get_data(
        auth=auth, method="PUT", url=url, body=body, session=session, debug_api=debug_api
    )

    if not res.is_success:
        raise UploadDataError(stage_num = 3 , dataset_id = dataset_id, domo_instance = auth.domo_instance)

    res.upload_id = upload_id
    res.dataset_id = dataset_id

    return res

# %% ../../nbs/routes/dataset.ipynb 24
async def index_dataset(
    auth: dmda.DomoAuth,
    dataset_id: str,
    session: Optional[aiohttp.ClientSession] = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    """manually index a dataset"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/indexes"

    body = {"dataIds": []}

    return await gd.get_data(
        auth=auth, method="POST", body=body, url=url, session=session, debug_api = debug_api
    )

# %% ../../nbs/routes/dataset.ipynb 25
async def index_status(
    auth: dmda.DomoAuth,
    dataset_id: str,
    index_id: str,
    session: Optional[aiohttp.ClientSession] = None,
    debug_api: bool = False,
) -> rgd.ResponseGetData:
    """get the completion status of an index"""

    url = f"https://{auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/indexes/{index_id}/statuses"

    return await gd.get_data(
        auth=auth, 
        method="GET", url=url, 
        session=session, debug_api=debug_api
    )


# %% ../../nbs/routes/dataset.ipynb 27
def generate_list_partitions_body(limit=100, offset=0):
    return {
        "paginationFields": [{
            "fieldName": "datecompleted",
            "sortOrder": "DESC",
            "filterValues": {
                "MIN": None,
                "MAX": None
            }
        }],
        "limit": 1000,
        "offset": 0
    }


async def list_partitions(auth: dmda.DomoAuth,
                          dataset_id: str,
                          body: dict = None,
                          session: aiohttp.ClientSession = None,
                          debug_api: bool = False,
                          debug_loop: bool = False,


                          ):

    body = body or generate_list_partitions_body()

    url = f"https://{auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/partition/list"

    offset_params = {
        'offset': 'offset',
        'limit': 'limit',
    }

    def arr_fn(res) -> list[dict]:
        return res.response

    res = await gd.looper(auth=auth,
                       method='POST',
                       url=url,
                       arr_fn=arr_fn,
                       body=body,
                       offset_params_in_body=True,
                       offset_params=offset_params,
                       loop_until_end=True,
                       session=session,
                       debug_loop=debug_loop,
                       debug_api = debug_api)

    if res.status == 404 and res.response == 'Not Found':
        raise DatasetNotFoundError(
            dataset_id=dataset_id, domo_instance=auth.domo_instance)
    return res

