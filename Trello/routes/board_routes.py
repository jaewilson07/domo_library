import Library.Trello.TrelloAuth as ta
from ..get_data import get_data


async def get_board_by_id(auth: ta.TrelloAuth, board_id, debug: bool = False) -> dict:
    res = await get_data(auth=auth,
                         http_method='get',
                         base_uri_path=f'/boards/{board_id}',
                         debug=debug)

    return res


async def get_board_labels(auth: ta.TrelloAuth,
                           board_id: str, debug: bool = False) -> dict:

    json_obj = await get_data(auth=auth,
                              base_uri_path=f'/boards/{board_id}/labels',
                              debug=debug)
    return json_obj


async def create_label(label_color, label_name,
                       auth,
                       board_id, debug: bool = False):

    body = {
        'name': label_name,
        'color': label_color
    }

    res = await get_data(auth=auth,
                         http_method='post',
                         post_args=body,
                         base_uri_path=f'/boards/{board_id}/labels',
                         debug=debug)
    return res


async def get_board_lists(auth: ta.TrelloAuth, board_id: str, list_filter: str, debug: bool = False) -> dict:
    json_obj = await get_data(auth=auth,
                              base_uri_path=f'/boards/{board_id}/lists',
                              query_params={'cards': 'none',
                                            'filter': list_filter},
                              debug=debug)
    return json_obj


async def get_board_cards(auth: ta.TrelloAuth,
                          board_id: str, card_filter: str,
                          debug: bool = False) -> dict:
    res = await get_data(auth=auth,
                         base_uri_path=f'/boards/{board_id}/cards',
                         query_params={'cards': 'none', 'filter': card_filter},
                         debug=debug)
    return res
