import aiohttp

from .get_data import get_data
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


async def create_document(full_auth: DomoFullAuth, app_id: str,
                          domo_environment: str,
                          collection_name: str,
                          document: dict,
                          session: aiohttp.ClientSession = None,
                          debug: bool = False):
    url = f'https://{app_id}.domoapps.{domo_environment}.domo.com/domo/datastores/v1/collections/{collection_name}/documents'

    if debug:
        print(url)

    res = await get_data(auth=full_auth,
                         method='POST',
                         url=url,
                         body=document,
                         session=session,
                         debug=debug)
    return res


async def get_documents(full_auth: DomoFullAuth, app_id: str,
                        domo_environment: str,
                        collection_name: str):
    url = f'https://{app_id}.domoapps.{domo_environment}.domo.com/domo/datastores/v1/collections/{collection_name}/documents/'

    res = await get_data(auth=full_auth,
                         method='GET',
                         url=url)
    return res
