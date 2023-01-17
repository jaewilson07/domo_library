import aiohttp
from dataclasses import dataclass

from .DomoAuth import DomoFullAuth
from .DomoDataset import DomoDataset
from .routes import bootstrap_routes
from ..utils.DictDot import DictDot


@dataclass
class DomoBootstrapFeature:
    id: int
    name: str
    label: str
    type: str
    purchased: bool
    enabled: bool

    @classmethod
    def create_from_json_bootstrap(cls, json_obj: dict):
        dd = DictDot(json_obj)

        bsf = cls(
            id=dd.id,
            name=dd.name,
            label=dd.label,
            type=dd.type,
            purchased=dd.purchased,
            enabled=dd.enabled
        )
        return bsf


class DomoBootstrap:

    @classmethod
    async def get_all(cls, full_auth: DomoFullAuth, debug: bool = False):
        return await bootstrap_routes.bsr_all(full_auth=full_auth, debug=debug)

    @classmethod
    async def get_pages(cls, full_auth: DomoFullAuth, debug: bool = False):
        return await bootstrap_routes.bsr_pages(full_auth=full_auth, debug=debug)

    @classmethod
    async def get_features(cls, full_auth: DomoFullAuth,
                           session: aiohttp.ClientSession = None, debug: bool = False):
        is_close_session= False
        if not session:
            session = aiohttp.ClientSession()
            is_close_session= True
            
        json_list = await bootstrap_routes.bsr_features(full_auth=full_auth, session=session, debug=debug)

        if is_close_session:
            await session.close()
            
        feature_list = [DomoBootstrapFeature.create_from_json_bootstrap(
            json_obj) for json_obj in json_list]
        
        return feature_list
