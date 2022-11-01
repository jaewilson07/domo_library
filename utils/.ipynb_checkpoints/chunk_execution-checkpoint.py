from typing import Any, Awaitable


async def run_sequence(*functions: Awaitable[Any]) -> None:
    for function in functions:
        await function


def chunk_list(tlist, chunk_size):
    chunked_list = [tlist[i * chunk_size:(i + 1) * chunk_size] for i in
                    range((len(tlist) + chunk_size - 1) // chunk_size)]
    return chunked_list


async def chunk_fn(chunk, api_fun, idx, sleep_time, session, list_id):
    print(f'sleeping {idx} and {len(chunk)}')

    res = await asyncio.gather(*[api_fun(row=row, session=session, list_id=list_id) for row in chunk])

    await asyncio.sleep(sleep_time)
    print(f'end_sleep {idx}')
    return res


async def api_request_in_chunks(full_list, api_fn, api_limit_size, list_id, sleep_time=10):
    chunked_list = chunk_list(tlist=full_list, chunk_size=api_limit_size)
    session = aiohttp.ClientSession(request_class=OAuthRequest)
    res = await run_sequence(
        *[chunk_fn(chunk, api_fn, idx, sleep_time=sleep_time, session=session, list_id=list_id) for idx, chunk in
          enumerate(chunked_list)])
    await session.close()
    return res
