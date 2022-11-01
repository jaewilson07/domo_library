import aiohttp
import asyncio

from .DomoAuth import DomoFullAuth
from .DomoDataset import DomoDataset
from .routes import datacenter_routes


class DomoDatacenter:
    
    @classmethod
    def generate_search_datacenter_body(cls, entities_list: list[str] = ['DATASET'],
                                        filters: list[dict] = None,
                                        combineResults: bool = True,
                                        count: int = 100,
                                        offset: int = 0):
        return {
            "entities": entities_list,
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
        
        body = cls.generate_search_datacenter_body( entities_list, filters,combineResults,count,offset)
        body['filters'].append({ 'field': 'name_sort', 'filterType': 'wildcard', 'query': entity_name })
        return body
     

    @classmethod
    async def search_datacenter(cls, full_auth: DomoFullAuth,
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
                                                             debug=False)

        return await datacenter_routes.search_datacenter(full_auth=full_auth,
                                                         arr_fn=arr_fn,
                                                         alter_maximum_fn=alter_maximum_fn,
                                                         body=body,
                                                         session=session,
                                                         debug=False)

    @classmethod
    async def search_datasets(cls,
                              full_auth=DomoFullAuth,
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
                *[DomoDataset.get_from_id(id=json_obj.get('databaseId'), full_auth=full_auth, debug = debug)
                  for json_obj in json_list]
            )
