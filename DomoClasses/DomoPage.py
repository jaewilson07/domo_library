import asyncio
import aiohttp
from dataclasses import dataclass, field

from .routes import page_routes
from .DomoAuth import DomoDeveloperAuth, DomoFullAuth
from ..utils.DictDot import DictDot
from ..utils.Base import Base


@dataclass
class DomoPage(Base):
    id: str
    title: str = None
    parent_page_id: str = None
    domo_instance: str = None
    full_auth: DomoFullAuth = None
    owners: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    collections: list = field(default_factory=list)

    def __post_init__(self, full_auth=None):
        Base().__init__()

        if full_auth:
            self.domo_instance = full_auth.domo_instance
            self.full_auth = full_auth
        # self.Definition = CardDefinition(self)

    def display_url(self):
        return f'https://{self.domo_instance}.domo.com/page/{self.id}'

    @classmethod
    async def get_from_id(cls, page_id: str, full_auth: DomoFullAuth, debug: bool = False):
        import Library.DomoClasses.DomoCard as dc
        res = await page_routes.get_page_by_id(full_auth=full_auth, page_id=page_id, debug=debug)

        if res.status == 200:
            dd = DictDot(res.response)

            pg = cls(
                id=dd.id,
                domo_instance=full_auth.domo_instance,
                title=dd.title,
                parent_page_id=dd.page.parentPageId,
                owners=dd.page.owners,
                collections=dd.collections
            )

            pg.cards = await asyncio.gather(
                *[dc.DomoCard.get_from_id(id=card.id, full_auth=full_auth) for card in dd.cards])

            return pg

    @classmethod
    async def get_cards(cls, full_auth, page_id, debug: bool = False, session: aiohttp.ClientSession = None):
        try:
            import Library.DomoClasses.DomoCard as dc
            close_session = False if session else True

            if not session:
                session = aiohttp.ClientSession()

            res = await page_routes.get_page_definition(full_auth=full_auth, page_id=page_id, debug=debug, session=session)

            if res.status == 200:
                json = res.response

                card_list = [dc.DomoCard(id=card.get(
                    'id'), full_auth=full_auth) for card in json.get('cards')]

                return card_list

            else:
                return None

        finally:
            if close_session:
                await session.close()

    async def get_datasets(full_auth, page_id, debug: bool = False, session: aiohttp.ClientSession = None):
        try:
            import Library.DomoClasses.DomoDataset as dmds
            close_session = False if session else True

            if not session:
                session = aiohttp.ClientSession()

            res = await page_routes.get_page_definition(full_auth=full_auth, page_id=page_id, debug=debug, session=session)

            if res.status == 200:
                json = res.response

                dataset_ls = [card.get('datasources')
                              for card in json.get('cards')]

                return [dmds.DomoDataset(id=ds.get('dataSourceId'), full_auth=full_auth) for ds_ls in dataset_ls for ds in ds_ls]

            else:
                return None

        finally:
            if close_session:
                await session.close()
