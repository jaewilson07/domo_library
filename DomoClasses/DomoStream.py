import aiohttp
import re
from dataclasses import field, dataclass
from sql_metadata import Parser
from typing import List, Any

from .DomoAuth import DomoFullAuth
import Library.DomoClasses.DomoDatacenter as dmdc
import Library.utils.LoggerClass as lc
from .routes import stream_routes
from ..utils.Base import Base
from ..utils.DictDot import DictDot


custom_query = ['enteredCustomQuery', 'query', 'customQuery']


@dataclass
class StreamConfig:
    name: str
    type: str
    value: str
    value_clean: str = None


@dataclass
class DomoStream(Base):
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
    async def get_definition(cls,
                             full_auth: DomoFullAuth, 
                             stream_id: str, 
                             session: aiohttp.ClientSession = None, 
                             logger: lc.MyLogger = None):
        if logger : 
            logger.log_info (f"⚙️ get_definition: for {stream_id}")
        if stream_id is None:
            return None

        res = await stream_routes.get_stream_definition(full_auth=full_auth,
                                                        stream_id=stream_id,
                                                        session=session
                                                        )

        if res.status != 200:
            error_str = f"get_definition: error retrieving stream {stream_id} from {full_auth.domo_instance}"
            print(error_str)
            if logger : 
                logger.log_error(error_str)
            return None

        dd = DictDot(res.response)

        sd = cls(
            id=dd.id,
            transport_description=dd.transport.description,
            transport_version=dd.transport.version,
            update_method=dd.updateMethod,
            data_provider_name=dd.dataProvider.name,
            data_provider_key=dd.dataProvider.key,
            dataset_id=dd.dataSource.id
        )
        if dd.account:
            sd.account_id = dd.account.id
            sd.account_display_name = dd.account.displayName
            sd.account_userid = dd.account.userId

        sd.configuration = []

        for config in dd.configuration:
            sc = StreamConfig(
                name=config.name,
                type=config.type,
                value=config.value)

            if sc.name in custom_query:
                sc.value_clean = sc.value.replace('\n', ' ')
                sc.value_clean = re.sub(' +', ' ', sc.value_clean)
                sd.configuration_query = sc.value_clean

                try:
                    for table in Parser(sc.value).tables:
                        sd.configuration_tables.append(table)
                    sd.configuration_tables = sorted(
                        list(set(sd.configuration_tables)))
                    
                except Exception as e:
                    if logger : 
                        logger.log_error(f"get_definition: unable to parse table for stream {stream_id}. Exception : {e}")
                    print('ALERT: unable to parse table')
                    sd.configuration_tables = ['unable to auto-parse query']

            sd.configuration.append(sc)
        return sd

    @classmethod
    async def create_stream(cls,
                            cnfg_body,
                            full_auth: DomoFullAuth = None,
                            session: aiohttp.ClientSession = None,
                            debug: bool = False,
                            log_result: bool = False):
        return await stream_routes.create_stream(full_auth=full_auth,
                                                 body=cnfg_body,
                                                 session=session,
                                                 debug=debug)

    @classmethod
    async def update_stream(cls,
                            cnfg_body,
                            stream_id,
                            full_auth: DomoFullAuth = None,
                            session: aiohttp.ClientSession = None,
                            debug: bool = False,
                            log_result: bool = False):

        return await stream_routes.update_stream(full_auth=full_auth,
                                                 stream_id=stream_id,
                                                 body=cnfg_body,
                                                 session=session,
                                                 debug=debug)

    @classmethod
    async def upsert_connector(cls,
                               cnfg_body,
                               match_name=None,
                               full_auth: DomoFullAuth = None,
                               session: aiohttp.ClientSession = None,
                               debug: bool = False,
                               log_result: bool = False):
        search_body = dmdc.DomoDatacenter.generate_search_datacenter_body_by_name(
            entity_name=match_name)

        search_res = await dmdc.DomoDatacenter.search_datacenter(full_auth=full_auth,
                                                                 body=search_body,
                                                                 session=session,
                                                                 debug=debug,
                                                                 log_result=log_result)

        existing_ds = next((ds for ds in search_res if ds.get(
            'name').lower() == match_name.lower()), None)

        if debug:
            print(
                f"existing_ds - {existing_ds.id if existing_ds else ' not found '}")

        if existing_ds:
            existing_ds = await DomoDataset.getDomoProps(id=existing_ds.get('databaseId'),
                                                         full_auth=full_auth)
            return await cls.update_stream(cnfg_body,
                                           stream_id=existing_ds.stream_id,
                                           full_auth=full_auth,
                                           session=session,
                                           debug=False,
                                           log_result=False)
        else:
            return await cls.create_stream(cnfg_body,
                                           full_auth=full_auth,
                                           session=session,
                                           debug=debug,
                                           log_result=log_result)
