from dataclasses import dataclass, field
from typing import List, Union
import aiohttp

from ..utils.DictDot import DictDot
from ..utils.Base import Base

import Library.Trello.TrelloAuth as ta
from Library.Trello.get_data import get_data
import datetime as dt

import Library.Trello.TrelloUtils as tu

from .routes import card_routes


class UpdateCard:
    def __init__(self, card, auth: ta.TrelloAuth):
        self._card = card
        self._auth = auth

    async def name(self, new_value, auth,  debug: bool = False):
        await card_routes.put_card_attribute(auth=auth or self._auth, card_id=self._card.id,
                                             attribute='name', value=new_value, debug=debug)

    async def description(self, new_value, auth,  debug: bool = False):
        await card_routes.put_card_attribute(auth=auth or self._auth, card_id=self._card.id,
                                             attribute='desc', value=new_value, debug=debug)

    async def start_date(self, new_value, auth, debug: bool = False):
        await card_routes.put_card_attribute(auth=auth or self._auth, card_id=self._card.id,
                                             attribute='start', value=new_value, debug=debug)

    async def add_label(self, new_value, auth, debug: bool = False):
        await card_routes.post_card_attribute(auth=auth or self._auth, card_id=self._card.id,
                                              attribute='idLabels', value=new_value, debug=debug)

    async def remove_label(self, new_value, auth, debug: bool = False):
        await card_routes.delete_card_attribute(auth=auth or self._auth, card_id=self._card.id,
                                                attribute='idLabels', value=new_value, debug=debug)


@dataclass
class TrelloCard(Base):
    id: str
    auth: ta.TrelloAuth = None

    name: str = None
    list_id: str = None
    board_id: str = None

    description: str = None
    start_date: dt.datetime = None
    label_ids: list = None
    labels: list = None

    url: str = None

    members_ids: List[str] = field(default_factory=list)

    closed: bool = None

    pos: Union[str, int] = None

    def __post_init__(self):
        self.update = UpdateCard(self, auth=self.auth)

    async def get_props(self, card_id: str = None, debug: bool = False):
        card_id = card_id or self.id

        if debug:
            print(f"debug -- getting props for {card_id}")

        res = await card_routes.get_card_by_id(auth=self.auth, card_id=card_id, debug=debug)

        if res.status == 200:
            json_obj = res.response

            dd = DictDot(json_obj)

            self.id = dd.id
            self.name = dd.name
            self.url = dd.url
            self.members_ids = dd.idMembers
            self.description = dd.desc
            self.closed = dd.closed
            self.board_id = dd.idBoard
            self.label_ids = dd.idLabels
            self.labels = dd.labels
            self.list_id = dd.idList
            self.pos = dd.pos
            self.start_date = tu.trello_timestr_to_datetime(dd.start)

        return res

    @classmethod
    def _create_from_json(cls, auth: ta.TrelloAuth, json_obj: dict):
        dd = DictDot(json_obj)

        card = cls(id=dd.id, auth=auth,
                   name=dd.name,
                   url=dd.url,
                   members_ids=dd.idMembers,
                   description=dd.desc,
                   closed=dd.closed,
                   board_id=dd.idBoard,
                   list_id=dd.idList,
                   pos=dd.pos,
                   start_date=tu.trello_timestr_to_datetime(
                       dd.start) if dd.start else None,
                   label_ids=dd.idLabels,
                   labels=dd.labels
                   )

        return card

    @classmethod
    async def _create_card(cls, auth: ta.TrelloAuth,
                           name: str,
                           list_id: str,
                           board_id: str,
                           description: str = '',
                           members_ids: list[str] = None,
                           closed: bool = False,
                           pos: str = 'top',
                           debug: bool = False, log_results: bool = False,
                           start_date: str = None,
                           session: aiohttp.ClientSession = None):

        card_properties = {
            'name': name,
            'idList': list_id,
            'idBoard': board_id,
            'closed': closed,
            'pos': pos
        }

        if start_date:
            card_properties.update({'start': start_date})

        if description:
            card_properties.update({'desc': description})

        if members_ids:
            card_properties.update({'idMembers': members_ids})

        res = await card_routes.post_new_card(auth=auth, card_properties=card_properties, debug=debug,
                                              session=session)

        if res.status == 200:
            return cls._create_from_json(auth=auth, json_obj=res.response)

    @classmethod
    async def _upsert_card(cls, auth: ta.TrelloAuth,
                           name: str,
                           list_id: str,
                           board_id: str,
                           description: str = None,
                           members_ids: list[str] = None,
                           closed: bool = False,
                           pos: str = 'top',
                           debug: bool = False, session: aiohttp.ClientSession = None):

        res = await card_routes.get_search_cards_by_name(auth, search_name=name, allow_partial_match=False,
                                                         debug=debug)

        if res.status == 200:
            search_cards = res.response

            match_card = next((card for card in search_cards if card.get(
                'name') == name), None) if len(search_cards) > 0 else None

            if match_card:
                if debug:
                    print({'log_create_card': {'match_card': match_card}})

                match_card = DictDot(match_card)
                update_card = cls(auth=auth, id=match_card.id, name=match_card.name,
                                  list_id=match_card.idList,
                                  board_id=match_card.idBoard)

                if description:
                    print('updating description')
                await update_card.update.description(description, debug=debug)
                # if members_ids:
                #     update_card.update.member_ids(members_ids)

                await update_card.get_props()
                return update_card

            return await cls._create_card(auth=auth,
                                          name=name,
                                          description=description,
                                          list_id=list_id,
                                          board_id=board_id, debug=debug)

    @classmethod
    async def create_card(cls,
                          auth: ta.TrelloAuth,
                          name: str,
                          list_id: str,
                          board_id: str,
                          check_duplicates: bool = True,
                          description: str = None,
                          members_ids: list[str] = None,
                          closed: bool = False,
                          pos: str = 'top',
                          start_date: str = None,
                          debug: bool = False, session: aiohttp.ClientSession = None):

        if check_duplicates:
            return await cls._upsert_card(auth=auth,
                                          name=name,
                                          list_id=list_id,
                                          board_id=board_id,
                                          description=description,
                                          members_ids=members_ids,
                                          closed=closed,
                                          pos=pos,
                                          debug=debug, session=session)

        return await cls._create_card(auth=auth,
                                      name=name,
                                      list_id=list_id,
                                      board_id=board_id,
                                      description=description,
                                      members_ids=members_ids,
                                      closed=closed,
                                      pos=pos,
                                      debug=debug,
                                      start_date=start_date,
                                      session=session)

    async def delete_card(self, debug: bool = False, session: aiohttp.ClientSession = None):
        return await card_routes.delete_card(auth=self.auth, card_id=self.id, debug=debug, session=session)
