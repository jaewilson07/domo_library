import aiohttp

import Library.DomoClasses.DomoAuth as dmda
import Library.utils.ResponseGetData as rgd

from Library.DomoClasses.routes.get_data import get_data

async def search_publications(full_auth : dmda.DomoFullAuth , search_term: str = None, limit = 100, offset =0, session :aiohttp.ClientSession = None, debug:bool = False) -> rgd.ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication/summaries"
    
    params ={ 'limit': limit, 'offset' : offset}
        
    if search_term:
        params.update({'searchTerm' : search_term})
        
    res = await get_data(auth=full_auth,
                         method='GET',
                         url=url,
                         params=params,
                         session=session,
                         debug=debug)
    
    return res
        

async def get_publication_by_id(full_auth : dmda.DomoFullAuth , publication_id : str, session :aiohttp.ClientSession = None, debug:bool = False) -> rgd.ResponseGetData:
    url = f"https://{full_auth.domo_instance}.domo.com/api/publish/v2/publication/{publication_id}"
    
    res = await get_data(auth=full_auth,
                         method='GET',
                         url=url,
                         session=session,
                         debug=debug)
    
    return res