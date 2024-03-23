# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoStream.ipynb.

# %% auto 0
__all__ = ['custom_query', 'StreamConfig', 'DomoStream']

# %% ../../nbs/classes/50_DomoStream.ipynb 3
from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod
import dateutil.parser as dtut
from typing import Union

import datetime as dt
import re


import httpx

from nbdev.showdoc import patch_to

import domolibrary.utils.convert as cd
import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.classes.DomoDataset as dmds
import domolibrary.classes.DomoDatacenter as dmdc
import domolibrary.client.DomoError as de
import domolibrary.routes.stream as stream_routes

# %% ../../nbs/classes/50_DomoStream.ipynb 6
custom_query = ["enteredCustomQuery", "query", "customQuery"]


@dataclass
class StreamConfig:
    name: str
    type: str
    value: str
    value_clean: str = None


@dataclass
class DomoStream:
    id: str
    dataset_id: str
    transport_description: str
    transport_version: int
    update_method: str
    data_provider_name: str
    data_provider_key: str
    account_id: str = None
    account_display_name: str = None
    account_userid: str = None

    configuration: list[StreamConfig] = field(default_factory=list)
    configuration_tables: list[str] = field(default_factory=list)
    configuration_query: str = None

    @classmethod
    async def get_stream_by_id(
        cls,
        auth: dmda.DomoAuth,
        stream_id: str,
        session: Optional[httpx.AsyncClient] = None,
    ):

        if stream_id is None:
            return None

        res = await stream_routes.get_stream_by_id(
            auth=auth, stream_id=stream_id, session=session
        )

        if res.status != 200:
            error_str = f"get_stream_by_id: error retrieving stream {stream_id} from {auth.domo_instance}"
            print(error_str)

            return None

        dd = util_dd.DictDot(res.response)

        sd = cls(
            id=dd.id,
            transport_description=dd.transport.description,
            transport_version=dd.transport.version,
            update_method=dd.updateMethod,
            data_provider_name=dd.dataProvider.name,
            data_provider_key=dd.dataProvider.key,
            dataset_id=dd.dataSource.id,
        )
        if dd.account:
            sd.account_id = dd.account.id
            sd.account_display_name = dd.account.displayName
            sd.account_userid = dd.account.userId

        sd.configuration = []

        for config in dd.configuration:
            sc = StreamConfig(name=config.name, type=config.type, value=config.value)

            if sc.name in custom_query:
                sc.value_clean = sc.value.replace("\n", " ")
                sc.value_clean = re.sub(" +", " ", sc.value_clean)
                sd.configuration_query = sc.value_clean

                try:
                    for table in dtut.parse(sc.value).tables:
                        sd.configuration_tables.append(table)
                    sd.configuration_tables = sorted(list(set(sd.configuration_tables)))

                except Exception as e:
                    print("ALERT: unable to parse table")
                    sd.configuration_tables = ["unable to auto-parse query"]

            sd.configuration.append(sc)
        return sd

    @classmethod
    async def create_stream(
        cls,
        cnfg_body,
        auth: dmda.DomoAuth = None,
        session: Optional[httpx.AsyncClient] = None,
        debug_api: bool = False,
    ):
        return await stream_routes.create_stream(
            auth=auth, body=cnfg_body, session=session, debug_api=debug_api
        )

    @classmethod
    async def update_stream(
        cls,
        cnfg_body,
        stream_id,
        auth: dmda.DomoAuth = None,
        session: Optional[httpx.AsyncClient] = None,
        debug_api: bool = False,
    ):

        return await stream_routes.update_stream(
            auth=auth,
            stream_id=stream_id,
            body=cnfg_body,
            session=session,
            debug_api=debug_api,
        )

    @classmethod
    async def upsert_connector(
        cls,
        cnfg_body,
        match_name=None,
        auth: dmda.DomoAuth = None,
        session: Optional[httpx.AsyncClient] = None,
        debug_api: bool = False,
    ):
        search_body = dmdc.DomoDatacenter.generate_search_datacenter_body_by_name(
            entity_name=match_name
        )

        search_res = await dmdc.DomoDatacenter.search_datacenter(
            auth=auth, body=search_body, session=session, debug_api=debug_api
        )

        existing_ds_obj = next(
            (ds for ds in search_res if ds.get("name").lower() == match_name.lower()),
            None,
        )

        # if debug_api:
        #     print(
        #         f"existing_ds - {existing_ds.id if existing_ds else ' not found '}")

        if existing_ds_obj:
            existing_ds = await dmds.DomoDataset.get_from_id(
                dataset_id=existing_ds.get("databaseId"), auth=auth
            )
            return await cls.update_stream(
                cnfg_body,
                stream_id=existing_ds.stream_id,
                auth=auth,
                session=session,
                debug_api=False,
            )
        else:
            return await cls.create_stream(
                cnfg_body, auth=auth, session=session, debug_api=debug_api
            )
