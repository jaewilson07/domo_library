import asyncio
import datetime as dt
import importlib
import io
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from pprint import pprint
from typing import Any, List

import aiohttp
import pandas as pd

from ..utils import Exceptions as ex
from ..utils.Base import Base
from ..utils.chunk_execution import chunk_list
from ..utils.DictDot import DictDot
from . import DomoCertification as dmdc
from . import DomoPDP as dmpdp
from . import DomoTag as dmtg
from .DomoAuth import DomoDeveloperAuth, DomoFullAuth
from .routes import dataset_routes

importlib.reload(dmtg)


@dataclass
class Schema_Column:
    name: str
    id: str
    type: str
    dataset: Any

    @classmethod
    def _from_json(cls, json_obj, domo_dataset):
        dd = DictDot(json_obj)
        return cls(
            name=dd.name,
            id=dd.id,
            type=dd.type,
            dataset=domo_dataset
        )


@dataclass(init=False)
class Dataset_Schema:
    columns: List[Schema_Column] = field(default_factory=list)

    def __init__(self, dataset):
        self.dataset = dataset
        self.columns = []

    async def get(self, full_auth: DomoFullAuth = None, debug: bool = False) -> List[Schema_Column]:
        full_auth = full_auth or self.dataset.full_auth

        res = await dataset_routes.get_schema(full_auth=self.dataset.full_auth, id=self.dataset.id, debug=debug)

        if res.status == 200:
            json_list = res.response.get('tables')[0].get('columns')

            self.columns = []
            for json_obj in json_list:
                dc = Schema_Column._from_json(
                    json_obj=json_obj, domo_dataset=self.dataset)
                if dc not in self.columns:
                    self.columns.append(dc)

            return self.columns


@dataclass
class DomoDataset:
    "interacts with domo datasets"
    full_auth: DomoFullAuth = field(repr=False, default=None)
    dev_auth: DomoDeveloperAuth = field(repr=False, default=None)

    id: str = ''
    display_type: str = ''
    data_provider_type: str = ''
    name: str = ''
    description: str = ''
    row_count: int = None
    column_count: int = None
    owner: dict = field(default_factory=dict)
    formula: dict = field(default_factory=dict)
    stream_id: int = None
    domo_instance: str = ''

    tags: dmtg.Dataset_Tags = None
    certification: dmdc.DomoCertification = None
    PDPPolicies: dmpdp.Dataset_PDP_Policies = None
    schema: Dataset_Schema = None

    def __post_init__(self):
        self.PDPPolicies = dmpdp.Dataset_PDP_Policies(self)
        self.schema = Dataset_Schema(self)
        self.tags = dmtg.Dataset_Tags(dataset=self)

    def display_url(self):
        return f'https://{self.domo_instance or self.full_auth.domo_instance}.domo.com/datasources/{self.id}/details/overview'

    @classmethod
    async def get_from_id(cls,
                          id: str,
                          full_auth: DomoFullAuth,
                          debug: bool = False, log_results: bool = False):

        # try:
        res = await dataset_routes.get_dataset_by_id(full_auth=full_auth,
                                                     id=id or cls.id, debug=debug)
        if res.status == 404:
            print(
                "f error retrieving get_from_id {full_auth.domo_instance} - {id} status = 404")
            raise ex.InvalidDataset(
                domo_instance=full_auth.domo_instance, dataset_id=id)

        # except Exception as e:
        #     print(e)
        #     return None

        if debug:
            pprint(res)

        dd = DictDot(res.response)
        ds = cls(
            full_auth=full_auth,
            id=dd.id,
            display_type=dd.displayType,
            data_provider_type=dd.dataProviderType,
            name=dd.name,
            description=dd.description,
            owner=dd.owner,
            formula=dd.properties.formulas.formulas,
            stream_id=dd.streamId,
            row_count=int(dd.rowCount),
            column_count=int(dd.columnCount)
        )

        if dd.tags:
            ds.tags.tag_ls = json.loads(dd.tags)

        if dd.certification:
            # print('class def certification', dd.certification)
            ds.certification = dmdc.DomoCertification._from_json(
                dd.certification)

        return ds

    @classmethod
    async def query_dataset(cls,
                            sql: str,
                            dataset_id: str,
                            dev_auth: DomoDeveloperAuth,
                            debug: bool = False,
                            session: aiohttp.ClientSession = None) -> pd.DataFrame:

        if debug:
            print("query dataset class method")
            print({'dataset_id': dataset_id,
                   'dev_auth': dev_auth})

        res = await dataset_routes.query_dataset_public(dev_auth=dev_auth, id=dataset_id, sql=sql, session=session,
                                                        debug=debug)

        if debug:
            print(res.response)

        if res.status == 200:
            df = pd.DataFrame(data=res.response.get('rows'),
                              columns=res.response.get('columns'))
            return df
        return None

    @classmethod
    async def query_dataset_private(cls,
                                    sql: str,
                                    dataset_id: str,
                                    full_auth: DomoFullAuth,
                                    debug: bool = False,
                                    session: aiohttp.ClientSession = None) -> pd.DataFrame:

        if debug:
            print("query dataset class method")
            print({'dataset_id': dataset_id,
                   'full_auth': full_auth})

        res = await dataset_routes.query_dataset_private(full_auth=full_auth, id=dataset_id, sql=sql, session=session,
                                                         debug=debug)

        return pd.DataFrame(res)

    async def upload_csv(self,
                         upload_df: pd.DataFrame = None,
                         upload_df_list: list[pd.DataFrame] = None,
                         upload_file: io.TextIOWrapper = None,

                         full_auth: DomoFullAuth = None,
                         upload_method: str = 'REPLACE',
                         dataset_id: str = None,
                         dataset_upload_id=None,
                         partition_key: str = None,
                         is_index: bool = True,
                         session: aiohttp.ClientSession = None,
                         debug: bool = False):

        full_auth = full_auth or self.full_auth
        dataset_id = dataset_id or self.id

        upload_df_list = upload_df_list or [upload_df]

        # stage 1 get uploadId
        if not dataset_upload_id:
            if debug:
                print(f"\n\n🎭 starting Stage 1")

            res = await dataset_routes.upload_dataset_stage_1(full_auth=full_auth,
                                                              dataset_id=dataset_id,
                                                              session=session,
                                                              data_tag=partition_key,
                                                              debug=debug
                                                              )
            if debug:
                print(f"\n\n🎭 Stage 1 response -- {res.status}")
                print(res)

            dataset_upload_id = res.response.get('uploadId')

        # stage 2 upload_dataset

        if debug:
            print(
                f"\n\n🎭 starting Stage 2 - {len(upload_df_list)} - number of parts")

        stage_2_res = None

        if upload_file:
            if debug:
                print('stage 2 - file')
            stage_2_res = await dataset_routes.upload_dataset_stage_2_file(full_auth=full_auth,
                                                                           dataset_id=dataset_id,
                                                                           upload_id=dataset_upload_id,
                                                                           part_id=1,
                                                                           file=upload_file,
                                                                           session=session, debug=debug)
            if debug:
                print(f"🎭 Stage 2 response -- {stage_2_res.status}")
                print(stage_2_res.print(is_pretty=True))

        else:
            if debug:
                print('stage 2 - df')
            stage_2_res = await asyncio.gather(*[dataset_routes.upload_dataset_stage_2_df(full_auth=full_auth,
                                                                                          dataset_id=dataset_id,
                                                                                          upload_id=dataset_upload_id,
                                                                                          part_id=index + 1,
                                                                                          upload_df=df,
                                                                                          session=session, debug=debug) for index, df in enumerate(upload_df_list)])

            if debug:
                for res in stage_2_res:
                    print(f"🎭 Stage 2 response -- {res.status}")
                    res.print(is_pretty=True)

        # return stage_2_res

#         # stage 3 commit_data
        if debug:
            print(f"\n\n🎭 starting Stage 3")
        await asyncio.sleep(10)

        stage3_res = await dataset_routes.upload_dataset_stage_3(full_auth=full_auth,
                                                                 dataset_id=dataset_id,
                                                                 upload_id=dataset_upload_id,
                                                                 update_method=upload_method,
                                                                 data_tag=partition_key,
                                                                 is_index=False,
                                                                 session=session,
                                                                 debug=debug)

        if debug:
            print(f"\n🎭 stage 3 res - {res.status}")
            print(stage3_res)

        if is_index:
            await self.index_dataset(full_auth=full_auth,
                                     dataset_id=dataset_id,
                                     debug=debug,
                                     session=session)

        return stage3_res

    async def index_dataset(self,
                            full_auth: DomoFullAuth = None,
                            dataset_id: str = None,
                            debug: bool = False,
                            session: aiohttp.ClientSession = None
                            ):

        full_auth = full_auth or self.full_auth
        dataset_id = dataset_id or self.id
        return await dataset_routes.index_dataset(full_auth=full_auth, dataset_id=dataset_id, debug=debug,
                                                  session=session)

    async def list_partitions(self,
                              full_auth: DomoFullAuth = None,
                              dataset_id: str = None,
                              debug: bool = False,
                              session: aiohttp.ClientSession = None
                              ):

        full_auth = full_auth or self.full_auth
        dataset_id = dataset_id or self.id

        res = await dataset_routes.list_partitions(full_auth=full_auth, dataset_id=dataset_id, debug=debug,
                                                   session=session)
        if res.status != 200:
            return None
        return res.response

    async def delete_partition(self,
                               dataset_partition_id: str,

                               dataset_id: str = None,
                               empty_df: pd.DataFrame = None,

                               full_auth: DomoFullAuth = None,

                               is_index: bool = True,
                               debug: bool = False,
                               session: aiohttp.ClientSession = None):

        is_close_session = True if not session else False

        session = session or aiohttp.ClientSession()
        full_auth = full_auth or self.full_auth
        dataset_id = dataset_id or self.id

#        if empty_df is None:
#            empty_df = await self.query_dataset_private(full_auth=full_auth,
#                                                        dataset_id=dataset_id,
#                                                        sql="SELECT * from table limit 1",
#                                                        debug=False)
#
#        await self.upload_csv(upload_df=empty_df.head(0),
#                              upload_method='REPLACE',
#                              is_index=is_index,
#                              partition_key=dataset_partition_id,
#                              session=session,
#                              debug=False)
        if debug:
            print(f"\n\n🎭 starting Stage 1")

        res = await dataset_routes.delete_partition_stage_1(full_auth=full_auth,
                                                            dataset_id=dataset_id,
                                                            dataset_partition_id=dataset_partition_id,
                                                            debug=debug, session=session)
        if debug:
            print(f"\n\n🎭 Stage 1 response -- {res.status}")
            print(res)

        stage_2_res = None
        if debug:
            print('starting Stage 2')
        stage_2_res = await dataset_routes.delete_partition_stage_2(full_auth=full_auth,
                                                                    dataset_id=dataset_id,
                                                                    dataset_partition_id=dataset_partition_id,
                                                                    debug=debug, session=session)
        if debug:
            print(f"\n\n🎭 Stage 2 response -- {stage_2_res.status}")

        stage_3_res = None
        if debug:
            print('starting Stage 3')
        stage_3_res = await dataset_routes.index_dataset(full_auth=full_auth,
                                                         dataset_id=dataset_id,
                                                         debug=debug, session=session)
        if debug:
            print(f"\n\n🎭 Stage 3 response -- {stage_3_res.status}")

        if is_close_session:
            await session.close()

        if debug:
            print(stage_3_res)

        if stage_3_res.status == 200:
            return res.response

    async def reset_dataset(self,
                            full_auth: DomoFullAuth = None,
                            is_index: bool = True,
                            debug: bool = False
                            ):
        execute_reset = input(
            "This function will delete all rows.  Type BLOW_ME_AWAY to execute:")

        if execute_reset != 'BLOW_ME_AWAY':
            print("You didn't type BLOW_ME_AWAY, moving on.")
            return None

        full_auth = full_auth or self.full_auth
        dataset_id = self.id

        if not full_auth:
            raise Exception("full_auth required")

        session = aiohttp.ClientSession()

        # create empty dataset to retain schema
        empty_df = await self.query_dataset_private(full_auth=full_auth,
                                                    dataset_id=dataset_id,
                                                    sql="SELECT * from table limit 1",
                                                    session=session,
                                                    debug=debug)
        empty_df = empty_df.head(0)

        # get partition list
#         partition_list = await dataset_routes.list_partitions(full_auth=full_auth,
#                                                               dataset_id=self.id,
#                                                               debug=debug,
#                                                               session=session)

#         if len(partition_list) > 0:
#             partition_list = chunk_list(partition_list, 100)

#             for index, pl in enumerate(partition_list):
#                 print(f'🥫 starting chunk {index + 1} of {len(partition_list)}')

#                 await asyncio.gather(*[self.delete_partition(full_auth=full_auth,
#                                                              dataset_partition_id=partition.get('partitionId'),
#                                                              session=session,
#                                                              empty_df=empty_df,
#                                                              debug=False) for partition in pl])
#                 if is_index:
#                     await self.index_dataset(session=session)

        res = await self.upload_csv(upload_df=empty_df,
                                    upload_method='REPLACE',
                                    is_index=is_index,
                                    session=session,
                                    debug=False)

        await session.close()
        return True

    async def delete(self,
                     dataset_id=None,
                     full_auth: DomoFullAuth = None,
                     debug: bool = False,
                     session: aiohttp.ClientSession = None):
        try:
            is_close_session = False

            if not session:
                session = aiohttp.ClientSession()
                is_close_session = True

            return await dataset_routes.delete(
                full_auth=full_auth or self.full_auth,
                dataset_id=dataset_id or self.id,
                debug=debug,
                session=session)

        finally:
            if is_close_session:
                await session.close()

    # async def create(self,
    #                   ds_name,
    #                   ds_type ='api',
    #                   schema = { "columns": [ {
    #                       "name": 'col1',
    #                       "type": 'LONG',
    #                       "metadata": None,
    #                       "upsertKey": False}
    #                   ]},
    #                   full_auth:DomoFullAuth = None,
    #                   debug:bool = False)
