# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoAccount_Config.ipynb.

# %% auto 0
__all__ = ['DomoAccount_Config', 'AccountConfig_UsesOauth', 'AccountConfig_ProviderTypeNotDefined', 'DomoAccount_NoConfig_OAuth',
           'DomoAccount_NoConfig', 'DomoAccount_Config_AbstractCredential', 'DomoAccount_Config_DatasetCopy',
           'DomoAccount_Config_DomoAccessToken', 'DomoAccount_Config_Governance', 'DomoAccount_Config_AmazonS3',
           'DomoAccount_Config_AmazonS3Advanced', 'DomoAccount_Config_AwsAthena',
           'DomoAccount_Config_HighBandwidthConnector', 'DomoAccount_Config_Snowflake',
           'DomoAccount_Config_SnowflakeUnload_V2', 'DomoAccount_Config_SnowflakeUnloadAdvancedPartition',
           'DomoAccount_Config_SnowflakeWriteback', 'DomoAccount_Config_SnowflakeUnload',
           'DomoAccount_Config_SnowflakeFederated', 'DomoAccount_Config_SnowflakeInternalUnload',
           'DomoAccount_Config_SnowflakeKeyPairAuthentication', 'AccountConfig']

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 3
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import domolibrary.utils.DictDot as util_dd

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 5
class DomoAccount_Config(ABC):
    """DomoAccount Config abstract base class"""

    data_provider_type: str
    is_defined_config: bool = True
    _associated_exception = None

    @classmethod
    @abstractmethod
    def _from_json(cls, obj):
        """convert accounts API response into a class object"""

    @abstractmethod
    def to_json(self):
        """convert class object into a format the accounts API expects"""

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 6
class AccountConfig_UsesOauth(Exception):
    def __init__(self, data_provider_type):
        super().__init__(
            f"data provider type {data_provider_type} uses OAuth and therefore wouldn't return a Config object"
        )


class AccountConfig_ProviderTypeNotDefined(Exception):
    def __init__(self, data_provider_type):
        super().__init__(
            f"data provider type {data_provider_type} not defined yet. Extend the AccountConfig class"
        )


@dataclass
class DomoAccount_NoConfig_OAuth(DomoAccount_Config):
    is_oauth: bool = True
    is_defined_config: bool = False
    _associated_exception = AccountConfig_UsesOauth

    @classmethod
    def _from_json(cls, obj):
        return cls()

    def to_json(self):
        return {}


@dataclass
class DomoAccount_NoConfig(DomoAccount_Config):
    is_defined_config: bool = False
    _associated_exception = AccountConfig_ProviderTypeNotDefined

    @classmethod
    def _from_json(cls, obj):
        return cls()

    def to_json(self):
        return {}

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 8
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

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 9
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

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 10
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

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 12
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
        bucket = self.bucket


        if bucket and bucket.lower().startswith("s3://"):
            bucket = bucket[5:]
            print(
                f"🤦‍♀️- Domo bucket expects string without s3:// prefix. Trimming to '{bucket}' for the output"
            )
        return {
            "accessKey": self.access_key,
            "secretKey": self.secret_key,
            "bucket": bucket,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 13
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
        bucket = self.bucket
        
        if bucket.lower().startswith("s3://"):
            bucket = bucket[5:]
            print(
                f"🤦‍♀️- Domo bucket expects string without s3:// prefix. Trimming to '{bucket}' for the output"
            )
        return {
            "accessKey": self.access_key,
            "secretKey": self.secret_key,
            "bucket": bucket,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 14
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

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 15
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

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 19
@dataclass
class DomoAccount_Config_Snowflake(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    account: str
    username: str
    password: str = field(repr=False)
    role: str = None

    data_provider_type = "snowflake"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            account=dd.account,
            username=dd.username,
            password=dd.password,
            role=dd.role,
        )

    def to_json(self):
        return {
            "account": self.account,
            "username": self.username,
            "password": self.password,
            "role": self.role,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 21
@dataclass
class DomoAccount_Config_SnowflakeUnload_V2(DomoAccount_Config):
    """this connector is not enabled by default contact your CSM / AE"""

    account: str
    username: str
    password: str = field(repr=False)

    access_key: str
    secret_key: str = field(repr=False)
    region: str
    bucket: str

    role: str = None

    data_provider_type = "snowflake-unload-v2"

    @classmethod
    def _from_json(cls, obj):
        dd = util_dd.DictDot(obj)

        return cls(
            account=dd.account,
            username=dd.username,
            password=dd.password,
            access_key=dd.accessKey,
            secret_key=dd.secretKey,
            bucket=dd.bucket,
            region=dd.region,
            role=dd.role,
        )

    def to_json(self):
        return {
            "account": self.account,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "accessKey": self.access_key,
            "secretKey": self.secret_key,
            "bucket": self.bucket,
            "region": self.region,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 23
@dataclass
class DomoAccount_Config_SnowflakeUnloadAdvancedPartition(DomoAccount_Config):
    password: str = field(repr=False)
    account: str
    user_name: str
    role: str = None

    data_provider_type = "snowflake-internal-unload-advanced-partition"

    @classmethod
    def _from_json(cls, obj):
        return cls(
            password=obj["password"],
            role=obj.get("role"),
            account=obj["account"],
            user_name=obj["username"],
        )

    def to_json(self):
        return {
            "password": self.password,
            "role": self.role,
            "account": self.account,
            "username": self.user_name,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 24
@dataclass
class DomoAccount_Config_SnowflakeWriteback(DomoAccount_Config):
    domo_client_secret: str = field(repr=False)
    domo_client_id: str
    account: str
    password: str = field(repr=False)
    user_name: str

    data_provider_type = "snowflake-writeback"

    @classmethod
    def _from_json(cls, obj):
        return cls(
            domo_client_secret=obj["domoClientSecret"],
            domo_client_id=obj["domoClientId"],
            account=obj["account"],
            user_name=obj["username"],
            password=obj["password"],
        )

    def to_json(self):
        return {
            "domoClientSecret": self.domo_client_secret,
            "password": self.password,
            "domoClientId": self.domo_client_id,
            "account": self.account,
            "username": self.user_name,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 25
@dataclass
class DomoAccount_Config_SnowflakeUnload(DomoAccount_Config):
    secret_key: str = field(repr=False)
    access_key: str
    account: str
    password: str = field(repr=False)
    user_name: str
    bucket: str

    data_provider_type = "snowflake-unload"

    @classmethod
    def _from_json(cls, obj):
        return cls(
            secret_key=obj["secretKey"],
            access_key=obj["accessKey"],
            account=obj["account"],
            user_name=obj["username"],
            password=obj["password"],
            bucket=obj["bucket"],
        )

    def to_json(self):
        return {
            "bucket": self.bucket,
            "password": self.password,
            "secretKey": self.secret_key,
            "accessKey": self.access_key,
            "account": self.account,
            "username": self.user_name,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 26
@dataclass
class DomoAccount_Config_SnowflakeFederated(DomoAccount_Config):
    password: str = field(repr=False)
    host: str
    warehouse: str
    user: str
    port: str = None
    role: str = None

    data_provider_type = "snowflake-federated"

    @classmethod
    def _from_json(cls, obj):
        return cls(
            password=obj["password"],
            host=obj["host"],
            warehouse=obj["warehouse"],
            user=obj["user"],
            role=obj.get("role"),
            port=obj.get("port"),
        )

    def to_json(self):
        return {
            "password": self.password,
            "port": self.port,
            "host": self.host,
            "warehouse": self.warehouse,
            "user": self.user,
            "role": self.role,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 27
@dataclass
class DomoAccount_Config_SnowflakeInternalUnload(DomoAccount_Config):
    password: str = field(repr=False)
    account: str
    user_name: str
    role: str = None
    data_provider_type = "snowflake-internal-unload"

    @classmethod
    def _from_json(cls, obj):
        return cls(
            password=obj["password"],
            role=obj.get("role"),
            account=obj["account"],
            user_name=obj["username"],
        )

    def to_json(self):
        return {
            "password": self.password,
            "role": self.role,
            "account": self.account,
            "username": self.user_name,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 28
@dataclass
class DomoAccount_Config_SnowflakeKeyPairAuthentication(DomoAccount_Config):
    private_key: str = field(repr=False)
    account: str = field(repr=False)
    pass_phrase: str = field(repr=False)
    user_name: str
    role: str = None
    data_provider_type = "snowflakekeypairauthentication"

    @classmethod
    def _from_json(cls, obj):
        return cls(
            private_key=obj["privateKey"],
            role=obj.get("role"),
            account=obj["account"],
            user_name=obj["username"],
            pass_phrase=obj["passPhrase"],
        )

    def to_json(self):
        return {
            "privateKey": self.private_key,
            "role": self.role,
            "account": self.account,
            "username": self.user_name,
            "passPhrase": self.pass_phrase,
        }

# %% ../../nbs/classes/50_DomoAccount_Config.ipynb 29
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

    snowflake = DomoAccount_Config_Snowflake

    snowflake_unload = DomoAccount_Config_SnowflakeUnload
    snowflake_unload_v2 = DomoAccount_Config_SnowflakeUnload_V2

    snowflake_internal_unload_advanced_partition = (
        DomoAccount_Config_SnowflakeUnloadAdvancedPartition
    )
    snowflake_internal_unload = DomoAccount_Config_SnowflakeInternalUnload

    snowflakekeypairauthentication = (
        DomoAccount_Config_SnowflakeKeyPairAuthentication,
    )

    snowflake_writeback = DomoAccount_Config_SnowflakeWriteback
    snowflake_federated = DomoAccount_Config_SnowflakeFederated

    _uses_oauth = ["google_spreadsheets"]

    _config_oauth = DomoAccount_NoConfig_OAuth
    _config_notdefined = DomoAccount_NoConfig

    @classmethod
    def _test_altname_search(cls, raw_value):
        alt_search_str = raw_value.lower().replace("-", "_")

        alt_search = next(
            (member for member in cls if member.name == alt_search_str), None
        )

        ## best case scenario alt_search yields a result
        if alt_search:
            return alt_search

        ## second best case, display_type is an oauth and therefore has mo matching config
        oauth_match = next(
            (
                oauth_str
                for oauth_str in cls._uses_oauth.value
                if oauth_str == alt_search_str
            ),
            None,
        )
        if oauth_match:
            raise AccountConfig_UsesOauth(raw_value)

        ## worst case, unencountered display_type
        raise AccountConfig_ProviderTypeNotDefined(raw_value)

    @classmethod
    def _missing_(cls, value):
        try:
            return cls._test_altname_search(value)

        except AccountConfig_UsesOauth as e:
            print(e)
            return cls._config_oauth

        except AccountConfig_ProviderTypeNotDefined as e:
            print(e)
            return cls._config_notdefined
