# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoAccount.ipynb.

# %% auto 0
__all__ = ['DomoAccount_Config', 'DomoAccount_Config_AbstractCredential', 'DomoAccount_Config_DatasetCopy',
           'DomoAccount_Config_DomoAccessToken', 'DomoAccount_Config_Governance', 'DomoAccount_Config_AmazonS3',
           'DomoAccount_Config_AmazonS3Advanced', 'DomoAccount_Config_AwsAthena',
           'DomoAccount_Config_HighBandwidthConnector', 'AccountConfig', 'DomoAccount',
           'DomoAccount_DataProviderType_ConfigNotDefined', 'DomoAccount_CreateAccount_Error',
           'DomoAccount_UpdateError', 'DomoAccount_DeleteAccount_Error', 'ShareAccount_Error', 'DomoAccounts',
           'GetAccounts_NotFound']

# %% ../../nbs/classes/50_DomoAccount.ipynb 3
from domolibrary.routes.account import (
    ShareAccount_V1_AccessLevel,
    ShareAccount_V2_AccessLevel,
    ShareAccount,
    GetAccount_NoMatch,
    AccountConfig_InvalidDataProvider,
)

# %% ../../nbs/classes/50_DomoAccount.ipynb 4
import asyncio

from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import datetime as dt
import re


import httpx

from fastcore.basics import patch_to

import domolibrary.utils.convert as cd
import domolibrary.utils.DictDot as util_dd
import domolibrary.client.DomoAuth as dmda
import domolibrary.client.DomoError as de
import domolibrary.routes.account as account_routes

# %% ../../nbs/classes/50_DomoAccount.ipynb 6
class DomoAccount_Config(ABC):
    """DomoAccount Config abstract base class"""

    data_provider_type: str

    @classmethod
    @abstractmethod
    def _from_json(cls, obj):
        """convert accounts API response into a class object"""
        pass

    @abstractmethod
    def to_json(self):
        """convert class object into a format the accounts API expects"""
        pass

# %% ../../nbs/classes/50_DomoAccount.ipynb 8
@dataclass
class DomoAccount_Config_AbstractCredential(DomoAccount_Config):
    data_provider_type = "abstract-credential-store"
    credentials: dict

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            credentials=dd.credentials,
        )

    def to_json(self):
        return {"credentials": self.credentials}

# %% ../../nbs/classes/50_DomoAccount.ipynb 9
@dataclass
class DomoAccount_Config_DatasetCopy(DomoAccount_Config):
    domo_instance: str
    access_token: str = field(repr=False)

    data_provider_type = "dataset-copy"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(access_token=dd.accessToken, domo_instance=dd.instance)

    def to_json(self):
        return {"accessToken": self.access_token, "instance": self.domo_instance}


@dataclass
class DomoAccount_Config_DomoAccessToken(DomoAccount_Config):
    data_provider_type = "domo-access-token"

    domo_access_token: str = field(repr=False, default=None)
    username: str = None
    password: str = field(repr=False, default=None)

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            domo_access_token=dd.domoAccessToken,
            username=dd.username,
            password=dd.password,
        )

    def to_json(self):
        return {
            "domoAccessToken": self.domo_access_token,
            "username": self.username,
            "password": self.password,
        }

# %% ../../nbs/classes/50_DomoAccount.ipynb 10
@dataclass
class DomoAccount_Config_Governance(DomoAccount_Config):
    domo_instance: str
    access_token: str = field(repr=False)

    data_provider_type = "domo-governance-d14c2fef-49a8-4898-8ddd-f64998005600"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(access_token=dd.apikey, domo_instance=dd.customer)

    def to_json(self):
        return {"apikey": self.access_token, "customer": self.domo_instance}

# %% ../../nbs/classes/50_DomoAccount.ipynb 12
@dataclass
class DomoAccount_Config_AmazonS3(DomoAccount_Config):
    access_key: str
    secret_key: str = field(repr=False)
    bucket: str
    region: str = "us-west-2"
    data_provider_type = "amazon-s3"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            access_key=dd.accessKey,
            secret_key=dd.secretKey,
            bucket=dd.bucket,
            region=dd.region,
        )

    def to_json(self):
        if self.bucket.lower().startswith("s3://"):
            bucket = self.bucket[5:]
            print(
                f"🤦‍♀️- Domo bucket expects string without s3:// prefix. Trimming to '{bucket}' for the output"
            )
        return {
            "accessKey": self.access_key,
            "secretKey": self.secret_key,
            "bucket": bucket,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount.ipynb 13
@dataclass
class DomoAccount_Config_AmazonS3Advanced(DomoAccount_Config):
    access_key: str
    secret_key: str = field(repr=False)
    bucket: str
    region: str = "us-west-2"
    data_provider_type = "amazons3-advanced"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            access_key=dd.accessKey,
            secret_key=dd.secretKey,
            bucket=dd.bucket,
            region=dd.region,
        )

    def to_json(self):
        if self.bucket.lower().startswith("s3://"):
            bucket = self.bucket[5:]
            print(
                f"🤦‍♀️- Domo bucket expects string without s3:// prefix. Trimming to '{bucket}' for the output"
            )
        return {
            "accessKey": self.access_key,
            "secretKey": self.secret_key,
            "bucket": bucket,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount.ipynb 14
@dataclass
class DomoAccount_Config_AwsAthena(DomoAccount_Config):
    aws_access_key: str
    aws_secret_key: str = field(repr=False)
    s3_staging_dir: str
    workgroup: str

    region: str = "us-west-2"
    data_provider_type = "aws-athena"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            aws_access_key=dd.awsAccessKey,
            aws_secret_key=dd.awsSecretKey,
            s3_staging_dir=dd.s3StagingDir,
            region=dd.region,
            workgroup=dd.workgroup,
        )

    def to_json(self):
        return {
            "awsAccessKey": self.aws_access_key,
            "awsSecretKey": self.aws_secret_key,
            "s3StagingDir": self.s3_staging_dir,
            "region": self.region,
            "workgroup": self.workgroup,
        }

# %% ../../nbs/classes/50_DomoAccount.ipynb 15
@dataclass
class DomoAccount_Config_HighBandwidthConnector(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    aws_access_key: str
    aws_secret_key: str = field(repr=False)
    s3_staging_dir: str

    region: str = "us-west-2"
    data_provider_type = "amazon-athena-high-bandwidth"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            aws_access_key=dd.awsAccessKey,
            aws_secret_key=dd.awsSecretKey,
            s3_staging_dir=dd.s3StagingDir,
            region=dd.region,
        )

    def to_json(self):
        return {
            "awsAccessKey": self.aws_access_key,
            "awsSecretKey": self.aws_secret_key,
            "s3StagingDir": self.s3_staging_dir,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount.ipynb 18
class AccountConfig(Enum):
    """
    Enum provides appropriate spelling for data_provider_type and config object.
    The name of the enum should correspond with the data_provider_type with hyphens replaced with underscores.
    """

    abstract_credential_store = DomoAccount_Config_AbstractCredential

    dataset_copy = DomoAccount_Config_DatasetCopy

    domo_access_token = DomoAccount_Config_DomoAccessToken
    domo_governance_d14c2fef_49a8_4898_8ddd_f64998005600 = DomoAccount_Config_Governance

    aws_athena = DomoAccount_Config_AwsAthena
    amazon_athena_high_bandwidth = DomoAccount_Config_HighBandwidthConnector

    amazon_s3 = DomoAccount_Config_AmazonS3
    amazons3_advanced = DomoAccount_Config_AmazonS3Advanced

# %% ../../nbs/classes/50_DomoAccount.ipynb 20
@dataclass
class DomoAccount:
    name: str
    data_provider_type: str

    id: int = None
    created_dt: dt.datetime = None
    modified_dt: dt.datetime = None
    auth: dmda.DomoAuth = field(repr=False, default=None)

    config: DomoAccount_Config = None

    @classmethod
    def _from_json(cls, obj: dict, auth: dmda.DomoAuth = None):
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
        )

# %% ../../nbs/classes/50_DomoAccount.ipynb 22
class DomoAccount_DataProviderType_ConfigNotDefined(de.DomoError):
    def __init__(
        self, account_id, data_provider_type, domo_instance, function_name="_get_config"
    ):
        message = f"ℹ️ data provider type {data_provider_type} for account_id {account_id} not defined yet.  Extend the AccountConfig class"

        super().__init__(
            message=message, function_name=function_name, domo_instance=domo_instance
        )


@patch_to(DomoAccount)
async def _get_config(
    self: DomoAccount,
    session=None,
    return_raw: bool = False,
    debug_api: bool = None,
    debug_prn: bool = False,
):
    res_config = await account_routes.get_account_config(
        auth=self.auth,
        account_id=self.id,
        data_provider_type=self.data_provider_type,
        session=session,
        debug_api=debug_api,
    )

    if return_raw:
        return res_config

    enum_clean = re.sub("-", "_", self.data_provider_type)

    if debug_prn:
        print(
            f"retrieving config for {self.id} - {self.name} with {res_config.response}"
        )

    if not enum_clean in AccountConfig.__members__:
        raise DomoAccount_DataProviderType_ConfigNotDefined(
            account_id=self.id,
            data_provider_type=self.data_provider_type,
            domo_instance=self.auth.domo_instance,
            function_name="_get_config",
        )

    self.config = AccountConfig[enum_clean].value._from_json(res_config.response)

    return self.config

# %% ../../nbs/classes/50_DomoAccount.ipynb 23
@patch_to(DomoAccount, cls_method=True)
async def get_by_id(
    cls,
    auth: dmda.DomoAuth,
    account_id: int,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
    debug_api: bool = False,
    debug_prn: bool = False,
):
    """retrieves account metadata and attempts to retrieve config"""

    res = await account_routes.get_account_from_id(
        auth=auth, account_id=account_id, session=session, debug_api=debug_api
    )

    if return_raw:
        return res

    if not res.is_success:
        return None

    obj = res.response
    acc = cls._from_json(obj, auth)

    try:
        await acc._get_config(session=session, debug_api=debug_api, debug_prn=debug_prn)

    except DomoAccount_DataProviderType_ConfigNotDefined as e:
        print(e)

    # except Exception as e:
    #     print(e)

    finally:
        return acc

# %% ../../nbs/classes/50_DomoAccount.ipynb 28
class DomoAccount_CreateAccount_Error(de.DomoError):
    def __init__(
        self,
        entity_id,
        domo_instance,
        status,
        message,
        function_name="create_account",
    ):
        super().__init__(
            function_name=function_name,
            entity_id=entity_id,
            domo_instance=domo_instance,
            status=status,
            message=message,
        )


@patch_to(DomoAccount, cls_method=True)
def generate_create_body(cls, account_name, config):
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

    if not res.is_success:
        raise DomoAccount_CreateAccount_Error(
            entity_id=account_name,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
        )

    return await cls.get_by_id(auth=auth, account_id=res.response.get("id"))

# %% ../../nbs/classes/50_DomoAccount.ipynb 30
class DomoAccount_UpdateError(de.DomoError):
    def __init__(
        self,
        domo_instance,
        status,
        message,
        entity_id,
        function_name="update_name",
    ):
        super().__init__(
            function_name=function_name,
            entity_id=entity_id,
            domo_instance=domo_instance,
            status=status,
            message=message,
        )

@patch_to(DomoAccount)
async def update_config(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    config: DomoAccount_Config = None,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth

    config = config or self.config

    res = await account_routes.update_account_config(
        auth=auth,
        account_id=self.id,
        data_provider_type=self.data_provider_type,
        config_body=config.to_json(),
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res
    
    if not res.is_success:
        raise DomoAccount_UpdateError(
            entity_id=self.id,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
            function_name = 'DomoAccount.update_config'
        )

    await self._get_config(session=session, debug_api=debug_api)

    return self

# %% ../../nbs/classes/50_DomoAccount.ipynb 33
@patch_to(DomoAccount)
async def update_name(
    self: DomoAccount,
    account_name: str = None,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    auth = auth or self.auth

    # print(auth, self.id, self.data_provider_type, self.config.to_json())

    res = await account_routes.update_account_name(
        auth=auth,
        account_id=self.id,
        account_name=account_name or self.name,
        debug_api=debug_api,
        session=session,
    )

    if return_raw:
        return res

    if not res.is_success:
        raise DomoAccount_UpdateError(
            entity_id=self.id,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
            function_name = 'DomoAccount.update_name'
        )

    self = await self.get_by_id(auth=auth, account_id=self.id)

    return self

# %% ../../nbs/classes/50_DomoAccount.ipynb 37
class DomoAccount_DeleteAccount_Error(de.DomoError):
    def __init__(
        self,
        entity_id,
        domo_instance,
        status,
        message,
        function_name="delete_account",
    ):
        super().__init__(
            function_name=function_name,
            entity_id=entity_id,
            domo_instance=domo_instance,
            status=status,
            message=message,
        )


@patch_to(DomoAccount)
async def delete_account(
    self: DomoAccount,
    auth: dmda.DomoAuth = None,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    res = await account_routes.delete_account(
        auth=auth, account_id=self.id, debug_api=debug_api, session=session
    )

    if not res.is_success:
        raise DomoAccount_DeleteAccount_Error(
            entity_id=self.id,
            domo_instance=auth.domo_instance,
            status=res.status,
            message=res.response,
        )

    return True

# %% ../../nbs/classes/50_DomoAccount.ipynb 39
@patch_to(DomoAccount)
async def _is_group_ownership_beta(self, auth: dmda.DomoAuth):
    import domolibrary.classes.DomoBootstrap as dmbs

    domo_bsr = dmbs.DomoBootstrap(auth=auth or self.auth)

    domo_feature_ls = await domo_bsr.get_features()

    match_accounts_v2 = next(
        (
            domo_feature
            for domo_feature in domo_feature_ls
            if domo_feature.name == "accounts-v2"
        ),
        None,
    )

    return True if match_accounts_v2 else False


class ShareAccount_Error(de.DomoError):
    def __init__(self, domo_instance, status, response):
        super().__init__(status=status, message=response, domo_instance=domo_instance)


@patch_to(DomoAccount)
async def share_account(
    self,
    user_id: int = None,
    group_id: int = None,
    domo_user=None,  # DomoUser,
    domo_group=None,  # DomoGroup
    auth: dmda.DomoAuth = None,
    is_v2: bool = None,
    access_level: ShareAccount = None,  # will default to Read
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    user_id = user_id or (domo_user and domo_user.id)
    group_id = group_id or (domo_group and domo_group.id)

    if isinstance(auth, dmda.DomoFullAuth) and is_v2 is None:
        is_v2 = await self._is_group_ownership_beta(auth)

    if debug_prn:
        print(
            f"ℹ️ - {auth.domo_instance} - {'is' if is_v2 else 'is not'} v2_group_ownership"
        )

    if is_v2 is None:
        raise Exception(
            """🛑 ERROR must explicitly pass a value for the `is_v2` boolean to share_accounts function.ABC
alternatively, use `dmda.DomoFullAuth` to automatically retrieve the correct setting.ABC
account sharing differs between v1 and v2 of the API."""
        )

        return None

    res = None

    if is_v2:
        share_payload = account_routes.generate_share_account_payload_v2(
            user_id=user_id,
            group_id=group_id,
            access_level=access_level or ShareAccount_V2_AccessLevel.CAN_VIEW,
        )

        res = await account_routes.share_account_v2(
            auth=auth,
            account_id=self.id,
            share_payload=share_payload,
            debug_api=debug_api,
            session=session,
        )

    else:
        share_payload = account_routes.generate_share_account_payload_v1(
            user_id=user_id,
            group_id=group_id,
            access_level=access_level or ShareAccount_V1_AccessLevel.CAN_VIEW,
        )

        res = await account_routes.share_account_v1(
            auth=auth,
            account_id=self.id,
            share_payload=share_payload,
            debug_api=debug_api,
            session=session,
        )

    if res.status == 500 and res.response == "Internal Server Error":
        ShareAccount_Error(domo_instance=auth.domo_instance,
                           status=res.status,
                           response=f'ℹ️ - {res.response} | User may own account.'
                           )

    if not res.is_success:
        ShareAccount_Error(domo_instance=auth.domo_instance,
                           status=res.status, response=res.response)

    if res.status == 200:
        res.response = f"shared {self.id} - {self.name} with {user_id or group_id}"

    return res


# %% ../../nbs/classes/50_DomoAccount.ipynb 42
@patch_to(DomoAccount)
async def share(
    self: DomoAccount,
    domo_user=None,
    domo_group=None,
    auth: dmda.DomoAuth = None,
    is_v2: bool = None,
    access_level: ShareAccount = None,  # will default to Read
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None,
):
    auth = auth or self.auth

    if isinstance(auth, dmda.DomoFullAuth) and is_v2 is None:
        is_v2 = await self._is_group_ownership_beta(auth)

    if debug_prn:
        print(
            f"ℹ️ - {auth.domo_instance} - {'is' if is_v2 else 'is not'} v2_group_ownership"
        )

    if is_v2 is None:
        raise Exception(
            """🛑 ERROR must pass `is_v2` bool to share_accounts function IF NOT passing `dmda.DomoFullAuth`.
the group management v2 API has a different body.  
Alternatively pass a full auth object to auto check the bootstrap.
"""
        )

    res = None

    if is_v2:
        share_payload = account_routes.generate_share_account_payload_v2(
            user_id=domo_user.id if domo_user else None,
            group_id=domo_group.id if domo_group else None,
            access_level=access_level or ShareAccount_V2_AccessLevel.CAN_VIEW,
        )

        res = await account_routes.share_account_v2(
            auth=auth,
            account_id=self.id,
            share_payload=share_payload,
            debug_api=debug_api,
            session=session,
        )

    else:
        share_payload = account_routes.generate_share_account_payload_v1(
            user_id=domo_user.id if domo_user else None,
            group_id=domo_group.id if domo_group else None,
            access_level=access_level or ShareAccount_V1_AccessLevel.CAN_VIEW,
        )

        res = await account_routes.share_account_v1(
            auth=auth,
            account_id=self.id,
            share_payload=share_payload,
            debug_api=debug_api,
            session=session,
        )

    if res.status == 500 and res.response == "Internal Server Error":
        res.response = f'ℹ️ - {res.response + "| User may own account."}'

    if res.status == 200:
        domo_entity = domo_user or domo_group
        res.response = f"shared {self.id} - {self.name} with {domo_entity.id}"

    return res

# %% ../../nbs/classes/50_DomoAccount.ipynb 46
@dataclass
class DomoAccounts:
    auth: dmda.DomoAuth


# %% ../../nbs/classes/50_DomoAccount.ipynb 47
class GetAccounts_NotFound(de.DomoError):
    def __init__(self, account_id, account_name, domo_instance):
        message = f"account {account_id or account_name} not found"
        super().__init__(message, domo_instance)


@patch_to(DomoAccounts, cls_method=True)
async def _get_accounts_accountsapi(
    cls: DomoAccounts,
    auth: dmda.DomoAuth,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
    return_raw: bool = False,
):
    res = await account_routes.get_accounts(
        auth=auth, debug_api=debug_api, session=session
    )

    if return_raw or len(res.response) == 0:
        return res

    return await asyncio.gather(
        *[
            DomoAccount.get_by_id(
                account_id=json_obj.get("id"),
                debug_api=debug_api,
                session=session,
                auth=auth,
            )
            for json_obj in res.response
        ]
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

    if return_raw or len(res.response) == 0:
        return res

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
    account_name: str = None,
    account_id: str = None,
    account_type: AccountConfig = None,  # to retrieve a specific account type
    account_type_str = None,
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
        domo_account = next((domo_account for domo_account in domo_accounts if int(domo_account.id) == int(account_id)), None)

        if not domo_account:
            raise GetAccount_NoMatch(
                account_id=account_id, domo_instance=auth.domo_instance)
                
        return domo_account

    if account_name and isinstance(account_name, str):
        domo_accounts = [ domo_account for domo_account in domo_accounts if domo_account.name.lower() == account_name.lower()]

    if account_type:
        return [
            domo_account
            for domo_account in domo_accounts
            if domo_account.data_provider_type == account_type.value.data_provider_type ]
    
    if account_type_str:
        return [
            domo_account
            for domo_account in domo_accounts
            if domo_account.data_provider_type == account_type_str ]
   
    return domo_accounts


# %% ../../nbs/classes/50_DomoAccount.ipynb 54
class UpsertAccount_MatchCriteria(de.DomoError):
    def __init__(self, domo_instance):
        super().__init__(message="must pass an account_id or account_name to UPSERT",
                         domo_instance=domo_instance)


@patch_to(DomoAccounts, cls_method=True)
async def upsert_account(
    cls: DomoAccounts,
    auth: dmda.DomoAuth,

    account_config: AccountConfig = None, 
    account_name: str = None,
    account_id: str = None,
    debug_api: bool = False,
    debug_prn: bool = False,
    session: httpx.AsyncClient = None
):
    """search for an account and upsert it"""

    if not account_name and not account_id:
        raise UpsertAccount_MatchCriteria(domo_instance=auth.domo_instance)

    acc = None

    if account_id and acc is None:
        acc = await DomoAccounts.get_accounts(account_id=account_id, auth=auth)

        if acc and account_name:
            await acc.update_name(account_name=account_name, debug_api = debug_api)

    if account_name and acc is None:
        acc = await DomoAccounts.get_accounts(
            account_name=account_name, auth=auth,
            account_type_str= (account_config and account_config.data_provider_type) or None
        )

        if (
            isinstance(acc, list)
            and len(acc) > 0
            and isinstance(acc[0], DomoAccount)
        ):
            acc = acc[0]

        else:
            acc = None

    if debug_prn: 
        print(f"match to {acc} for upsert in {auth.domo_instance}")

    if acc and account_config:  # upsert account
        acc.config = account_config

        if debug_prn:
            print(f"upsertting config {acc.config}")

        await acc.update_config( debug_api = debug_api)

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

