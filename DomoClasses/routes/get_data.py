import aiohttp
from pprint import pprint

from ..DomoAuth import DomoAuth
from ...utils.ResponseGetData import ResponseGetData

from ast import literal_eval


async def get_data(url, method, auth: DomoAuth,
                   content_type=None,
                   headers=None,
                   session: aiohttp.ClientSession = None,
                   body=None,
                   params: dict = None,
                   log_results=False, debug=False) -> ResponseGetData:
    from pprint import pprint
    import aiohttp

    if auth and not auth.token:
        await auth.get_auth_token()

    if headers is None:
        headers = {}

    is_close_session = False
    if session is None:
        is_close_session = True
        session = session or aiohttp.ClientSession()

    headers = {
        'Content-Type': content_type or 'application/json',
        'Connection': 'keep-alive',
        'accept': 'application/json, text/plain',
        **headers
    }

    if auth:
        headers.update(**auth.auth_header)

    if debug:
        pprint({'method': method,
                'url': url,
                'headers': headers,
                'json': body,
                'params': params})

    # if params:
    #     params = {k: literal_eval(v) for k, v in params.items()}
    #     print(params)

    if headers.get('Content-Type') == 'application/json':
        if debug:
            print('passing json')

        res = await session.request(method=method.upper(),
                                    url=url, headers=headers,
                                    json=body,
                                    params=params)
        
    elif body is not None:
        res = await session.request(method=method.upper(),
                                    url=url,
                                    headers=headers,
                                    data=body,
                                    params=params)

    else:
        res = await session.request(method=method.upper(),
                                    url=url,
                                    headers=headers,
                                    params=params)

    if is_close_session:
        await session.close()

    if log_results:
        try:
            pprint({'url': url, 'text': await res.json()})
        except:
            pprint({'url': url, 'text': await res.text()})

    if res.status == 200 \
            and hasattr(res, 'headers') \
            and res.headers.get('Content-Type') \
            and 'application/json' in res.headers.get('Content-Type'):

        if debug:
            print('return json')

        try:
            response = await res.json()

            # if debug:
            #     print({'get_data_json_response': response})

            return ResponseGetData(status=res.status,
                                   response=response,
                                   is_success=True,
                                   auth=auth)
        except:
            if debug:
                print('SUCCESS - however. Expected JSON but received read io')
            response = await res.read()
            return ResponseGetData(status=res.status,
                                   response=response.decode(),
                                   is_success=True,
                                   auth=auth)
            raise Exception

    elif res.status == 200:
        if debug:
            print('return text')
        return ResponseGetData(res.status, await res.text(), is_success=True, auth=auth)

    else:
        return ResponseGetData(res.status, response={'success': False, 'reason': res.reason}, is_success=False,
                               auth=auth)


async def looper(auth: DomoAuth,
                 session: aiohttp.ClientSession,
                 url,
                 offset_params,
                 arr_fn: callable,
                 alter_maximum_fn: callable = None,
                 loop_until_end: bool = False,
                 method='POST',
                 body: dict = None,
                 fixed_params: dict = None,
                 offset_params_in_body: bool = False,
                 body_fn=None,
                 limit=1000,
                 maximum=2000,
                 debug: bool = False):
    allRows = []
    skip = 0
    isLoop = True

    while isLoop:
        params = fixed_params or {}

        if offset_params_in_body:
            body[offset_params.get('offset')] = skip
            body[offset_params.get('limit')] = limit

        else:
            params[offset_params.get('offset')] = skip
            params[offset_params.get('limit')] = limit

        if body_fn:
            body = body_fn(skip,
                           limit)

        if debug:
            pprint(params)
            print(
                f'Retrieving records {skip} through {skip + limit} via {url}')

        res = await get_data(auth=auth,
                             url=url,
                             method=method,
                             params=params,
                             session=session,
                             body=body,
                             debug=debug)

        newRecords = arr_fn(res)
        # print('loop', newRecords)
        # process rows
        allRows += newRecords

        if skip == 0 and alter_maximum_fn:
            maximum = alter_maximum_fn(res)
            #print(f'the new maximum is: {maximum}')

        if loop_until_end and len(newRecords) != 0:
            maximum = maximum + limit

        if debug:
            print(len(allRows), len(newRecords))

        if maximum <= len(allRows) or len(newRecords) < limit:
            if debug:
                print(
                    f'{len(allRows)} records retrieved from {url} in query looper\n')
            isLoop = False

        skip += limit

    return allRows
