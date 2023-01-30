# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoBootstrap.ipynb.

# %% auto 0
__all__ = ['DomoBootstrap_Feature', 'DomoBootstrap']

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 2
from dataclasses import dataclass, field

import httpx

import domolibrary.classes.DomoPage as dmpg

import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.Logger as lc
import domolibrary.routes.bootstrap as bootstrap_routes


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 3
from fastcore.basics import patch_to



# %% ../../nbs/classes/50_DomoBootstrap.ipynb 4
@dataclass
class DomoBootstrap_Feature:
    id: int
    name: str
    label: str
    type: str
    purchased: bool
    enabled: bool

    @classmethod
    def _from_json_bootstrap(cls, json_obj: dict):
        dd = util_dd.DictDot(json_obj)

        bsf = cls(
            id=dd.id,
            name=dd.name,
            label=dd.label,
            type=dd.type,
            purchased=dd.purchased,
            enabled=dd.enabled
        )
        return bsf

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 5
@dataclass
class DomoBootstrap:
    auth : dmda.DomoAuth = field(repr = False)
    page_ls : list[dmpg.DomoPage] = field(default = None)
    feature_ls : list[DomoBootstrap_Feature] = field(default = None)
    

# %% ../../nbs/classes/50_DomoBootstrap.ipynb 6
@patch_to(DomoBootstrap)
async def get_all(self: DomoBootstrap,
                  auth: dmda.DomoAuth = None, debug_api: bool = False):
    
    auth = auth or self.auth

    res =  await bootstrap_routes.get_bootstrap(auth=auth, debug_api=debug_api)

    return res.response


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 9
@patch_to(DomoBootstrap)
async def get_pages(self: DomoBootstrap,
                    auth: dmda.DomoAuth = None, return_raw : bool = False, debug_api: bool = False) -> list[dmpg.DomoPage]:

    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap_pages(auth=auth,
                                                     debug_api=debug_api)
    
    if return_raw:
        return res.response
        
    if not res.is_success:
        return None
    
    page_ls = res.response

    self.page_ls =  [dmpg.DomoPage._from_bootstrap(page_obj, auth = auth) for page_obj in page_ls]

    return self.page_ls


# %% ../../nbs/classes/50_DomoBootstrap.ipynb 12
@patch_to(DomoBootstrap)
async def get_features(self : DomoBootstrap,
                        auth: dmda.DomoAuth = None,
                        debug_api: bool = False,
                        return_raw:bool = False,
                        session: httpx.AsyncClient = None, 
                        ):
    
    auth = auth or self.auth

    res = await bootstrap_routes.get_bootstrap_features(auth=auth, session=session, debug_api=debug_api)

    if return_raw:
        return res

    feature_list = [DomoBootstrap_Feature._from_json_bootstrap(
        json_obj) for json_obj in res.response]

    return feature_list
