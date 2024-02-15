# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoInstanceConfig.ipynb.

# %% auto 0
__all__ = ['DomoInstanceConfig', 'SSO_Config', 'DomoConnector']

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 2
from ..routes.instance_config import UpdateSSO_Error

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 3
import httpx
import datetime as dt
import asyncio
from fastcore.basics import patch_to
import sys
import pandas as pd


from dataclasses import dataclass, field, asdict
from typing import List

import domolibrary.utils.DictDot as util_dd
import domolibrary.utils.chunk_execution as ce
import domolibrary.utils.convert as cd

import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.client.Logger as lg

import domolibrary.classes.DomoInstanceConfig_UserAttribute as dicua

import domolibrary.routes.instance_config as instance_config_routes
import domolibrary.routes.bootstrap as bootstrap_routes
import domolibrary.routes.sandbox as sandbox_routes
import domolibrary.routes.publish as publish_routes
import domolibrary.routes.application as application_routes

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 5
@dataclass
class DomoInstanceConfig:
    """utility class that absorbs many of the domo instance configuration methods"""

    auth: dmda.DomoAuth
    allowlist: list[str] = field(default_factory=list)

    is_sandbox_self_instance_promotion_enabled: bool = field(default=None)
    is_user_invite_notification_enabled: bool = field(default=None)
    is_invite_social_users_enabled: bool = field(default=None)

    sso_config: dict = field(default=None)

    user_attributes: dicua.UserAttributes = None

    def __post_init__(self):
        self.user_attributes = dicua.UserAttributes(auth=self.auth)

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 10
@patch_to(DomoInstanceConfig)
async def get_sandbox_is_same_instance_promotion_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_num_stacks_to_drop=2,
):
    auth = auth or self.auth

    res = await sandbox_routes.get_is_allow_same_instance_promotion_enabled(
        auth=auth or self.auth,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=self.__class__.__name__,
    )

    self.is_sandbox_self_instance_promotion_enabled = res.response["is_enabled"]

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 13
@patch_to(DomoInstanceConfig)
async def toggle_sandbox_allow_same_instance_promotion(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth,
    is_enabled: bool,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_num_stacks_to_drop=2,
):
    res = await sandbox_routes.toggle_allow_same_instance_promotion(
        auth=auth or self.auth,
        session=session,
        is_enabled=is_enabled,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=self.__class__.__name__,
    )

    res_is_enabled = await self.get_sandbox_is_same_instance_promotion_enabled()

    if return_raw:
        return res

    return res_is_enabled

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 16
@patch_to(DomoInstanceConfig)
async def get_is_user_invite_notification_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    """
    Admin > Company Settings > Admin Notifications
    Toggles whether user recieves 'You've been Domo'ed email
    """

    auth = auth or self.auth

    res = await instance_config_routes.get_is_user_invite_notifications_enabled(
        auth=auth or self.auth,
        session=session,
        debug_api=debug_api,
    )

    self.is_user_invite_notification_enabled = res.response["is_enabled"]

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 19
@patch_to(DomoInstanceConfig)
async def toggle_is_user_invite_notification_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth,
    is_enabled: bool,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    res_is_enabled = await self.get_is_user_invite_notification_enabled(auth=auth)

    if is_enabled == self.is_user_invite_notification_enabled:
        if debug_prn:
            print(
                f"User invite notification is already {'enabled' if is_enabled else 'disabled'} in {auth.domo_instance}"
            )
        return res_is_enabled

    if debug_prn:
        print(
            f"{'enabling' if is_enabled else 'disabling'} User invite notification {auth.domo_instance}"
        )

    res = await instance_config_routes.toggle_is_user_invite_enabled(
        auth=auth or self.auth,
        is_enabled=is_enabled,
        session=session,
        debug_api=debug_api,
    )

    res_is_enabled = await self.get_is_user_invite_notification_enabled(auth=auth)

    if return_raw:
        return res

    return res_is_enabled

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 23
@patch_to(DomoInstanceConfig)
async def get_is_invite_social_users_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    import domolibrary.classes.DomoBootstrap as dmbp

    auth = auth or self.auth
    bs = dmbp.DomoBootstrap(auth=auth)
    customer_id = await bs.get_customer_id()

    res = await instance_config_routes.get_is_invite_social_users_enabled(
        auth=auth or self.auth,
        customer_id=customer_id,
        session=session,
        debug_api=debug_api,
    )

    self.is_invite_social_users_enabled = res.response["is_enabled"]

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 26
@patch_to(DomoInstanceConfig)
async def toggle_is_invite_social_users_enabled(
    self: DomoInstanceConfig,
    is_enabled: bool,
    auth: dmda.DomoFullAuth = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth

    res_is_enabled = await self.get_is_invite_social_users_enabled(auth=auth)

    if is_enabled == self.is_invite_social_users_enabled:
        if debug_prn:
            print(
                f"invite social users is already {'enabled' if is_enabled else 'disabled'} in {auth.domo_instance}"
            )
        return res_is_enabled

    if debug_prn:
        print(
            f"{'enabling' if is_enabled else 'disabling'} invite social users {auth.domo_instance}"
        )

    res = await instance_config_routes.toggle_is_social_users_enabled(
        auth=auth or self.auth,
        is_enabled=is_enabled,
        session=session,
        debug_api=debug_api,
    )

    res_is_enabled = await self.get_is_invite_social_users_enabled()

    if return_raw:
        return res

    return res_is_enabled

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 30
@patch_to(DomoInstanceConfig)
async def get_is_weekly_digest_enabled(
    self: DomoInstanceConfig,
    auth: dmda.DomoFullAuth = None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop: int = 2,
    session: httpx.AsyncClient = None,
):

    res = await instance_config_routes.get_is_weekly_digest_enabled(
        auth=auth or self.auth,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=self.__class__.__name__,
    )

    self.is_weekly_digest_enabled = res.response["is_enabled"]

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 32
@patch_to(DomoInstanceConfig)
async def toggle_is_weekly_digest_enabled(
    self: DomoInstanceConfig,
    is_enabled: bool,
    auth: dmda.DomoFullAuth = None,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    debug_num_stacks_to_drop=1,
):
    auth = auth or self.auth

    res_is_enabled = await self.get_is_weekly_digest_enabled(auth=auth)

    if is_enabled == self.is_weekly_digest_enabled:
        if debug_prn:
            print(
                f"weekly digest is already {'enabled' if is_enabled else 'disabled'} in {auth.domo_instance}"
            )
        return res_is_enabled

    if debug_prn:
        print(
            f"{'enabling' if is_enabled else 'disabling'} weekly digest {auth.domo_instance}"
        )

    res = await instance_config_routes.toggle_is_weekly_digest_enabled(
        auth=auth or self.auth,
        is_enabled=is_enabled,
        session=session,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    res_is_enabled = await self.get_is_weekly_digest_enabled()

    if return_raw:
        return res

    return res_is_enabled

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 35
py310 = sys.version_info.minor >= 10 or sys.version_info.major > 3

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 36
# class SSOConfig_InstantiationError(de.DomoError):
#     def __init__(self, domo_instance, parent_class, function_name, message="invalid data types, check attribute types"):

#         super().__init__(
#             domo_instance=domo_instance,
#             message=message,
#             parent_class=parent_class,
#             function_name=function_name)


@dataclass(**({"slots": True} if py310 else {}))
class SSO_Config:
    auth: dmda.DomoAuth = field(repr=False)

    login_enabled: bool = None  # False
    idp_enabled: bool = None  # False
    import_groups: bool = None  # False
    require_invitation: bool = None  # False
    enforce_allowlist: bool = None  # False
    skip_to_idp: bool = None  # False
    auth_request_endpoint: str = None
    token_endpoint: str = None
    user_info_endpoint: str = None
    public_key: str = None
    redirect_url: str = None
    certificate: str = None
    override_sso: bool = None  # False
    override_embed: bool = None  # False
    # "https://{domo_instance}}.domo.com/auth/oidc"
    well_known_config: str = None
    assertion_endpoint: str = None
    ingest_attributes: bool = None  # False

    # def __post_init__(self):
    #     self.override_sso = self.override_sso or f"https://{auth.domo_instance}.domo.com/auth/oidc"

    @classmethod
    def _from_json(cls, auth: dmda.DomoAuth, obj: dict):
        dd = obj

        if not isinstance(obj, util_dd.DictDot):
            dd = util_dd.DictDot(obj)

        return cls(
            auth=auth,
            login_enabled=dd.loginEnabled,
            idp_enabled=dd.idpEnabled,
            import_groups=dd.importGroups,
            require_invitation=dd.requireInvitation,
            enforce_allowlist=dd.enforceWhitelist,
            skip_to_idp=dd.skipToIdp,
            auth_request_endpoint=dd.authRequestEndpoint,
            token_endpoint=dd.tokenEndpoint,
            user_info_endpoint=dd.userInfoEndpoint,
            public_key=dd.publicKey,
            redirect_url=dd.redirectUrl,
            certificate=dd.certificate,
            override_sso=dd.overrideSSO,
            override_embed=dd.overrideEmbed,
            well_known_config=dd.wellKnownConfig,
            assertion_endpoint=dd.assertionEndpoint,
            ingest_attributes=dd.ingestAttributes,
        )

    def add_attribute(self, overwrite_existing: bool = False, **kwargs):
        [
            setattr(self, key, value)
            for key, value in kwargs.items()
            if value is not None
        ]
        return self

        # except TypeError as e:
        #     traceback_details = lg.get_traceback(num_stacks_to_drop=1)

        #     raise SSOConfig_InstantiationError(
        #         domo_instance=self.auth.domo_instance,
        #         parent_class=self.__class__.__name__,
        #         function_name=traceback_details.function_name)

    def to_json(self, is_include_undefined: bool = False):
        r = {
            "loginEnabled": self.login_enabled,
            "idpEnabled": self.idp_enabled,
            "importGroups": self.import_groups,
            "requireInvitation": self.require_invitation,
            "enforceWhitelist": self.enforce_allowlist,
            "skipToIdp": self.skip_to_idp,
            "authRequestEndpoint": self.auth_request_endpoint,
            "tokenEndpoint": self.token_endpoint,
            "userInfoEndpoint": self.user_info_endpoint,
            "publicKey": self.public_key,
            "redirectUrl": self.redirect_url,
            "certificate": self.certificate,
            "overrideSSO": self.override_sso,
            "overrideEmbed": self.override_embed,
            "wellKnownConfig": self.well_known_config,
            "assertionEndpoint": self.assertion_endpoint,
            "ingestAttributes": self.ingest_attributes,
        }

        if not is_include_undefined:
            return {key: value for key, value in r.items() if value is not None}

        return r

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 38
@patch_to(DomoInstanceConfig)
async def get_sso_config(
    self: DomoInstanceConfig,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    return_raw: bool = False,
):
    res = await instance_config_routes.get_sso_config(
        auth=self.auth,
        session=session,
        parent_class=self.__class__.__name__,
        debug_api=debug_api,
        debug_num_stacks_to_drop=2,
    )

    if return_raw:
        return res

    self.sso_config = SSO_Config._from_json(auth=auth, obj=res.response)

    return self.sso_config

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 42
@patch_to(DomoInstanceConfig)
async def update_sso_config(
    self: DomoInstanceConfig,
    login_enabled: bool = None,  # False
    idp_enabled: bool = None,  # False
    import_groups: bool = None,  # False
    require_invitation: bool = None,  # False
    enforce_allowlist: bool = None,  # False
    skip_to_idp: bool = None,  # False
    auth_request_endpoint: str = None,
    token_endpoint: str = None,
    user_info_endpoint: str = None,
    public_key: str = None,
    redirect_url: str = None,
    certificate: str = None,
    override_sso: bool = None,  # False
    override_embed: bool = None,  # False
    # "https://{domo_instance}}.domo.com/auth/oidc"
    well_known_config: str = None,
    assertion_endpoint: str = None,
    ingest_attributes: bool = None,  # False
    debug_is_test: bool = False,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
):
    update_config = await self.get_sso_config()

    update_config.add_attribute(
        overwrite_existing=True,
        login_enabled=login_enabled,
        idp_enabled=idp_enabled,
        import_groups=import_groups,
        require_invitation=require_invitation,
        enforce_allowlist=enforce_allowlist,
        skip_to_idp=skip_to_idp,
        auth_request_endpoint=auth_request_endpoint,
        token_endpoint=token_endpoint,
        user_info_endpoint=user_info_endpoint,
        public_key=public_key,
        redirect_url=redirect_url,
        certificate=certificate,
        override_sso=override_sso,
        override_embed=override_embed,
        well_known_config=well_known_config,
        assertion_endpoint=assertion_endpoint,
        ingest_attributes=ingest_attributes,
    )

    config_body = update_config.to_json()

    if debug_is_test:
        print("⚗️⚠️ This is a test, SSO Config will not be updated")
        return config_body

    res = await instance_config_routes.update_sso_config(
        auth=self.auth,
        config_body=config_body,
        parent_class=self.__class__.__name__,
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=2,
    )

    # await asyncio.sleep(3)

    await self.get_sso_config()

    errors_obj = {
        update_key: f"expected_value: {str(update_value)  } , current_value: { str(self.sso_config[update_key])}"
        for update_key, update_value in asdict(update_config).items()
        if asdict(self.sso_config)[update_key] != update_value
    }

    if len(errors_obj.keys()) > 0:
        raise instance_config_routes.UpdateSSO_Error(
            domo_instance=self.auth.domo_instance,
            config_body=errors_obj,
            function_name=res.traceback_details.function_name,
            parent_class=self.__class__.__name,
        )

    return self.sso_config

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 46
@patch_to(DomoInstanceConfig, cls_method=True)
async def get_publications(
    cls: DomoInstanceConfig,
    auth: dmda.DomoFullAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    import domolibrary.classes.DomoPublish as dmpb

    res = await publish_routes.search_publications(
        auth=auth, debug_api=debug_api, session=session
    )
    if debug_api:
        print("Getting Publish jobs")

    if res.status == 200 and not return_raw:
        return await ce.gather_with_concurrency(
            n=60,
            *[
                dmpb.DomoPublication.get_from_id(
                    publication_id=job.get("id"), auth=auth
                )
                for job in res.response
            ],
        )

    if res.status == 200 and return_raw:
        return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 50
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

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 54
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

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 59
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

    return await dmg.DomoGrants.get_grants(
        auth=auth, return_raw=return_raw, session=session, debug_api=debug_api
    )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 62
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

    return await dmr.DomoRoles.get_roles(
        auth=auth, debug_api=debug_api, return_raw=return_raw, session=session
    )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 66
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

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 69
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
            "authorized_domains": await dmdic.get_authorized_domains(
                debug_api=debug_api
            ),
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
    existing_domains = await cls.get_authorized_domains(auth=auth, debug_api=debug_api)

    authorized_domains += existing_domains

    if debug_prn:
        print(f'🌡️ upsertting authorized domain to {",".join(authorized_domains)}')

    return await cls.set_authorized_domains(
        auth=auth,
        authorized_domains=authorized_domains,
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 71
@patch_to(DomoInstanceConfig)
async def get_authorized_custom_app_domains(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth

    res = await instance_config_routes.get_authorized_custom_app_domains(
        auth=auth, debug_api=debug_api, session=session, return_raw=return_raw
    )

    if return_raw:
        return res

    return res.response

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 75
@patch_to(DomoInstanceConfig, cls_method=True)
async def set_authorized_custom_app_domains(
    cls: DomoInstanceConfig,
    auth: dmda.DomoAuth,
    authorized_domains: list[str],
    debug_prn: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    if debug_prn:
        print(f'🌡️ setting authorized domain with {",".join(authorized_domains)}')

    res = await instance_config_routes.set_authorized_custom_app_domains(
        auth=auth,
        authorized_custom_app_domain_ls=authorized_domains,
        debug_api=debug_api,
        session=session,
    )

    if res.status == 200 or res.status == 204:
        dmdic = DomoInstanceConfig(auth=auth)
        res.response = {
            "authorized_domains": await dmdic.get_authorized_custom_app_domains(
                debug_api=debug_api
            ),
            "status": 200,
        }

    return res


@patch_to(DomoInstanceConfig, cls_method=True)
async def upsert_authorized_custom_app_domains(
    cls: DomoInstanceConfig,
    auth: dmda.DomoAuth,
    authorized_domains: list[str],
    debug_prn: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    existing_domains = await cls.get_authorized_custom_app_domains(
        auth=auth, debug_api=debug_api
    )

    authorized_domains += existing_domains

    if debug_prn:
        print(f'🌡️ upsertting authorized domain to {",".join(authorized_domains)}')

    return await cls.set_authorized_custom_app_domains(
        auth=auth,
        authorized_custom_app_domain_ls=authorized_domains,
        debug_api=debug_api,
        session=session,
    )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 77
@patch_to(DomoInstanceConfig, cls_method=True)
async def get_applications(
    cls,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_num_stacks_to_drop=2,
):
    import domolibrary.classes.DomoApplication as dmapp

    res = await application_routes.get_applications(
        auth=auth,
        debug_api=debug_api,
        session=session,
        parent_class=cls.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    if res.status != 200:
        return res

    return [dmapp.DomoApplication._from_json(job) for job in res.response]

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 80
@patch_to(DomoInstanceConfig)
async def generate_applications_report(
    self,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_num_stacks_to_drop=2,
):
    import domolibrary.classes.DomoApplication as dmapp

    domo_apps = await self.get_applications(auth=self.auth, debug_api=debug_api)

    df = pd.DataFrame([app.__dict__ for app in domo_apps])
    df["domo_instance"] = self.auth.domo_instance

    df.drop(columns=["auth"], inplace=True)
    df.rename(
        columns={
            "id": "application_id",
            "name": "application_name",
            "description": "application_description",
            "version": "application_version",
        },
        inplace=True,
    )

    return df.sort_index(axis=1)

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 84
@dataclass
class DomoConnector:
    id: str
    label: str
    title: str
    sub_title: str
    description: str
    create_date: dt.datetime
    last_modified: dt.datetime
    publisher_name: str
    writeback_enabled: bool
    tags: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)

    @classmethod
    def _from_str(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            id=dd.databaseId,
            label=dd.label,
            title=dd.title,
            sub_title=dd.subTitle,
            description=dd.description,
            create_date=cd.convert_epoch_millisecond_to_datetime(dd.createDate),
            last_modified=cd.convert_epoch_millisecond_to_datetime(dd.lastModified),
            publisher_name=dd.publisherName,
            writeback_enabled=dd.writebackEnabled,
            tags=dd.tags,
            capabilities=dd.capabilities,
        )

# %% ../../nbs/classes/50_DomoInstanceConfig.ipynb 85
@patch_to(DomoInstanceConfig)
async def get_connectors(
    self: DomoInstanceConfig,
    auth: dmda.DomoAuth = None,
    search_text=None,
    additional_filters_ls=None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
    session: httpx.AsyncClient = None,
):
    import domolibrary.routes.datacenter as datacenter_routes

    res = await datacenter_routes.get_connectors(
        auth=auth or self.auth,
        session=session,
        search_text=search_text,
        additional_filters_ls=additional_filters_ls,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    return [DomoConnector._from_str(obj) for obj in res.response]
