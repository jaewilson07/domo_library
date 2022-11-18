import aiohttp
import Library.Trello.TrelloAuth as ta

from ..get_data import get_data


async def get_card_by_id(auth: ta.TrelloAuth, card_id: str, debug: bool = False, log_results: bool = False) -> dict:
    res = await get_data(auth, base_uri_path=f'/cards/{card_id}', debug=debug, log_results=log_results)
    return res


async def post_new_card(auth: ta.TrelloAuth, card_properties: dict, debug: bool = False, log_results: bool = False,
                        session: aiohttp.ClientSession = None) -> dict:
    if debug:
        print({'route_create_new_card': card_properties})

    res = await get_data(auth,
                         base_uri_path='/cards',
                         http_method='POST',
                         post_args=card_properties,
                         debug=debug,
                         log_results=log_results,
                         session=session)
    return res


async def get_search_cards_by_name(auth: ta.TrelloAuth, search_name: str,
                                   allow_partial_match: bool = False,
                                   debug: bool = False):
    query_parmas = {
        'modelTypes': 'cards',
        'card_fields': 'name',
        'query': search_name,
        'partial': allow_partial_match
    }

    res = await get_data(auth=auth,
                         base_uri_path=f'/search',
                         http_method='GET',
                         query_params=query_parmas,
                         debug=debug)

    if res.status == 200:
        obj_list = res.response.get('cards')

        if not allow_partial_match:
            obj_list = [card for card in obj_list if card.get(
                'name') == search_name]

        res.response = obj_list

        return res

    else:
        return res


async def put_card_attribute(auth: ta.TrelloAuth, card_id, attribute, value, debug: bool = False):
    url = f'/cards/{card_id}/{attribute}'
    post_args = {'value': value}

    if debug:
        print({'debug_put_card_attributes_route': {
              'url': url, 'post_args': post_args}})

    await get_data(
        auth=auth,
        base_uri_path=url,
        http_method='PUT',
        post_args=post_args,
        debug=debug)


async def post_card_attribute(auth: ta.TrelloAuth, card_id, attribute, value, debug: bool = False):
    url = f'/cards/{card_id}/{attribute}'
    post_args = {'value': value}

    if debug:
        print({'debug_put_card_attributes_route': {
              'url': url, 'post_args': post_args}})

    await get_data(
        auth=auth,
        base_uri_path=url,
        http_method='POST',
        post_args=post_args,
        debug=debug)


async def delete_card_attribute(auth: ta.TrelloAuth, card_id, attribute, value, debug: bool = False):
    url = f'/cards/{card_id}/{attribute}/{value}'

    if debug:
        print({'debug_put_card_attributes_route': {'url': url}})

    await get_data(
        auth=auth,
        base_uri_path=url,
        http_method='DELETE',
        debug=debug)


async def delete_card(auth: ta.TrelloAuth, card_id: str,
                      debug: bool = False, log_results: bool = True,
                      session: aiohttp.ClientSession = None):
    url = f'/cards/{card_id}'

    await get_data(
        auth=auth,
        base_uri_path=url,
        http_method='DELETE',
        debug=debug,
        log_results=log_results,
        session=session)
