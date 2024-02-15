# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/routes/instance_config.ipynb.

# %% auto 0
__all__ = [
    "get_is_invite_social_users_enabled",
    "ToggleSocialUsers_Error",
    "toggle_is_social_users_enabled",
    "ToggleUserInvite_Error",
    "toggle_is_user_invite_enabled",
    "get_is_user_invite_notifications_enabled",
    "get_sso_config",
    "generate_sso_body",
    "UpdateSSO_Error",
    "update_sso_config",
    "get_allowlist",
    "Allowlist_UnableToUpdate",
    "set_allowlist",
    "set_authorized_domains",
    "GetDomains_NotFound",
    "get_authorized_domains",
    "get_is_weekly_digest_enabled",
    "toggle_is_weekly_digest_enabled",
    "GetAppDomains_NotFound",
    "get_authorized_custom_app_domains",
    "set_authorized_custom_app_domains",
]

# %% ../../nbs/routes/instance_config.ipynb 3
import httpx

import domolibrary.client.get_data as gd
import domolibrary.client.ResponseGetData as rgd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de

from ..utils.convert import convert_string_to_bool

import domolibrary.routes.user as user_routes
import domolibrary.routes.bootstrap as bootstrap_routes


# %% ../../nbs/routes/instance_config.ipynb 6
@gd.route_function
async def get_is_invite_social_users_enabled(
    auth: dmda.DomoAuth,
    customer_id: str,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    return_raw: bool = False,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:

    # must pass the customer as the short form API endpoint (without customer_id) does not support a GET request
    # url = f"https://{auth.domo_instance}.domo.com/api/content/v3/customers/features/free-invite"

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/customers/{customer_id}/features/free-invite"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise ToggleSocialUsers_Error(
            status=res.status, message=res.response, domo_instance=auth.domo_instance
        )

    if return_raw:
        return res

    res.response = {"name": "free-invite", "is_enabled": res.response["enabled"]}

    return res


# %% ../../nbs/routes/instance_config.ipynb 9
class ToggleSocialUsers_Error(de.DomoError):
    def __init__(self, status, domo_instance, message="failure to toggle social users"):
        super().__init__(status=status, domo_instance=domo_instance, message=message)


@gd.route_function
async def toggle_is_social_users_enabled(
    is_enabled: bool,
    auth: dmda.DomoAuth = None,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    return_raw: bool = False,
    parent_class=False,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    """
    Admin > Features > Buzz
    Toggles the ability for users to add social users to Domo when sharing content
    """

    auth = auth or self.auth

    url = f"https://{auth.domo_instance}.domo.com/api/content/v3/customers/features/free-invite"

    body = {"enabled": is_enabled}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise ToggleSocialUsers_Error(
            status=res.status, message=res.response, domo_instance=auth.domo_instance
        )

    if return_raw:
        return res

    res.response = {
        "is_enabled": is_enabled,
        "feature": "free-invite",
    }

    return res


# %% ../../nbs/routes/instance_config.ipynb 13
class ToggleUserInvite_Error(de.DomoError):
    def __init__(
        self, status, domo_instance, message="failure to toggle user invite enabled"
    ):
        super().__init__(status=status, domo_instance=domo_instance, message=message)


@gd.route_function
async def toggle_is_user_invite_enabled(
    auth: dmda.DomoAuth,
    is_enabled: bool,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    return_raw: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    """
    Admin > Company Settings > Notifications
    """

    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/user.invite.email.enabled"

    body = {"value": is_enabled}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        session=session,
        debug_api=debug_api,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        raise ToggleUserInvite_Error(
            status=res.status, message=res.response, domo_instance=auth.domo_instance
        )

    if return_raw:
        return res

    res.response = {"feature": "user.invite.email.enabled", "is_enabled": is_enabled}

    return res


# %% ../../nbs/routes/instance_config.ipynb 16
@gd.route_function
async def get_is_user_invite_notifications_enabled(
    auth: dmda.DomoFullAuth,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
    return_raw: bool = False,
) -> rgd.ResponseGetData:
    url = f"https://{auth.domo_instance}.domo.com/api/customer/v1/properties/user.invite.email.enabled"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
    )

    if not res.is_success:
        raise ToggleSocialUsers_Error(
            status=res.status, message=res.response, domo_instance=auth.domo_instance
        )

    if return_raw:
        return res

    res.response = {
        "name": "user.invite.email.enabled",
        "is_enabled": convert_string_to_bool(res.response["value"]),
    }

    return res


# %% ../../nbs/routes/instance_config.ipynb 20
@gd.route_function
async def get_sso_config(
    auth: dmda.DomoAuth,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/oidc/std/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    return res


# %% ../../nbs/routes/instance_config.ipynb 24
def generate_sso_body(
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
):
    r = {
        "loginEnabled": login_enabled,
        "idpEnabled": idp_enabled,
        "importGroups": import_groups,
        "requireInvitation": require_invitation,
        "enforceWhitelist": enforce_allowlist,
        "skipToIdp": skip_to_idp,
        "authRequestEndpoint": auth_request_endpoint,
        "tokenEndpoint": token_endpoint,
        "userInfoEndpoint": user_info_endpoint,
        "publicKey": public_key,
        "redirectUrl": redirect_url,
        "certificate": certificate,
        "overrideSSO": override_sso,
        "overrideEmbed": override_embed,
        "wellKnownConfig": well_known_config,
        "assertionEndpoint": assertion_endpoint,
        "ingestAttributes": ingest_attributes,
    }

    return {key: value for key, value in r.items() if value is not None}


# %% ../../nbs/routes/instance_config.ipynb 25
class UpdateSSO_Error(de.DomoError):
    def __init__(
        self,
        domo_instance,
        config_body,
        function_name,
        status=None,
        parent_class=None,
    ):
        message = f'failed to set config to {  " || ".join([ key + " : " + str(value)  for key, value in config_body.items()]) }'

        super().__init__(
            domo_instance=domo_instance,
            message=message,
            status=status,
            parent_class=parent_class,
            function_name=function_name,
        )


@gd.route_function
async def update_sso_config(
    auth: dmda.DomoAuth,
    config_body: dict,
    session: httpx.AsyncClient = None,
    debug_api: bool = False,
    parent_class: str = None,
    debug_num_stacks_to_drop=1,
):
    """to successfully update the SSO Configuration, you must send all the parameters related to SSO Configuration"""

    url = f"https://{auth.domo_instance}.domo.com/api/identity/v1/authentication/oidc/std/settings"

    res = await gd.get_data(
        auth=auth,
        url=url,
        body=config_body,
        method="PUT",
        session=session,
        debug_api=debug_api,
        num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    if res.status == 200:
        res.is_success = True

    else:
        res.is_success = False
        raise UpdateSSO_Error(
            domo_instance=auth.domo_instance,
            config_body=config_body,
            status=res.status,
            function_name=res.traceback_details.function_name,
            parent_class=parent_class,
        )

    return res


# %% ../../nbs/routes/instance_config.ipynb 29
@gd.route_function
async def get_allowlist(
    auth: dmda.DomoFullAuth,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_api: bool = False,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:

    if auth.__class__.__name__ != "DomoFullAuth":
        raise dmda.InvalidAuthTypeError(
            function_name="get_allowlist",
            domo_instance=auth.domo_instance,
            required_auth_type=dmda.DomoFullAuth,
        )

    url = f"https://{auth.domo_instance}.domo.com/admin/companysettings/whitelist"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        headers={"accept": "*/*"},
        session=session,
        debug_api=debug_api,
        is_follow_redirects=True,
        return_raw=return_raw,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    return res


# %% ../../nbs/routes/instance_config.ipynb 34
class Allowlist_UnableToUpdate(de.DomoError):
    def __init__(
        self,
        status: int,
        reason: str,
        domo_instance: str,
        function_name: str = "update_allowlist",
    ):
        super().__init__(
            function_name=function_name,
            status=status,
            message=f"unable to update allowlist: {reason}",
            domo_instance=domo_instance,
        )


# %% ../../nbs/routes/instance_config.ipynb 35
@gd.route_function
async def set_allowlist(
    auth: dmda.DomoAuth,
    ip_address_ls: list[str],
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
) -> rgd.ResponseGetData:
    """companysettings/whitelist API only allows users to SET the allowlist does not allow INSERT or UPDATE"""

    url = f"https://{auth.domo_instance}.domo.com/admin/companysettings/whitelist"

    body = {"addresses": ip_address_ls}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        is_follow_redirects=True,
        return_raw=return_raw,
        session=session,
        headers={"accept": "text/plain"},
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )
    if not res.is_success:
        raise Allowlist_UnableToUpdate(
            status=res.status, reason=res.response, domo_instance=auth.domo_instance
        )

    if res.is_success:
        res.response = f"allow list updated from {res.response}"

    return res


# %% ../../nbs/routes/instance_config.ipynb 38
@gd.route_function
async def set_authorized_domains(
    auth: dmda.DomoAuth,
    authorized_domain_ls: [str],
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-domains"

    body = {"name": "authorized-domains", "value": ",".join(authorized_domain_ls)}

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    return res


# %% ../../nbs/routes/instance_config.ipynb 39
class GetDomains_NotFound(de.DomoError):
    def __init__(self, status, message, domo_instance):
        super().__init__(status=status, message=message, domo_instance=domo_instance)


@gd.route_function
async def get_authorized_domains(
    auth: dmda.DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-domains"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    # domo raises a 404 error even if the success is valid but there are no approved domains
    if res.status == 404 and res.response == "Not Found":
        res_test = await user_routes.get_all_users(auth=auth)

        if not res_test.is_success:
            raise GetDomains_NotFound(
                domo_instance=auth.domo_instance,
                status=res.status,
                message=res.response,
            )

        if res_test.is_success:
            res.status = 200
            res.is_success = True
            res.response = []

        return res

    res.response = [domain.strip() for domain in res.response.get("value").split(",")]
    return res


# %% ../../nbs/routes/instance_config.ipynb 43
@gd.route_function
async def get_is_weekly_digest_enabled(
    auth: dmda.DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/come-back-to-domo-all-users"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    res.response = {
        "is_enabled": convert_string_to_bool(res.response["value"]),
        "feature": "come-back-to-domo-all-users",
    }

    return res


# %% ../../nbs/routes/instance_config.ipynb 45
@gd.route_function
async def toggle_is_weekly_digest_enabled(
    auth: dmda.DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    is_enabled: bool = True,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/come-back-to-domo-all-users"

    body = {"name": "come-back-to-domo-all-users", "value": is_enabled}
    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if not res.is_success:
        return res

    return await get_is_weekly_digest_enabled(auth=auth)


# %% ../../nbs/routes/instance_config.ipynb 48
class GetAppDomains_NotFound(de.DomoError):
    def __init__(self, status, message, domo_instance):
        super().__init__(status=status, message=message, domo_instance=domo_instance)


@gd.route_function
async def get_authorized_custom_app_domains(
    auth: dmda.DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-app-domains"

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="GET",
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    # domo raises a 404 error even if the success is valid but there are no approved domains
    if res.status == 404 and res.response == "Not Found":
        res_test = await user_routes.get_all_users(auth=auth)

        if not res_test.is_success:
            raise GetAppDomains_NotFound(
                domo_instance=auth.domo_instance,
                status=res.status,
                message=res.response,
            )

        if res_test.is_success:
            res.status = 200
            res.is_success = True
            res.response = []

        return res

    res.response = [domain.strip() for domain in res.response.get("value").split(",")]
    return res


# %% ../../nbs/routes/instance_config.ipynb 51
@gd.route_function
async def set_authorized_custom_app_domains(
    auth: dmda.DomoAuth,
    authorized_custom_app_domain_ls: [str],
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    parent_class=None,
    debug_num_stacks_to_drop=1,
):
    url = f"https://{auth.domo_instance}.domo.com/api/content/v1/customer-states/authorized-app-domains"

    body = {
        "name": "authorized-app-domains",
        "value": ",".join(authorized_custom_app_domain_ls),
    }

    res = await gd.get_data(
        auth=auth,
        url=url,
        method="PUT",
        body=body,
        debug_api=debug_api,
        session=session,
        parent_class=parent_class,
        num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    return res
