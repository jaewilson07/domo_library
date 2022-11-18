import json
from pprint import pprint

import aiohttp
import asyncio
import authlib.client.aiohttp as aioauthlib
import requests


import Library.Trello.TrelloAuth as ta
import Library.utils.Exceptions as ex
from Library.utils.ResponseGetData import ResponseGetData


SESSION_TIMEOUT = 5


async def get_data(
        auth: ta.TrelloAuth,
        base_uri_path: str,
        http_method='GET',
        headers: dict = None,
        query_params=None,
        post_args=None,
        session: aiohttp.ClientSession = None,
        host: str = "https://trello.com/1",
        debug: bool = False,
        log_results: bool = False) -> dict:
    """ Fetch some JSON from Trello """

    is_close_session = True if not session else True
    response = None

    if headers is None:
        headers = {}

        if http_method in ("POST", "PUT", "DELETE"):
            headers.update({'Content-Type': 'application/json'})

        headers = {
            # 'Connection': 'keep-alive',
            'accept': 'application/json, text/plain',
            **headers
        }

    if query_params is None:
        query_params = {}

    for key in query_params.keys():
        if type(query_params[key]) == type(True):
            query_params.update({key: str(query_params[key]).lower()})

    if post_args is None:
        post_args = {}
    data = post_args

    # construct the full URL without query parameters
    if base_uri_path[0] == '/':
        base_uri_path = base_uri_path[1:]
    url = f'{host}/{base_uri_path}'

    if debug:
        print(f"\n🐞 debugging auth 🐞")
        pprint({'auth': auth, 'url': url, 'params': query_params,
               'headers': headers, 'data': data})

    timeout = aiohttp.ClientTimeout(total=SESSION_TIMEOUT)

    try:
        if isinstance(auth, ta.TrelloWebAuth):
            if debug:
                print("🐞 using web auth 🐞")
            query_params['key'] = auth.consumer_key
            query_params['token'] = auth.token

            session = session or aiohttp.ClientSession(timeout=timeout)

            response = await session.request(method=http_method.upper(),
                                             url=url, headers=headers,
                                             json=data,
                                             params=query_params)

        elif isinstance(auth, ta.TrelloOauth):
            print("🐞 using oauth 🐞")
            session = session or aiohttp.ClientSession(
                request_class=aioauthlib.OAuthRequest, timeout=timeout)

            client = aioauthlib.AsyncOAuth1Client(session=session,
                                                  client_id=auth.consumer_key,
                                                  client_secret=auth.consumer_secret,
                                                  token=auth.token,
                                                  token_secret=auth.token_secret)

            response = await getattr(client, http_method.lower())(url=url,

                                                                  headers=headers, data=data,
                                                                  params=query_params)
        else:
            print('invalid creds')
            raise ex.AuthRequiredException(
                message=f"invalid Trello Auth object - {type(auth)}")

        if response.status == 401:
            raise ex.Unauthorized("%s at %s" % (response.text, url), response)

        if response.status != 200:
            print(response)
            print(response.headers)
            raise ex.ResourceUnavailable(
                "%s at %s" % (response.text, url), response)

        if is_close_session and session:
            await session.close()

        return ResponseGetData(status=response.status,
                               response=await response.json() or response.text(),
                               is_success=True if response.status == 200 else False,
                               auth=auth)

    except asyncio.TimeoutError:
        print("🐞 timeout error running backup synchronously 🐞")
        response = requests.request(
            http_method, url, params=query_params, headers=headers, data=data)
        return ResponseGetData(status=response.status_code,
                               response=response.json() or response.text(),
                               is_success=True if response.status_code == 200 else False,
                               auth=auth)

    except Exception as e:
        print("🐞 exception 🐞")
        print(e)

        return ResponseGetData(status=-1,
                               response='error',
                               is_success=False,
                               auth=auth)
