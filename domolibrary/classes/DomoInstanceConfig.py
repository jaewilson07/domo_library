# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoInstanceConfig.ipynb.

# %% auto 0
__all__ = ['DomoInstanceConfig']

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 3
import httpx
import datetime as dt
import asyncio
from fastcore.basics import patch_to


from dataclasses import dataclass, field
from typing import List

import domolibrary.client.DomoAuth as dmda
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoError as de
import domolibrary.routes.instance_config as instance_config_routes
import domolibrary.routes.grant as grant_routes
import domolibrary.classes.DomoGrant as dmdg
import domolibrary.classes.DomoRole as dmr
import domolibrary.routes.role as role_routes

# import Library.utils.convert as cd
# from .DomoAuth import DomoAuth
# from .DomoApplication import DomoApplication
# import Library.DomoClasses.DomoPublish as dmpb


# import domolibrary.utils.convert as cd
# import domolibrary.utils.DictDot as util_dd
# import domolibrary.client.DomoError as de


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 4
@dataclass
class DomoInstanceConfig:
    """utility class that absorbs many of the domo instance configuration methods"""
    
    auth: dmda.DomoAuth
    allowlist : list[str] = field(default_factory = list)

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 5
@patch_to(DomoInstanceConfig)
async def get_allowlist(self: DomoInstanceConfig, 
                        auth: dmda.DomoFullAuth = None, # get_allowlist requires full authentication
                        session: httpx.AsyncClient = None, 
                        return_raw : bool = False,
                        debug_api: bool = False) -> list[str]:
    """retrieves the allowlist for an instance"""

    auth = auth or self.auth

    res =  await instance_config_routes.get_allowlist(auth=auth,  debug_api=debug_api, session = session)

    if return_raw:
        return res

    if not res.is_success:
        return None

    allowlist = res.response.get('addresses')

    self.allowlist = allowlist

    return allowlist


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 9
@patch_to(DomoInstanceConfig)
async def set_allowlist(self : DomoInstanceConfig,
                        ip_address_ls: list[str],
                        debug_api: bool = False,
                        auth: dmda.DomoFullAuth = None,
                        session: httpx.AsyncClient = None
                        ):
                        
    auth = auth or self.auth

    await instance_config_routes.set_allowlist(auth=auth,
                                               ip_address_ls=ip_address_ls,
                                               debug_api=debug_api, session=session)

    return await self.get_allowlist(auth=auth, debug_api=debug_api, session=session)


@patch_to(DomoInstanceConfig, )
async def upsert_allowlist(self : DomoInstanceConfig,
                           ip_address_ls: list[str],
                           debug_api: bool = False,
                           session: httpx.AsyncClient = None,
                           auth: dmda.DomoAuth = None,
                           ):

    exist_ip_address_ls = await self.get_allowlist(auth=auth, debug_api=debug_api, session=session)
    ip_address_ls += exist_ip_address_ls

    return await self.set_allowlist(auth=auth,
                                   ip_address_ls=list(set(ip_address_ls)),
                                   debug_api=debug_api, session=session)


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 13
@patch_to(DomoInstanceConfig)
async def get_grants(self: DomoInstanceConfig,
                     auth: dmda.DomoAuth = None,
                     debug_prn:bool = False,
                     debug_api: bool = False,
                     session: httpx.AsyncClient = None,
                     return_raw: bool = False):

    auth = auth or self.auth

    res = await grant_routes.get_grants(auth=auth,
                                        debug_api=debug_api,
                                        session=session)

    if debug_prn:
        print(
            f"ℹ️ - get_instance_grants: {len(res.response)} grants returned from {auth.domo_instance}")
    


    if return_raw:
        return res

    if res.status == 200:
        json_list = res.response
        return [dmdg.DomoGrant._from_json(obj) for obj in json_list]


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 16
@patch_to(DomoInstanceConfig)
async def get_roles(self, auth: dmda.DomoAuth = None,
                    debug_api: bool = False,
                    return_raw: bool = False,
                    session: httpx.AsyncClient = None):

    auth = auth or self.auth

    res = await role_routes.get_roles(auth=auth,
                                      debug_api=debug_api, session = session)
    
    if return_raw:
        return res

    if res.status == 200:
        json_list = res.response
        return [dmr.DomoRole._from_json(obj = obj, auth = auth
                                   ) for obj in json_list]

