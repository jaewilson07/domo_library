from dataclasses import dataclass
from typing import List

from ..utils.DictDot import DictDot
from ..utils.Base import Base

import Library.Trello.TrelloAuth as ta

from .routes import list_routes


@dataclass
class TrelloList(Base):
    auth: ta.TrelloAuth
    id: str
    board_id: str = None
    name: str = None
    pos: int = None
    url: str = None
    closed: bool = None
    subscribed: bool = None

    def __post_init__(self):
        # self.cards = GetListCards(auth=self.auth, tlist=self)
        pass

    @classmethod
    def _create_list_from_board(cls, auth: ta.TrelloAuth, json_obj: dict):
        dd = DictDot(json_obj)
        tlist = cls(id=dd.id or None,
                    board_id=dd.idBoard or None,
                    auth=auth,
                    name=dd.name or None,
                    url=dd.url or None)
        return tlist

    async def get_props(self, list_id: str = None, auth: ta.TrelloAuth = None, debug: bool = False):
        """Fetch all attributes for this list"""

        auth = auth or self.auth

        list_id = list_id or self.id

        res = await list_routes.get_list_by_id(auth=auth, list_id=list_id, debug=debug)

        if res.status == 200:
            json_obj = res.response

            self.id = json_obj['id']
            self.name = json_obj['name']
            self.closed = json_obj['closed']
            self.board_id = json_obj['idBoard']
            self.pos = json_obj['pos']
            self.subscribed = json_obj.get('subscribed', False)

            return json_obj
