import aiohttp

from ...utils.ResponseGetData import ResponseGetData


async def get_full_auth(domo_instance, domo_username, domo_password, session=None) -> ResponseGetData:
    is_close_session = False

    if not session:
        is_close_session = True
        session = aiohttp.ClientSession()

    url = f'https://{domo_instance}.domo.com/api/content/v2/authentication'

    tokenHeaders = {'Content-Type': 'application/json'}
    body = {'method': 'password', 'emailAddress': domo_username,
            'password': domo_password}

    res = await session.request(method='POST', url=url, headers=tokenHeaders, json=body)

    data = await res.json()

    if is_close_session:
        await session.close()

    if res.status == 200 and data.get('sessionToken'):
        return ResponseGetData(status=res.status,
                               is_success=True,
                               response=data)

    if not data.get('sessionToken'):
        return ResponseGetData(status=res.status,
                               is_success=False,
                               response=data)

    return gdr


async def get_developer_auth(domo_client_id, domo_client_secret, session=None) -> ResponseGetData:
    if not session:
        session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(domo_client_id, domo_client_secret))

    url = f'https://api.domo.com/oauth/token?grant_type=client_credentials'

    res = await session.request(method='GET', url=url)
    data = await res.json()

    gdr = ResponseGetData(status=res.status,
                          is_success=True if res.status == 200 else False,
                          response=data)

    await session.close()
    return gdr
