from dataclasses import dataclass
from typing import List

from ..utils.DictDot import DictDot
from ..utils.Base import Base

import Library.Trello.TrelloAuth as ta
import Library.Trello.TrelloList as tl
import Library.Trello.TrelloCard as tc

from .routes import board_routes


class GetBoardCards:
    def __init__(self, auth: ta.TrelloAuth, board):
        self._auth = auth
        self._board = board

        self.cards: List[TrelloCard] = None

    async def _process_board_card(self, card_filter: str,
                                  auth: ta.TrelloAuth,
                                  debug: bool = False,
                                  log_results: bool = False):
        self.cards = []

        res = await board_routes.get_board_cards(auth=auth,
                                                 board_id=self._board.id,
                                                 card_filter=card_filter,
                                                 debug=debug)

        if res.status == 200:
            json_list = res.response

            if len(json_list) > 0:

                for index, json_obj in enumerate(json_list):
                    tcard = tc.TrelloCard._create_from_json(
                        auth=self._auth, json_obj=json_obj)

                    self.cards.append(tcard)
                return self.cards

    async def all(self, debug: bool = False, auth: ta.TrelloOauth = None):
        auth = auth or self._auth

        return await self._process_board_card(card_filter='all', auth=auth, debug=debug)


class GetBoardLists:
    def __init__(self, auth: ta.TrelloAuth, board):
        self._auth = auth
        self._board = board

        self.lists: List[TrelloList] = None

    async def _process_board_list(self, list_filter: str,
                                  auth: ta.TrelloAuth,
                                  debug: bool = False,
                                  log_results: bool = False):
        self.lists = []
        res = await board_routes.get_board_lists(auth=auth, board_id=self._board.id, list_filter=list_filter, debug=debug)

        if res.status == 200:
            json_obj = res.response

            for obj in json_obj:
                tlist = tl.TrelloList._create_list_from_board(
                    auth=self._auth, json_obj=obj)
                self.lists.append(tlist)

            return self.lists

    async def open(self, debug: bool = False, log_results: bool = False):
        return await self._process_board_list(list_filter='open', debug=debug)

    async def closed(self, debug: bool = False, log_results: bool = False):
        return await self._process_board_list(list_filter='closed',
                                              debug=debug)

    async def all(self, debug: bool = False, auth: ta.TrelloOauth = None):
        auth = auth or self._auth
        return await self._process_board_list(list_filter='all', auth=auth, debug=debug)


@dataclass
class TrelloLabel:
    id: str
    name: str

    @classmethod
    def _create_from_json(cls, json_obj):
        dd = DictDot(json_obj)

        return cls(id=dd.id,
                   name=dd.name)


@dataclass
class TrelloBoard(Base):

    id: str
    auth: ta.TrelloAuth = None
    name: str = None
    url: str = None
    description: str = None
    closed: bool = None
    labels: list = None

    def __post_init__(self):
        self.get_lists = GetBoardLists(auth=self.auth, board=self)
        self.get_cards = GetBoardCards(auth=self.auth, board=self)

    @classmethod
    def create_from_board_json(cls, auth: ta.TrelloAuth, json_obj: dict):
        dd = DictDot(json_obj)

        board = cls(id=dd.id,
                    auth=auth,
                    name=dd.name,
                    description=dd.desc or None,
                    url=dd.url or None,
                    closed=dd.closed or None)

        return board

    async def create_label(self, label_color, label_name, auth=None):

        res = await board_routes.create_label(label_color, label_name,
                                              auth=auth or self.auth,
                                              board_id=self.id)
        return res

    async def get_labels(self, auth=None, debug: bool = False):
        res = await board_routes.get_board_labels(auth=auth or self.auth,
                                                  board_id=self.id, debug=debug)

        if res.status == 200:
            json_list = res.response
            self.labels = []

            for json_obj in json_list:
                tlabel = TrelloLabel._create_from_json(json_obj=json_obj)
                self.labels.append(tlabel)
            return(self.labels)

    async def get_props(self, board_id: str = None, auth: ta.TrelloAuth = None, debug: bool = False):
        """Fetch all attributes for this board"""

        auth = auth or self.auth

        board_id = board_id or self.id
        res = await board_routes.get_board_by_id(auth=auth, board_id=board_id, debug=debug)

        if res.status == 200:
            json_obj = res.response

            self.id = json_obj['id']
            self.name = json_obj['name']
            self.description = json_obj.get('desc', '')
            self.closed = json_obj.get('closed')
            self.url = json_obj.get('url')

            return json_obj
