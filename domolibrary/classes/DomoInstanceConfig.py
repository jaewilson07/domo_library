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
import domolibrary.client.DomoError as de

import domolibrary.routes.instance_config as instance_config_routes
import domolibrary.routes.bootstrap as bootstrap_routes
import domolibrary.routes.publish as publish_routes

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 4
@dataclass
class DomoInstanceConfig:
    """utility class that absorbs many of the domo instance configuration methods"""

    auth: dmda.DomoAuth
    allowlist: list[str] = field(default_factory=list)
    is_user_invite_notification_enabled : bool = field(default = None)
    is_invite_social_users_enabled: bool = field(default = None)

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 6
@patch_to(DomoInstanceConfig)
async def get_is_user_invite_notification_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False):
    
    """
    Admin > Company Settings > Admin Notifications
    Toggles whether user recieves 'You've been Domo'ed email
    """

    res = await instance_config_routes.get_is_user_invite_notifications_enabled(
        auth=auth or self.auth,
        session=session,
        debug_api=debug_api,
    )

    self.is_user_invite_notification_enabled = bool(res.response["value"])

    if return_raw:
        return res


    return self.is_user_invite_notification_enabled

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 9
@patch_to(DomoInstanceConfig)
async def toggle_is_user_invite_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth,
    is_enabled: bool,
    debug_api: bool = False,
    debug_prn: bool = True,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    is_user_invite_notification_enabled = await self.get_is_user_invite_notification_enabled(auth=auth)

    if is_enabled == is_user_invite_notification_enabled:
        if debug_prn:
            print(f"User invite notification is already {'enabled' if is_enabled else 'disabled'} in {auth.domo_instance}")
        return True
    
    if debug_prn:
        print(f"{'enabling' if is_enabled else 'disabling'} User invite notification {auth.domo_instance}")

    res = await instance_config_routes.toggle_is_user_invite_enabled(
        auth=auth or self.auth,
        is_enabled=is_enabled,
        session=session,
        debug_api=debug_api
    )

    if return_raw:
        return res

    return await self.get_is_user_invite_notification_enabled(auth=auth)


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 13
@patch_to(DomoInstanceConfig)
async def get_is_invite_social_users_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False):
    
    import domolibrary.classes.DomoBootstrap as dmbp

    bs = dmbp.DomoBootstrap( auth = auth)
    customer_id = await bs.get_customer_id()
    
    res = await instance_config_routes.get_is_invite_social_users_enabled(
        auth=auth or self.auth,
        customer_id=customer_id,
        session=session,
        debug_api=debug_api,
    )

    self.is_invite_social_users_enabled = bool(res.response["enabled"])

    if return_raw:
        return res

    return res.response["enabled"]


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 16
@patch_to(DomoInstanceConfig)
async def toggle_social_users(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth,
    is_enabled: bool,
    debug_api: bool = False,
    debug_prn: bool = True,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    is_invite_social_users_enabled = await self.get_is_invite_social_users_enabled(
        auth=auth)

    if is_enabled == is_invite_social_users_enabled:
        if debug_prn:
            print(f"invite social users is already {'enabled' if is_enabled else 'disabled'} in {auth.domo_instance}")
        return True
    
    if debug_prn:
        print(f"{'enabling' if is_enabled else 'disabling'} invite social users {auth.domo_instance}")

    res = await instance_config_routes.toggle_social_users(
        auth=auth or self.auth,
        is_enabled=is_enabled,
        session=session,
        debug_api=debug_api
    )

    if return_raw:
        return res

    return await self.get_is_invite_social_users_enabled()


# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 24
@patch_to(DomoInstanceConfig)
async def get_allowlist(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth = None,  # get_allowlist requires full authentication
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_api: bool = False,
) -> list[str]:
    """retrieves the allowlist for an instance"""

    auth = auth or self.auth

    res = None
    loop = 0

    while not res and loop <= 5:
        try:
            res = await instance_config_routes.get_allowlist(
                auth=auth, debug_api=debug_api, session=session
            )
        except Exception as e:
            print(e)
        finally:
            loop += 1

    if return_raw:
        return res

    if not res.is_success:
        return None

    allowlist = res.response.get("addresses")

    self.allowlist = allowlist

    return allowlist

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 28
@patch_to(DomoInstanceConfig)
async def set_allowlist(
    self: DomoInstanceConfig,
    ip_address_ls: list[str],
    debug_api: bool = False,
    auth: dmda.DomoFullAuth = None,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    await instance_config_routes.set_allowlist(
        auth=auth, ip_address_ls=ip_address_ls, debug_api=debug_api, session=session
    )

    return await self.get_allowlist(auth=auth, debug_api=debug_api, session=session)


@patch_to(
    DomoInstanceConfig,
)
async def upsert_allowlist(
    self: DomoInstanceConfig,
    ip_address_ls: list[str],
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    auth: dmda.DomoAuth = None,
):
    exist_ip_address_ls = await self.get_allowlist(
        auth=auth, debug_api=debug_api, session=session
    )
    ip_address_ls += exist_ip_address_ls

    return await self.set_allowlist(
        auth=auth,
        ip_address_ls=list(set(ip_address_ls)),
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 33
@patch_to(DomoInstanceConfig)
async def get_grants(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth = None,
    debug_prn: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    import domolibrary.classes.DomoGrant as dmg

    auth = auth or self.auth

    return await dmg.DomoGrants.get_grants(auth = auth, return_raw = return_raw, session = session, debug_api = debug_api)
    

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 36
@patch_to(DomoInstanceConfig)
async def get_roles(
    self,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
):
    import domolibrary.classes.DomoRole as dmr

    auth = auth or self.auth

    return await dmr.DomoRoles.get_roles(auth=auth, debug_api=debug_api, return_raw = return_raw, session=session)

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 40
@patch_to(DomoInstanceConfig)
async def get_authorized_domains(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth

    res = await instance_config_routes.get_authorized_domains(
        auth=auth, debug_api=debug_api, session=session, return_raw=return_raw
    )

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 43
@patch_to(DomoInstanceConfig, cls_method=True)
async def set_authorized_domains(
    cls: DomoInstanceConfig,
    auth: dmda.DomoAuth,
    authorized_domains: list[str],
    debug_prn: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    if debug_prn:
        print(f'🌡️ setting authorized domain with {",".join(authorized_domains)}')

    res = await instance_config_routes.set_authorized_domains(
        auth=auth,
        authorized_domain_ls=authorized_domains,
        debug_api=debug_api,
        session=session,
    )

    if res.status == 200 or res.status == 204:
        dmdic = DomoInstanceConfig(auth=auth)
        res.response = {
            "authorized_domains": await dmdic.get_authorized_domains(debug_api=debug_api),
            "status": 200,
        }

    return res


@patch_to(DomoInstanceConfig, cls_method=True)
async def upsert_authorized_domains(
    cls: DomoInstanceConfig,
    auth: dmda.DomoAuth,
    authorized_domains: list[str],
    debug_prn: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    existing_domains = await cls.get_authorized_domains(
        auth=auth, debug_api=debug_api
    )

    authorized_domains += existing_domains

    if debug_prn:
        print(f'🌡️ upsertting authorized domain to {",".join(authorized_domains)}')

    return await cls.set_authorized_domains(
        auth=auth,
        authorized_domains=authorized_domains,
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 44
@patch_to(DomoInstanceConfig, cls_method=True)
async def get_applications(
    cls,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False):
    
    res = await application_routes.get_applications(
        auth=auth,
        debug=debug_api,
        session=session
    )

    if return_raw:
        return res

    if res.status != 200:
        return res
    
    return [DomoApplication._from_json(job) for job in res.response]



