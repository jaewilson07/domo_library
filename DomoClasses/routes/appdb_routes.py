import aiohttp

from ...DomoClasses import DomoAuth as dmda
from ...utils.ResponseGetData import ResponseGetData
from . import get_data as gd


async def create_document(full_auth: dmda.DomoFullAuth, app_id: str,
                          domo_environment: str,
                          collection_name: str,
                          document: dict,
                          session: aiohttp.ClientSession = None,
                          debug: bool = False):
    url = f'https://{app_id}.domoapps.{domo_environment}.domo.com/domo/datastores/v1/collections/{collection_name}/documents'

    if debug:
        print(url)

    res = await gd.get_data(auth=full_auth,
                            method='POST',
                            url=url,
                            body=document,
                            session=session,
                            debug=debug)
    return res


async def get_documents(full_auth: dmda.DomoFullAuth, app_id: str,
                        domo_environment: str,
                        collection_name: str):
    url = f'https://{app_id}.domoapps.{domo_environment}.domo.com/domo/datastores/v1/collections/{collection_name}/documents/'

    res = await gd.get_data(auth=full_auth,
                            method='GET',
                            url=url)
    return res
