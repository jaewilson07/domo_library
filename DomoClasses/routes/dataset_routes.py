import aiohttp
import pandas as pd
import io
from pprint import pprint

from .get_data import get_data, looper
from ..DomoAuth import DomoDeveloperAuth, DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def get_dataset_by_id(id: str,
                            full_auth: DomoFullAuth = None,
                            dev_auth: DomoDeveloperAuth = None,
                            debug: bool = False, log_result: bool = False) -> ResponseGetData:
    domo_instance = full_auth.domo_instance if full_auth else dev_auth.domo_instance

    url = f'https://{domo_instance}.domo.com/api/data/v3/datasources/{id}'

    res = await get_data(
        auth=full_auth or dev_auth,
        url=url,
        method='GET',
        debug=debug,
    )

    if log_result:
        print(res)

    return res


async def query_dataset_public(dev_auth: DomoDeveloperAuth,
                               id: str,
                               sql: str,
                               session: aiohttp.ClientSession,
                               debug: bool = False):
    url = f'https://api.domo.com/v1/datasets/query/execute/{id}?IncludeHeaders=true'

    body = {'sql': sql}

    res = await get_data(auth=dev_auth, url=url, method='POST', body=body, session=session, debug=debug)

    return res


async def query_dataset_private(full_auth: DomoFullAuth,
                                id: str,
                                sql: str,
                                session: aiohttp.ClientSession,
                                loop_until_end: bool = True,
                                limit=100,

                                debug: bool = False):
    is_close_session = False
    if not session:
        session = aiohttp.ClientSession()
        is_close_session = True

    url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/execute/{id}'
    if debug:
        print(url)

    offset_params = {
        'offset': 'offset',
        'limit': 'limit',
    }

    def body_fn(skip, limit):
        return {
            'sql': f"{sql} offset {skip} limit {limit}"
        }

    def arr_fn(res) -> pd.DataFrame:
        rows_ls = res.response.get('rows')
        columns_ls = res.response.get('columns')
        output = []
        for row in rows_ls:
            new_row = {}
            for index, column in enumerate(columns_ls):
                new_row[column] = row[index]
            output.append(new_row)
            # pd.DataFrame(data=res.response.get('rows'), columns=res.response.get('columns'))
        return output

    # res = await get_data(auth=full_auth, url=url, method='POST', body=body, session = session ,debug=debug)

    res = await looper(auth=full_auth,
                       method='POST',
                       url=url,
                       arr_fn=arr_fn,
                       offset_params=offset_params,
                       limit=limit,
                       session=session,
                       body_fn=body_fn,
                       debug=debug)

    if is_close_session:
        await session.close()

    return res


async def get_schema(full_auth: DomoFullAuth, id: str,
                     debug: bool = False, log_result: bool = False) -> ResponseGetData:
    url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/datasources/{id}/schema/indexed?includeHidden=false'

    if debug:
        print(url)

    res = await get_data(
        auth=full_auth,
        url=url,
        method='GET',
        debug=debug,
    )

    if log_result:
        print(res)

    return res


# UPLOAD DATASET
async def upload_dataset_stage_1(full_auth: DomoFullAuth,
                                 dataset_id: str,
                                 session: aiohttp.ClientSession = None,
                                 debug: bool = False,
                                 restate_data_tag: str = None,
                                 data_tag: str = None
                                 ):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads"

    body = {
        "action": None,
        "appendId": None
    }
    if not restate_data_tag and not data_tag:
        params = None
    else:
        params = {'dataTag': restate_data_tag or data_tag}
        body.update({'appendId': 'latest'})

    return await get_data(auth=full_auth,
                          url=url, method='POST',
                          body=body,
                          session=session,
                          debug=debug,
                          params=params)


async def upload_dataset_stage_2_file(full_auth: DomoFullAuth,
                                      dataset_id: str,
                                      upload_id: str,
                                      file: io.TextIOWrapper = None,
                                      session: aiohttp.ClientSession = None,
                                      part_id: str = 2,
                                      debug: bool = False

                                      ):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/parts/{part_id}"
    body = file

    if debug:
        print(body)

    res = await get_data(
        url=url,
        method="PUT",
        auth=full_auth,
        content_type='text/csv',
        body=body,
        session=session,
        debug=debug
    )
    res.upload_id = upload_id
    res.dataset_id = dataset_id
    res.part_id = part_id

    return res


async def upload_dataset_stage_2_df(full_auth: DomoFullAuth,
                                    dataset_id: str,
                                    upload_id: str,
                                    upload_df: pd.DataFrame,
                                    session: aiohttp.ClientSession = None,
                                    part_id: str = 2,
                                    debug: bool = False

                                    ):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/parts/{part_id}"
    body = upload_df.to_csv(header=False, index=False)

    # if debug:
    #     print(body)

    res = await get_data(
        url=url,
        method="PUT",
        auth=full_auth,
        content_type='text/csv',
        body=body,
        session=session,
        debug=debug
    )

    res.upload_id = upload_id
    res.dataset_id = dataset_id
    res.part_id = part_id

    return res


async def upload_dataset_stage_3(full_auth: DomoFullAuth,
                                 dataset_id: str,
                                 upload_id: str,
                                 session: aiohttp.ClientSession = None,
                                 update_method: str = 'REPLACE',
                                 restate_data_tag: str = None,
                                 data_tag: str = None,
                                 is_index: bool = False,
                                 debug: bool = False):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/uploads/{upload_id}/commit"

    body = {"index": is_index,
            "action": update_method}

    if restate_data_tag or data_tag:
        if debug:
            print('route_stage_3_updating body')

        body.update({"action": 'APPEND',
                     'dataTag': restate_data_tag or data_tag,
                     'appendId': 'latest' if (restate_data_tag or data_tag) else None,
                     'index': is_index
                     })

    res = await get_data(
        auth=full_auth,
        method="PUT",
        url=url,
        body=body,
        session=session,
        debug=debug
    )

    res.upload_id = upload_id
    res.dataset_id = dataset_id

    return res


async def upload_dataset_stage_4(full_auth: DomoFullAuth,
                                 dataset_id: str,
                                 index_id: str,
                                 session: aiohttp.ClientSession = None,
                                 debug: bool = False):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/indexes/{index_id}/statuses"

    return await get_data(
        auth=full_auth,
        method="GET",
        url=url,
        body=body,
        session=session,
        debug=debug
    )


async def index_dataset(full_auth: DomoFullAuth,
                        dataset_id: str,
                        session: aiohttp.ClientSession = None,
                        debug: bool = False):

    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}/indexes"

    body = {"dataIds": []}

    return await get_data(auth=full_auth, method='POST', body=body, url=url, session=session)


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


async def list_partitions(full_auth: DomoFullAuth,
                          dataset_id: str,
                          body: dict = None,
                          maximum: int = None,
                          loop_until_end: bool = True,
                          session: aiohttp.ClientSession = None,
                          debug: bool = False):
    try:

        is_close_session = False if session else True

        if not session:
            session = aiohttp.ClientSession()

        body = body or generate_list_partitions_body()

        url = f"https://{full_auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/partition/list"

        offset_params = {
            'offset': 'offset',
            'limit': 'limit',
        }

        def arr_fn(res) -> list[dict]:
            return res.response

        res = await looper(auth=full_auth,
                           method='POST',
                           url=url,
                           arr_fn=arr_fn,
                           body=body,
                           offset_params_in_body=True,
                           offset_params=offset_params,
                           loop_until_end=True,
                           session=session,
                           debug=debug)

        if isinstance(res, list):
            return ResponseGetData(status=200,
                                   response=res,
                                   is_success=True)
        else:
            return ResponseGetData(status=400,
                                   response=None,
                                   is_success=False)

    finally:
        if is_close_session:
            await session.close()

# Delete partition has 3 stages
# Stage 1. This marks the data version associated with the partition tag as deleted.  It does not delete the partition tag or remove the association between the partition tag and data version.  There should be no need to upload an empty file – step #3 will remove the data from Adrenaline.


async def delete_partition_stage_1(full_auth: DomoFullAuth,
                                   dataset_id: str,
                                   dataset_partition_id: str,
                                   session: aiohttp.ClientSession = None,
                                   debug: bool = False):

    #url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/partition/{dataset_partition_id}'
    # update on 9/9/2022 based on the conversation with Greg Swensen
    url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/tag/{dataset_partition_id}/data'

    return await get_data(
        auth=full_auth,
        method="DELETE",
        url=url,
        session=session,
        debug=debug
    )
# Stage 2. This will remove the partition association so that it doesn’t show up in the list call.  Technically, this is not required as a partition against a deleted data version will not count against the 400 partition limit, but as the current partitions api doesn’t make that clear, cleaning these up will make it much easier for you to manage.


async def delete_partition_stage_2(full_auth: DomoFullAuth,
                                   dataset_id: str,
                                   dataset_partition_id: str,
                                   session: aiohttp.ClientSession = None,
                                   debug: bool = False):

    url = f'https://{full_auth.domo_instance}.domo.com/api/query/v1/datasources/{dataset_id}/partition/{dataset_partition_id}'

    return await get_data(
        auth=full_auth,
        method="DELETE",
        url=url,
        session=session,
        debug=debug
    )


async def delete(full_auth: DomoFullAuth,
                 dataset_id: str, session: aiohttp.ClientSession = None, debug: bool = False):
    url = f"https://{full_auth.domo_instance}.domo.com/api/data/v3/datasources/{dataset_id}?deleteMethod=hard"

    return await get_data(
        auth=full_auth,
        method="DELETE",
        url=url,
        session=session,
        debug=debug
    )
