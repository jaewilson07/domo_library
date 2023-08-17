import asyncio
import importlib
from dataclasses import dataclass, field
from enum import Enum

import aiohttp

import Library.DomoClasses.DomoAuth as dmda

from .DomoDataset import DomoDataset
from .routes import account_routes, datacenter_routes

importlib.reload(datacenter_routes)


class DomoEntity(Enum):
    DATASET = 'DATA_SOURCE'
    DATAFLOW = 'DATAFLOW'
    PAGE = 'PAGE'
    CARD = 'CARD'
    ACCOUNT = 'ACCOUNT'


class DomoDatacenter:
    full_auth: dmda.DomoFullAuth = None

    @classmethod
    def generate_search_datacenter_body(cls, entities_list: list[str] = ['DATASET'],
                                        filters: list[dict] = None,
                                        combineResults: bool = True,
                                        count: int = 100,
                                        offset: int = 0):
        return {
            "entities": entities_list,
            #old value on Jan 13
            #"entityList": entities_list,
            "filters": filters or [],
            "combineResults": combineResults,
            "query": "*",
            "count": count,
            "offset": offset}

    @classmethod
    def generate_search_datacenter_body_by_name(cls,
                                                entity_name, entities_list: list[str] = ['DATASET'],
                                                filters: list[dict] = None,
                                                combineResults: bool = True,
                                                count: int = 100,
                                                offset: int = 0):

        body = cls.generate_search_datacenter_body(
            entities_list, filters, combineResults, count, offset)
        body['filters'].append(
            {'field': 'name_sort', 'filterType': 'wildcard', 'query': entity_name})
        return body

    @classmethod
    async def search_datacenter(cls, full_auth: dmda.DomoFullAuth,
                                body: dict = None,
                                session: aiohttp.ClientSession = None,
                                maximum: int = None,
                                debug: bool = False, log_result: bool = False) -> list:

        def arr_fn(res):
            # pprint(res.response)
            return res.response.get('searchObjects')

        def alter_maximum_fn(res):
            return res.response.get('totalResultCount')

        if not body:
            body = cls.generate_search_datacenter_body(
                entities_list=['DATASET'],
                filters=[],
                count=1000,
                offset=0,
                combineResults=False
            )

        if debug:
            print(body)

        if maximum:
            return await datacenter_routes.search_datacenter(full_auth=full_auth,
                                                             arr_fn=arr_fn,
                                                             maximum=maximum,
                                                             body=body,
                                                             session=session,
                                                             debug=debug)

        return await datacenter_routes.search_datacenter(full_auth=full_auth,
                                                         arr_fn=arr_fn,
                                                         alter_maximum_fn=alter_maximum_fn,
                                                         body=body,
                                                         session=session,
                                                         debug=debug)

    @classmethod
    async def search_datasets(cls,
                              full_auth=dmda.DomoFullAuth,
                              body: dict = None,
                              session: aiohttp.ClientSession = None,
                              maximum: int = None,
                              debug=False) -> list[DomoDataset]:

        if not body:
            body = DomoDatacenter.generate_search_datacenter_body(
                
                entities_list=['DATASET'],
                filters=[],
                count=1000,
                offset=0,
                combineResults=False
            )

        if debug:
            print(body)

        json_list = await cls.search_datacenter(full_auth=full_auth,
                                                maximum=maximum,
                                                body=body,
                                                session=session,
                                                debug=False)

        if json_list:
            return await asyncio.gather(
                *[DomoDataset.get_from_id(id=json_obj.get('databaseId'), full_auth=full_auth, debug=debug)
                  for json_obj in json_list]
            )

    @classmethod
    async def get_lineage_upstream(cls,
                                   full_auth: dmda.DomoFullAuth,
                                   entity_id,
                                   entity_type,
                                   session: aiohttp.ClientSession = None,
                                   debug: bool = False,
                                   debug_prn: bool = False):

        import Library.DomoClasses.DomoDataflow as dmdf
        import Library.DomoClasses.DomoDataset as dmds

        try:
            if not session:
                session = aiohttp.ClientSession()
                is_close_session = True

            res = await datacenter_routes.get_lineage_upstream(full_auth=full_auth,
                                                               entity_type=entity_type,
                                                               entity_id=entity_id,
                                                               session=session, debug=debug)

            if res.status == 200:
                obj = res.response

                domo_obj = []
                for key, item in obj.items():
                    if item.get('type') == 'DATA_SOURCE':
                        domo_obj.append(await dmds.DomoDataset.get_from_id(full_auth=full_auth, id=item.get('id')))

                    if item.get('type') == 'DATAFLOW':
                        # print(item.get('id'))
                        domo_obj.append(await dmdf.DomoDataflow.get_from_id(full_auth=full_auth, id=item.get('id')))
                        pass

                return domo_obj
            else:
                return None

        finally:
            if is_close_session:
                await session.close()

    @classmethod
    async def get_accounts(cls, full_auth: dmda.DomoFullAuth,
                           search_str: str = None,
                           is_exact_match: bool = True,
                           maximum: int = None,
                           session: aiohttp.ClientSession = None, debug: bool = False):

        import Library.DomoClasses.DomoAccount as dma

        json_ls = None

        if search_str:
            body = datacenter_routes.generate_search_datacenter_account_body(
                search_str=search_str, is_exact_match=is_exact_match)

            search_ls = await cls.search_datacenter(full_auth=full_auth,
                                                    maximum=maximum,
                                                    body=body,
                                                    session=session,
                                                    debug=debug)

            if not search_ls or len(search_ls) == 0:
                return None

            json_ls = [{'id': obj.get('databaseId')} for obj in search_ls]

        else:
            res = await account_routes.get_accounts(full_auth=full_auth, session=session, debug=debug)
            
            if debug:
                print(res)

            if res.status != 200:
                return None

            json_ls = res.response

        domo_account_ls = await asyncio.gather(*[dma.DomoAccount.get_from_id(account_id=obj.get('id'), full_auth=full_auth) for obj in json_ls])

        if is_exact_match and search_str:
            return next((domo_account for domo_account in domo_account_ls if domo_account.name == search_str), None)

        return domo_account_ls
