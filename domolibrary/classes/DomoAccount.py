# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoAccount.ipynb.

# %% auto 0
__all__ = ['Account_CanIModify', 'UpsertAccount_MatchCriteria', 'DomoAccount', 'DomoAccounts']

# %% ../../nbs/classes/50_DomoAccount.ipynb 3
from dataclasses import dataclass, field

import datetime as dt
import re

import httpx

from fastcore.basics import patch_to

import domolibrary.utils.convert as cd
import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.account as account_routes

import domolibrary.utils.chunk_execution as ce


# %% ../../nbs/classes/50_DomoAccount.ipynb 4
from domolibrary.routes.account import (
    ShareAccount_V1_AccessLevel,
    ShareAccount_V2_AccessLevel,
    ShareAccount,
    GetAccount_NoMatch,
    ShareAccount_Error,
    DeleteAccount_Error,
)

from domolibrary.classes.DomoAccount_Config import (
    AccountConfig_UsesOauth,
    AccountConfig_ProviderTypeNotDefined,
    DomoAccount_Config,
    AccountConfig,
)


class Account_CanIModify(de.DomoError):
    def __init__(self, account_id, domo_instance):
        super().__init__(
            message=f"`DomoAccount.is_admin_summary` must be `False` to proceed.  Either set the value explicity, or retrieve the account instance using `DomoAccount.get_by_id()`",
            domo_instance=domo_instance,
        )


class UpsertAccount_MatchCriteria(de.DomoError):
    def __init__(self, domo_instance):
        super().__init__(
            message="must pass an account_id or account_name to UPSERT",
            domo_instance=domo_instance,
        )

# %% ../../nbs/classes/50_DomoAccount.ipynb 6
@dataclass
class DomoAccount:
    data_provider_type: str = None
    name: str = None

    id: int = None
    created_dt: dt.datetime = None
    modified_dt: dt.datetime = None
    auth: dmda.DomoAuth = field(repr=False, default=None)

    config: DomoAccount_Config = (None,)

    is_admin_summary: bool = True

    @classmethod
    def _from_json(
        cls,
        obj: dict,
        is_admin_summary: bool = True,
        auth: dmda.DomoAuth = None,
    ):
        """converts data_v1_accounts API response into an accounts class object"""

        dd = util_dd.DictDot(obj)

        return cls(
            id=dd.id or dd.databaseId,
            name=dd.displayName,
            data_provider_type=dd.dataProviderId or dd.dataProviderType,
            created_dt=cd.convert_epoch_millisecond_to_datetime(
                dd.createdAt or dd.createDate
            ),
            modified_dt=cd.convert_epoch_millisecond_to_datetime(
                dd.modifiedAt or dd.lastModified
            ),
            auth=auth,
            is_admin_summary=is_admin_summary,
        )

# %% ../../nbs/classes/50_DomoAccount.ipynb 8
@patch_to(DomoAccount)
async def _get_config(
    self: DomoAccount,
    session=None,
    return_raw: bool = False,
    debug_api: bool = None,
    auth: dmda.DomoAuth = None,
    debug_num_stacks_to_drop=2,
    is_suppress_no_config: bool = False,  # can be used to suppress cases where the config is not defined, either because the account_config is OAuth, and therefore not stored in Domo OR because the AccountConfig class doesn't cover the data_type
):
    res = await account_routes.get_account_config(
        auth=auth or self.auth,
        account_id=self.id,
        session=session,
        debug_api=debug_api,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    data_provider_type = res.response.get(
        "_search_metadata").get("data_provider_type")

    config_fn = AccountConfig(data_provider_type).value

    if not is_suppress_no_config and not config_fn.is_defined_config:
        raise config_fn._associated_exception(data_provider_type)

    self.config = config_fn._from_json(res.response)

    return self.config


# %% ../../nbs/classes/50_DomoAccount.ipynb 11
@patch_to(DomoAccount, cls_method=True)
async def get_by_id(
    cls,
    auth: dmda.DomoAuth,
    account_id: int,
    is_suppress_no_config: bool = True,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_num_stacks_to_drop=2,
):
    """retrieves account metadata and attempts to retrieve config"""

    res = await account_routes.get_account_from_id(
        auth=auth,
        account_id=account_id,
        session=session,
        debug_api=debug_api,
        parent_class=cls.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

    if return_raw:
        return res

    acc = cls._from_json(obj=res.response, auth=auth, is_admin_summary=False)

    await acc._get_config(
        session=session,
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        is_suppress_no_config=is_suppress_no_config,
    )

    return acc

# %% ../../nbs/classes/50_DomoAccount.ipynb 18
@staticmethod
@patch_to(DomoAccount)
def generate_create_body(account_name, config):
    return {
        "displayName": account_name,
        "dataProviderType": config.data_provider_type,
        "name": config.data_provider_type,
        "configurations": config.to_json(),
    }


@patch_to(DomoAccount, cls_method=True)
async def create_account(
    cls: DomoAccount,
    account_name: str,
    config: DomoAccount_Config,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    body = cls.generate_create_body(account_name=account_name, config=config)

    res = await account_routes.create_account(
        auth=auth, config_body=body, debug_api=debug_api, session=session
    )

    return await cls.get_by_id(auth=auth, account_id=res.response.get("id"))

# %% ../../nbs/classes/50_DomoAccount.ipynb 20
@patch_to(DomoAccount)
async def update_config(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    config: DomoAccount_Config = None,
    is_suppress_no_config=False,
    debug_num_stacks_to_drop=2,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    if self.is_admin_summary:
        raise Account_CanIModify(account_id=self.id, domo_instance=auth.domo_instance)

    auth = auth or self.auth
    config = config or self.config

    res = await account_routes.update_account_config(
        auth=auth,
        account_id=self.id,
        config_body=config.to_json(),
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res

    await self._get_config(
        debug_api=debug_api,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop + 1,
        is_suppress_no_config=is_suppress_no_config,
    )

    return self

# %% ../../nbs/classes/50_DomoAccount.ipynb 25
@patch_to(DomoAccount)
async def update_name(
    self: DomoAccount,
    account_name: str = None,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    if self.is_admin_summary:
        raise Account_CanIModify(account_id=self.id, domo_instance=auth.domo_instance)

    auth = auth or self.auth

    res = await account_routes.update_account_name(
        auth=auth,
        account_id=self.id,
        account_name=account_name or self.name,
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res

    await self.get_by_id(auth=auth, account_id=self.id)

    return self

# %% ../../nbs/classes/50_DomoAccount.ipynb 30
@patch_to(DomoAccount)
async def delete_account(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=2,
):
    if self.is_admin_summary:
        raise Account_CanIModify(account_id=self.id, domo_instance=auth.domo_instance)

    auth = auth or self.auth

    res = await account_routes.delete_account(
        auth=auth,
        account_id=self.id,
        debug_api=debug_api,
        session=session,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
        parent_class=parent_class,
    )

    return res

# %% ../../nbs/classes/50_DomoAccount.ipynb 32
@patch_to(DomoAccount)
async def _is_group_ownership_beta(
    self, auth: dmda.DomoAuth = None, return_raw: bool = False
):
    import domolibrary.classes.DomoBootstrap as dmbs

    auth = auth or self.auth

    domo_bsr = dmbs.DomoBootstrap(auth=auth)

    domo_feature_ls = await domo_bsr.get_features()

    if return_raw:
        return domo_feature_ls

    match_accounts_v2 = next(
        (
            domo_feature
            for domo_feature in domo_feature_ls
            if domo_feature.name == "accounts-v2"
        ),
        None,
    )

    return True if match_accounts_v2 else False

# %% ../../nbs/classes/50_DomoAccount.ipynb 34
@patch_to(DomoAccount)
async def _share_v2(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    user_id=None,
    group_id=None,
    access_level: ShareAccount = ShareAccount_V2_AccessLevel.CAN_VIEW,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    debug_num_stacks_to_drop=2,
):
    share_payload = account_routes.generate_share_account_payload_v2(
        user_id=user_id,
        group_id=group_id,
        access_level=access_level,
    )

    return await account_routes.share_account_v2(
        auth=auth,
        account_id=self.id,
        share_payload=share_payload,
        debug_api=debug_api,
        session=session,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )

# %% ../../nbs/classes/50_DomoAccount.ipynb 37
@patch_to(DomoAccount)
async def _share_v1(self: DomoAccount,
                    auth: dmda.DomoAuth = None,
                    user_id=None,
                    group_id=None,
                    access_level: ShareAccount = ShareAccount_V1_AccessLevel.CAN_VIEW,
                    debug_api: bool = False,
                    session: httpx.AsyncClient = None,
                    debug_num_stacks_to_drop=2
                    ):

    share_payload = account_routes.generate_share_account_payload_v1(
        user_id=user_id,
        group_id=group_id,
        access_level=access_level,
    )

    return await account_routes.share_account_v1(
        auth=auth,
        account_id=self.id,
        share_payload=share_payload,
        debug_api=debug_api,
        session=session,
        parent_class=self.__class__.__name__,
        debug_num_stacks_to_drop=debug_num_stacks_to_drop,
    )


# %% ../../nbs/classes/50_DomoAccount.ipynb 44
@dataclass
class DomoAccounts:
    auth: dmda.DomoAuth

# %% ../../nbs/classes/50_DomoAccount.ipynb 45
@staticmethod
@patch_to(DomoAccounts)
async def _get_accounts_accountsapi(
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    res = await account_routes.get_accounts(
        auth=auth, debug_api=debug_api, session=session
    )

    if return_raw:
        return res

    if len(res.response) == 0:
        return []

    return await ce.gather_with_concurrency(
        n=60,
        *[
            DomoAccount.get_by_id(
                account_id=json_obj.get("id"),
                debug_api=debug_api,
                session=session,
                auth=auth,
            )
            for json_obj in res.response
        ],
    )


@patch_to(DomoAccounts, cls_method=True)
async def _get_accounts_queryapi(
    cls: DomoAccounts,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    additional_filters_ls=None,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    """v2 api for works with group_account_v2 beta"""

    import domolibrary.routes.datacenter as datacenter_routes

    res = await datacenter_routes.search_datacenter(
        auth=auth,
        entity_type=datacenter_routes.Datacenter_Enum.ACCOUNT.value,
        additional_filters_ls=additional_filters_ls,
        session=session,
        debug_api=debug_api,
    )

    if return_raw:
        return res

    if len(res.response) == 0:
        return []

    return [
        DomoAccount._from_json(account_obj, auth=auth) for account_obj in res.response
    ]


@patch_to(DomoAccounts, cls_method=True)
async def get_accounts(
    cls: DomoAccounts,
    auth: dmda.DomoAuth,
    additional_filters_ls=None,  # datacenter_routes.generate_search_datacenter_filter
    # account string to search for, must be an exact match in spelling.  case insensitive
    # v2 will use the queryAPI as it returns more complete results than the accountsAPI
    is_v2: bool = None,
    is_suppress_undefined_provider_type: bool = False,
    account_name: str = None,
    account_id: str = None,
    account_type: AccountConfig = None,  # to retrieve a specific account type
    account_type_str=None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_prn: bool = False,
):
    import domolibrary.classes.DomoBootstrap as bsr
    import domolibrary.routes.datacenter as datacenter_routes

    if isinstance(auth, dmda.DomoFullAuth) and is_v2 is None:
        instance_bsr = bsr.DomoBootstrap(auth=auth)

        is_v2 = await instance_bsr.is_group_ownership_beta(auth)

        if debug_prn:
            print(
                f"{auth.domo_instance} {'is' if is_v2 else 'is not'} using the v2 beta"
            )

    if is_v2:
        try:
            domo_accounts = await cls._get_accounts_queryapi(
                auth=auth,
                debug_api=debug_api,
                additional_filters_ls=additional_filters_ls,
                session=session,
            )
        except datacenter_routes.SearchDatacenter_NoResultsFound as e:
            print(e)
            domo_accounts = []
    else:
        domo_accounts = await cls._get_accounts_accountsapi(
            auth=auth, debug_api=debug_api, session=session
        )

    if return_raw or len(domo_accounts) == 0:
        return domo_accounts

    if account_id:
        domo_account = next(
            (
                domo_account
                for domo_account in domo_accounts
                if int(domo_account.id) == int(account_id)
            ),
            None,
        )

        if not domo_account:
            raise GetAccount_NoMatch(
                account_id=account_id, domo_instance=auth.domo_instance
            )

        return domo_account

    if account_name and isinstance(account_name, str):
        domo_accounts = [
            domo_account
            for domo_account in domo_accounts
            if domo_account.name.lower() == account_name.lower()
        ]

    if account_type:
        return [
            domo_account
            for domo_account in domo_accounts
            if domo_account.data_provider_type == account_type.value.data_provider_type
        ]

    if account_type_str:
        return [
            domo_account
            for domo_account in domo_accounts
            if domo_account.data_provider_type == account_type_str
        ]

    return domo_accounts

# %% ../../nbs/classes/50_DomoAccount.ipynb 48
@patch_to(DomoAccount)
async def get_accesslist(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    return_raw: bool = False,
    session: httpx.AsyncClient = None,
):
    res = await account_routes.get_account_accesslist_for_v2(
        auth=auth or self.auth, account_id=self.id, debug_api=debug_api, session=session
    )

    if return_raw:
        return res

    return res.response["list"]

# %% ../../nbs/classes/50_DomoAccount.ipynb 52
@patch_to(DomoAccounts, cls_method=True)
async def upsert_account(
    cls: DomoAccounts,
    auth: dmda.DomoAuth,
    account_config: AccountConfig = None,
    account_name: str = None,
    account_id: str = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    """search for an account and upsert it"""

    if not account_name and not account_id:
        raise UpsertAccount_MatchCriteria(domo_instance=auth.domo_instance)

    acc = None

    if account_id:
        acc = await DomoAccounts.get_accounts(account_id=account_id, auth=auth)

        if acc and account_name:
            if debug_prn:
                print(f"upsertting {acc.id}:  updating account_name")
            await acc.update_name(account_name=account_name, debug_api=debug_api)

    if account_name and acc is None:
        acc = await DomoAccounts.get_accounts(
            account_name=account_name,
            auth=auth,
            account_type_str=(account_config and account_config.data_provider_type)
            or None,
            # is_suppress_undefined_provider_type = True
        )

        if isinstance(acc, list) and len(acc) > 0 and isinstance(acc[0], DomoAccount):
            acc = acc[0]

        else:
            acc = None

    if acc and account_config:  # upsert account
        acc.config = account_config

        if debug_prn:
            print(f"upsertting {acc.id}:  updating config")

        await acc.update_config(debug_api=debug_api)

    if not acc:
        if debug_prn:
            print(f"creating account {account_name} in {auth.domo_instance}")

        acc = await DomoAccount.create_account(
            account_name=account_name,
            config=account_config,
            auth=auth,
            debug_api=debug_api,
        )

    return acc

# %% ../../nbs/classes/50_DomoAccount.ipynb 56
@patch_to(DomoAccount)
async def upsert_share_account_user(
    self: DomoAccount,
    domo_user,
    auth: dmda.DomoAuth = None,
    is_v2: bool = None,
    access_level: ShareAccount = None,  # will default to Read
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    ls_share = await account_routes.get_account_accesslist_for_v2(
        auth=auth, account_id=self.id
    )
    res = None
    if domo_user:
        user_id = domo_user.id
        found_user = next(
            (
                obj
                for obj in ls_share.response["list"]
                if obj["id"] == user_id and obj["type"] == "USER"
            ),
            None,
        )
        if not found_user:
            res = await self.share(
                domo_user=domo_user,
                auth=auth,
                is_v2=is_v2,
                access_level=access_level,
                debug_api=debug_api,
                debug_prn=debug_prn,
                session=session,
            )

    return res


@patch_to(DomoAccount)
async def upsert_share_account_group(
    self: DomoAccount,
    domo_group,
    auth: dmda.DomoAuth = None,
    is_v2: bool = None,
    access_level: ShareAccount = None,  # will default to Read
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    ls_share = await account_routes.get_account_accesslist_for_v2(
        auth=auth, account_id=self.id
    )
    res = None

    if domo_group:
        group_id = domo_group.id
        found_group = next(
            (
                obj
                for obj in ls_share.response["list"]
                if obj["id"] == group_id and obj["type"] == "GROUP"
            ),
            None,
        )
        if not found_group:
            res = await self.share(
                domo_group=domo_group,
                auth=auth,
                is_v2=is_v2,
                access_level=access_level,
                debug_api=debug_api,
                debug_prn=debug_prn,
                session=session,
            )

    return res
