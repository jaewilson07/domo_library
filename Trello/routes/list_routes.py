import Library.Trello.TrelloAuth as ta

from ..get_data import get_data


async def get_list_by_id(auth: ta.TrelloAuth, list_id, debug: bool = False) -> dict:
    res = await get_data(auth=auth, base_uri_path=f'/lists/{list_id}', debug=debug)
    return res
