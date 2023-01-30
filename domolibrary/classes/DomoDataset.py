# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoDataset.ipynb.

# %% auto 0
__all__ = ['DatasetSchema_Types', 'DatasetSchema_AuthNotProvidedError', 'DatasetSchema_DatasetNotProvidedError',
           'DomoDataset_Schema_Column', 'DomoDataset_Schema', 'DatasetTags_AuthNotProvidedError',
           'DatasetTags_SetTagsError', 'DomoDataset_Tags', 'DomoDataset', 'QueryExecutionError',
           'DomoDataset_DeleteDataset_Error', 'DomoDataset_UploadData_Error',
           'DomoDataset_UploadData_DatasetUploadId_Error', 'DomoDataset_UploadData_UploadData_Error',
           'DomoDataset_CreateDataset_Error']

# %% ../../nbs/classes/50_DomoDataset.ipynb 4
from fastcore.basics import patch, patch_to
import pandas as pd

# %% ../../nbs/classes/50_DomoDataset.ipynb 5
from dataclasses import dataclass, field
from typing import Any, List, Optional
from enum import Enum, auto

import json

import aiohttp

import io

# import datetime as dt

# import asyncio
# import importlib
# import json
# from pprint import pprint

# import pandas as pd

# from ..utils import Exceptions as ex
# from ..utils.Base import Base
# from ..utils.chunk_execution import chunk_list
# from . import DomoCertification as dmdc
# from . import DomoPDP as dmpdp
# from . import DomoTag as dmtg


import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.routes.dataset as dataset_routes

# %% ../../nbs/classes/50_DomoDataset.ipynb 7
class DatasetSchema_Types(Enum):
    STRING = 'STRING'
    DOUBLE = 'DOUBLE'
    LONG = 'LONG'
    DATE = 'DATE'
    DATETIME = 'DATETIME'


class DatasetSchema_AuthNotProvidedError(Exception):
    """return if DatasetSchema request cannot access an auth object"""

    def __init__(self, dataset_id):
        message = f"valid Auth object not provided to dataset - {dataset_id}"
        super().__init__(message)


class DatasetSchema_DatasetNotProvidedError(Exception):
    """return if DatasetSchema request does not have a dataset id"""

    def __init__(self):
        message = f"dataset_id not provided"
        super().__init__(message)


@dataclass
class DomoDataset_Schema_Column:
    name: str
    id: str
    type: DatasetSchema_Types

    @classmethod
    def _from_json(cls, json_obj):
        dd = util_dd.DictDot(json_obj)
        return cls(name=dd.name, id=dd.id, type=dd.type)


@dataclass
class DomoDataset_Schema:
    """class for interacting with dataset schemas"""

    dataset: any = None
    columns: List[DomoDataset_Schema_Column] = field(default_factory=list)

    async def get(
        self,
        auth: Optional[dmda.DomoAuth] = None,
        dataset_id: str = None,
        debug_api: bool = False,
        return_raw_res: bool = False,  # return the raw response
    ) -> List[DomoDataset_Schema_Column]:

        """method that retrieves schema for a dataset"""

        if self.dataset and (not self.dataset.auth and not auth):
            raise DatasetSchema_AuthNotProvidedError(dataset_id = self.dataset.id)

        auth = auth or self.dataset.auth

        if not self.dataset and not dataset_id:
            raise DatasetSchema_DatasetNotProvidedError()

        dataset_id = dataset_id or self.dataset.id

        res = await dataset_routes.get_schema(
            auth=auth, dataset_id=dataset_id, debug_api=debug_api
        )

        if return_raw_res:
            return res.response

        if res.status == 200:
            json_list = res.response.get("tables")[0].get("columns")

            self.columns = [
                DomoDataset_Schema_Column._from_json(json_obj=json_obj)
                for json_obj in json_list
            ]

            return self.columns

# %% ../../nbs/classes/50_DomoDataset.ipynb 12
class DatasetTags_AuthNotProvidedError(Exception):
    """return if DatasetTags request cannot access an auth object"""

    def __init__(self, id):
        message = f"valid Auth object not provided to dataset - {id}"
        super().__init__(message)


class DatasetTags_SetTagsError(Exception):
    """return if DatasetTags request is not successfull"""

    def __init__(self, dataset_id, domo_instance):
        message = f"failed to set tags on dataset - {dataset_id} in {domo_instance}"
        super().__init__(message)


@dataclass
class DomoDataset_Tags:
    """class for interacting with dataset tags"""

    dataset: any = None
    tag_ls: List[str] = field(default_factory=list)

    def _have_prereqs(self, auth, dataset_id):
        """tests if have a parent dataset or prerequsite dataset_id and auth object"""

        if self.dataset and (not self.dataset.auth and not auth):
            raise DatasetTags_AuthNotProvidedError(self.dataset.id)

        auth = auth or self.dataset.auth

        if not self.dataset and not auth:
            raise DatasetTags_AuthNotProvidedError(self.dataset.id)

        dataset_id = dataset_id or self.dataset.id

        return auth, dataset_id

    async def get(
        self,
        dataset_id: str = None,
        auth: Optional[dmda.DomoAuth] = None,
        debug_api: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> List[str]:  # returns a list of tags
        """gets the existing list of dataset_tags"""

        auth, dataset_id = self._have_prereqs(auth=auth, dataset_id=dataset_id)

        res = await dataset_routes.get_dataset_by_id(
            dataset_id=dataset_id, auth=auth, debug_api=debug_api, session=session
        )

        if res.is_success == False:
            print(res)
            return None

        if res.is_success == True:
            tag_ls = json.loads(res.response.get("tags"))
            self.tag_ls = tag_ls

            return tag_ls

    async def set(
        self,
        tag_ls: [str],
        dataset_id: str = None,
        auth: Optional[dmda.DomoAuth] = None,
        debug_api: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> List[str]: # returns a list of tags
        """replaces all tags with a new list of dataset_tags"""

        auth, dataset_id = self._have_prereqs(auth=auth, dataset_id=dataset_id)

        res = await dataset_routes.set_dataset_tags(
            auth=auth,
            tag_ls=list(set(tag_ls)),
            dataset_id=dataset_id,
            debug_api=debug_api,
            session=session,
        )

        if res.status != 200:
            raise DatasetTags_SetTagsError(
                dataset_id=dataset_id, domo_instance=auth.domo_instance
            )

        await self.get(dataset_id=dataset_id, auth=auth)

        return self.tag_ls

# %% ../../nbs/classes/50_DomoDataset.ipynb 15
@patch
async def add(
    self: DomoDataset_Tags,
    add_tag_ls: [str],
    dataset_id: str = None,
    auth: Optional[dmda.DomoAuth] = None,
    debug_api: bool = False,
    session: Optional[aiohttp.ClientSession] = None,
) -> List[str]:  # returns a list of tags
    """appends tags to the list of existing dataset_tags"""

    auth, dataset_id = self._have_prereqs(auth=auth, dataset_id=dataset_id)

    existing_tag_ls = await self.get(dataset_id=dataset_id, auth=auth)
    add_tag_ls += existing_tag_ls

    return await self.set(
        auth=auth,
        dataset_id=dataset_id,
        tag_ls=list(set(add_tag_ls)),
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/classes/50_DomoDataset.ipynb 17
@patch
async def remove(self: DomoDataset_Tags,
                 remove_tag_ls: [str],
                 dataset_id: str = None,
                 auth: dmda.DomoFullAuth = None,
                 debug_api: bool = False,
                 session: Optional[aiohttp.ClientSession] = None
                 ) -> List[str]:  # returns a list of tags
    """removes tags from the existing list of dataset_tags"""

    auth, dataset_id = self._have_prereqs(auth=auth, dataset_id=dataset_id)

    existing_tag_ls = await self.get(dataset_id=dataset_id, auth=auth)

    existing_tag_ls = [
        ex for ex in existing_tag_ls if ex not in remove_tag_ls]

    return await self.set(auth=auth,
                          dataset_id=dataset_id,
                          tag_ls=list(set(existing_tag_ls)),
                          debug_api=debug_api, session=session)


# %% ../../nbs/classes/50_DomoDataset.ipynb 21
@dataclass
class DomoDataset:
    "interacts with domo datasets"

    auth: dmda.DomoAuth = field(repr=False, default=None)

    id: str = ""
    display_type: str = ""
    data_provider_type: str = ""
    name: str = ""
    description: str = ""
    row_count: int = None
    column_count: int = None

    stream_id: int = None

    owner: dict = field(default_factory=dict)
    formula: dict = field(default_factory=dict)

    schema: DomoDataset_Schema = field(default=None)
    # tags: Dataset_Tags = field(default = None)

    # certification: dmdc.DomoCertification = None
    # PDPPolicies: dmpdp.Dataset_PDP_Policies = None

    def __post_init__(self):
        self.schema = DomoDataset_Schema(dataset=self)
        # self.tags = Dataset_Tags(dataset=self)

        # self.PDPPolicies = dmpdp.Dataset_PDP_Policies(self)

    def display_url(self):
        return f"https://{self.auth.domo_instance }.domo.com/datasources/{self.id}/details/overview"

# %% ../../nbs/classes/50_DomoDataset.ipynb 25
@patch(cls_method=True)
async def get_from_id(
    cls: DomoDataset,
    dataset_id: str,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    return_raw_res: bool = False,
):

    """retrieves dataset metadata"""

    res = await dataset_routes.get_dataset_by_id(
        auth=auth, dataset_id=dataset_id, debug_api=debug_api
    )

    if return_raw_res:
        return res.response

    dd = util_dd.DictDot(res.response)
    ds = cls(
        auth=auth,
        id=dd.id,
        display_type=dd.displayType,
        data_provider_type=dd.dataProviderType,
        name=dd.name,
        description=dd.description,
        owner=dd.owner,
        formula=dd.properties.formulas.formulas,
        stream_id=dd.streamId,
        row_count=int(dd.rowCount),
        column_count=int(dd.columnCount),
    )

    # if dd.tags:
    #     ds.tags.tag_ls = json.loads(dd.tags)

    # if dd.certification:
    #     # print('class def certification', dd.certification)
    #     ds.certification = dmdc.DomoCertification._from_json(
    #         dd.certification)

    return ds


# %% ../../nbs/classes/50_DomoDataset.ipynb 29
class QueryExecutionError(Exception):
    def __init__(self, sql, dataset_id, domo_instance):
        self.message = f"error executing {sql} against dataset {dataset_id} in {domo_instance}"
        super.__init__(self, self.message)


@patch_to(DomoDataset, cls_method=True)
async def query_dataset_private(cls: DomoDataset,
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
                                ) -> pd.DataFrame:

    res = await dataset_routes.query_dataset_private(auth=auth,
                                                     dataset_id=dataset_id,
                                                     sql=sql,
                                                     maximum=maximum,
                                                     skip=skip,
                                                     limit=limit,
                                                     loop_until_end=loop_until_end,
                                                     session=session,
                                                     debug_loop=debug_loop,
                                                     debug_api=debug_api
                                                     )

    if not res.is_success:
        raise QueryExecutionError(sql=sql, dataset_id=dataset_id, domo_instance=auth.domo_instance)

    return pd.DataFrame(res.response)


# %% ../../nbs/classes/50_DomoDataset.ipynb 30
class DomoDataset_DeleteDataset_Error(Exception):
    def __init__(self, status, reason, dataset_id, domo_instance):
        message = f"Error deleting {dataset_id} from {domo_instance}: {status} - {reason}"
        super.__init__(message)

@patch_to(DomoDataset)
async def delete(self : DomoDataset,
                    dataset_id=None,
                    auth: dmda.DomoAuth = None,
                    debug_api: bool = False,
                    session: aiohttp.ClientSession = None):

    dataset_id = dataset_id or self.id
    auth = auth or self.auth

    res = await dataset_routes.delete(
        auth=auth,
        dataset_id=dataset_id,
        debug_api=debug_api,
        session=session)

    if not res.is_success:
        raise DomoDataset_DeleteDataset_Error(domo_instance = auth.domo_instance, dataset_id = dataset_id, status = res.status, reason = res.response )
    
    return res

# %% ../../nbs/classes/50_DomoDataset.ipynb 33
class DomoDataset_UploadData_Error(Exception):

    def __init__(self,
                 message_error: str,
                 domo_instance: str,
                 dataset_id: str,
                 stage: int,
                 status="", reason="",
                 partition_key: str = None):

        message_start = f"Stage {stage}:: {message_error} :: API {status} - {reason} :: "
        message_end = f"in {dataset_id} in {domo_instance}"

        message_partition = ""
        if partition_key:
            message_partition = f"for partition - '{partition_key}' "

        super().__init__(message)


class DomoDataset_UploadData_DatasetUploadId_Error(DomoDataset_UploadData_Error):
    def __init__(self, domo_instance: str, dataset_id: str,
                 stage: int = 1, status="", reason="",
                 partition_key: str = None):

        message_error = "unable to retrieve dataset_upload_id"

        super().__init__(message_error=message_error,
                         domo_instance=domo_instance, dataset_id=dataset_id,
                         stage=stage, status=status, reason=reason,
                         partition_key=partition_key)


class DomoDataset_UploadData_UploadData_Error(Exception):
    def __init__(self, domo_instance: str, dataset_id: str,
                 stage: int = 2, status="", reason="",
                 partition_key: str = None):

        message_error = "while uploading data"

        super().__init__(message_error=message_error,
                         domo_instance=domo_instance, dataset_id=dataset_id,
                         stage=stage, status=status, reason=reason,
                         partition_key=partition_key)

    class DomoDataset_UploadData_CommitDatasetUploadId_Error(Exception):
        def __init__(self, domo_instance: str, dataset_id: str,
                     stage: int = 3, status="", reason="",
                     partition_key: str = None):

            message_error = "while commiting dataset_upload_id"

            ssuper().__init__(message_error=message_error,
                              domo_instance=domo_instance, dataset_id=dataset_id,
                              stage=stage, status=status, reason=reason,
                              partition_key=partition_key)


# %% ../../nbs/classes/50_DomoDataset.ipynb 34
@patch_to(DomoDataset)
async def index_dataset(self: DomoDataset,
                        auth: dmda.DomoAuth = None,
                        dataset_id: str = None,
                        debug_api: bool = False,
                        session: aiohttp.ClientSession = None
                        ):

    auth = auth or self.auth
    dataset_id = dataset_id or self.id
    return await dataset_routes.index_dataset(auth=auth, dataset_id=dataset_id, debug_api=debug_api,
                                              session=session)


# %% ../../nbs/classes/50_DomoDataset.ipynb 35
@patch_to(DomoDataset)
async def upload_data(self : DomoDataset,
                      upload_df: pd.DataFrame = None,
                      upload_df_ls: list[pd.DataFrame] = None,
                      upload_file: io.TextIOWrapper = None,

                      upload_method: str = 'REPLACE',  # APPEND or REPLACE
                      partition_key: str = None,

                      is_index: bool = True,

                      dataset_id: str = None,
                      dataset_upload_id=None,

                      auth: dmda.DomoAuth = None,

                      session: aiohttp.ClientSession = None,
                      debug_api: bool = False,
                      debug_prn: bool = False
                      ):

    auth = auth or self.auth
    dataset_id = dataset_id or self.id

    upload_df_list = upload_df_list or [upload_df]

    # stage 1 get uploadId
    if not dataset_upload_id:
        if debug_prn:
            print(f"\n\n🎭 starting Stage 1")

        stage_1_res = await dataset_routes.upload_dataset_stage_1(auth=auth,
                                                                  dataset_id=dataset_id,
                                                                  session=session,
                                                                  data_tag=partition_key,
                                                                  debug_api=debug_api
                                                                  )
        if debug_prn:
            print(f"\n\n🎭 Stage 1 response -- {stage_1_res.status}")

        dataset_upload_id = stage_1_res.response.get('uploadId')

    if not dataset_upload_id:
        raise DomoDataset_UploadData_DatasetUploadId_Error(
            domo_instnace=auth.domo_instance,  dataset_id=dataset_id, stage=1, partition_key=partition_key,
            status=stage_1_res.status, reason=stage_1_res.response)

    # stage 2 upload_dataset
    stage_2_res = None

    if upload_file:
        if debug_prn:
            print(f"\n\n🎭 starting Stage 2 - upload file")

        stage_2_res = await asyncio.gather(*[dataset_routes.upload_dataset_stage_2_file(auth=auth,
                                                                                        dataset_id=dataset_id,
                                                                                        upload_id=dataset_upload_id,
                                                                                        part_id=1,
                                                                                        file=upload_file,
                                                                                        session=session, debug_api=debug_api)])

    else:
        if debug_prn:
            print(
                f"\n\n🎭 starting Stage 2 - {len(upload_df_list)} - number of parts")
        stage_2_res = await asyncio.gather(*[dataset_routes.upload_dataset_stage_2_df(auth=auth,
                                                                                      dataset_id=dataset_id,
                                                                                      upload_id=dataset_upload_id,
                                                                                      part_id=index + 1,
                                                                                      upload_df=df,
                                                                                      session=session, debug_api=debug_api) for index, df in enumerate(upload_df_list)])

    for res in stage_2_res:
        if not res.is_success:
            raise DomoDataset_UploadData_UploadData_Error(
                domo_instance=auth.domo_instance, dataset_id=dataset_id, stage=2, partition_key=partition_key,
                status=res.status, reason=res.response)

    if debug_prn:
        print(f"🎭 Stage 2 - upload data: complete")

    # stage 3 commit_data
    if debug_prn:
        print(f"\n\n🎭 starting Stage 3 - commit dataset_upload_id")

    await asyncio.sleep(10)  # wait for uploads to finish
    stage3_res = await dataset_routes.upload_dataset_stage_3(auth=auth,
                                                             dataset_id=dataset_id,
                                                             upload_id=dataset_upload_id,
                                                             update_method=upload_method,
                                                             data_tag=partition_key,
                                                             is_index=False,
                                                             session=session,
                                                             debug_api=debug_api)

    if not stage3_res.is_success:
        raise DomoDataset_UploadData_CommitDatasetUploadId_Error(
            domo_instance=auth.domo_instance, dataset_id=dataset_id, partition_key=partition_key, stage=3,
            status=stage3_res.status, reason=stage3_res.response)

    if debug_prn:
        print(f"\n🎭 stage 3 - commit dataset: complete")

    if is_index:
        await asyncio.sleep(3)
        return await self.index_dataset(auth=auth,
                                        dataset_id=dataset_id,
                                        debug_api=debug_api,
                                        session=session)

    return stage3_res


# %% ../../nbs/classes/50_DomoDataset.ipynb 37
@patch_to(DomoDataset)
async def list_partitions(self : DomoDataset,
                            auth: dmda.DomoAuth = None,
                            dataset_id: str = None,
                            debug_api: bool = False,
                            session: aiohttp.ClientSession = None
                            ):

    auth = auth or self.auth
    dataset_id = dataset_id or self.id

    res = await dataset_routes.list_partitions(auth=auth, dataset_id=dataset_id, debug_api=debug_api,
                                                session=session)
    if res.status != 200:
        return None

    return res.response

# %% ../../nbs/classes/50_DomoDataset.ipynb 39
class DomoDataset_CreateDataset_Error(Exception):
    def __init__(self, domo_instance: str, dataset_name: str, status: int, reason: str):
        message = f"Failure to create dataset {dataset_name} in {domo_instance} :: {status} - {reason}"


@patch_to(DomoDataset, cls_method=True)
async def create(cls: DomoDataset,
                 dataset_name: str,
                 dataset_type='api',

                 schema={"columns": [
                     {"name": 'col1', "type": 'LONG', "upsertKey": False},
                     {"name": 'col2', "type": 'STRING', "upsertKey": False}
                 ]},
                 auth: dmda.DomoAuth = None,
                 debug_api: bool = False, 
                 session : aiohttp.ClientSession = None
                 ):
    

    res = await dataset_routes.create(dataset_name=dataset_name,
                                      dataset_type=dataset_type,
                                      schema=schema, auth=auth, debug_api=debug_api, session=session
                                      )

    if not res.is_success:
        raise DomoDataset_CreateDataset_Error(
            domo_instance=auth.domo_instance, dataset_name=dataset_name, 
            status=res.status, reason=res.response)

    dataset_id = res.response.get('dataSource').get('dataSourceId')

    return await cls.get_from_id(dataset_id=dataset_id, auth=auth)

