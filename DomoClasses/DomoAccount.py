import datetime as dt
import importlib
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.routes.account_routes as account_routes
import Library.utils.DictDot as dcd

importlib.reload(account_routes)


@dataclass
class DomoAccount_Config_HighBandwidthConnector:
    aws_access_key: str
    aws_secret_key: str = field(repr = False)
    s3_staging_dir: str
    region: str = 'us-west-2'
    data_provider_type = 'amazon-athena-high-bandwidth'

    @classmethod
    def _from_json(cls, obj):

        dd = dcd.DictDot(obj)

        return cls(
            aws_access_key=dd.awsAccessKey,
            aws_secret_key=dd.awsSecretKey,
            s3_staging_dir=dd.s3StagingDir,
            region=dd.region
        )

    def to_json(self):
        return {"awsAccessKey": self.aws_access_key,
                "awsSecretKey": self.aws_secret_key,
                "s3StagingDir": self.s3_staging_dir,
                "region": self.region
                }


@dataclass
class DomoAccount_Config_AbstractCredential:
    credentials: dict

    @classmethod
    def _from_json(cls, obj):

        dd = dcd.DictDot(obj)

        return cls(
            credentials=dd.credentials,
        )

    def to_json(self):
        return {"credentials": self.credentials
                }


class AccountConfig(Enum):
    amazon_athena_high_bandwidth = {'type': 'amazon-athena-high-bandwidth',
                                    'config': DomoAccount_Config_HighBandwidthConnector}

    abstract_credential_store = {'type': 'abstract-credential-store',
                                 'config': DomoAccount_Config_AbstractCredential}


@dataclass
class DomoAccount:
    name: str
    data_provider_type: str
    id: int = None
    created_dt: dt.datetime = None
    modified_dt: dt.datetime = None
    full_auth: dmda.DomoFullAuth = field(repr=False, default=None)

    config:  AccountConfig = None

    @classmethod
    def _from_json(cls, obj: dict, full_auth: dmda.DomoFullAuth = None):
        import Library.utils.convert as cd

        dd = dcd.DictDot(obj)

        return cls(id=dd.id,
                   name=dd.displayName,
                   data_provider_type=dd.dataProviderType,
                   created_dt=cd.convert_epoch_millisecond_to_datetime(
                       dd.createdAt),
                   modified_dt=cd.convert_epoch_millisecond_to_datetime(
                       dd.modifiedAt),
                   full_auth=full_auth)

    @classmethod
    async def get_from_id(cls, full_auth: dmda.DomoFullAuth, account_id: int, session: aiohttp.ClientSession = None):
        res = await account_routes.get_account_from_id(full_auth=full_auth, account_id=account_id,
                                                       session=session
                                                       )

        import re

        if res.status != 200:
            return None

        obj = res.response
        acc = cls._from_json(obj, full_auth)

        res_config = await account_routes.get_account_config(full_auth=full_auth,
                                                             account_id=acc.id,
                                                             data_provider_type=acc.data_provider_type,
                                                             session=session)

        if res_config.status != 200:
            return acc

        enum_clean = re.sub("-", '_', acc.data_provider_type)

        account_config_names = [member.name for member in AccountConfig]

        if enum_clean not in account_config_names:
            return acc

        acc.config = AccountConfig[enum_clean].value.get('config')._from_json(
            res_config.response
        )

        return acc

    async def update_config(self,
                            full_auth: dmda.DomoFullAuth = None,
                            debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

        full_auth = full_auth or self.full_auth

        # print(full_auth, self.id, self.data_provider_type, self.config.to_json())

        res = await account_routes.update_account_config(full_auth=full_auth,
                                                         account_id=self.id,
                                                         data_provider_type=self.data_provider_type,
                                                         config_body=self.config.to_json(),
                                                         debug=debug, log_results=log_results, session=session)

        obj = res.response
        acc = await self.get_from_id(full_auth=full_auth, account_id=obj.get('id'))
        acc.status = res.status
        acc.is_success = res.is_success

        return acc

    async def update_name(self,
                          account_name: str = None,
                          full_auth: dmda.DomoFullAuth = None,
                          debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):

        full_auth = full_auth or self.full_auth

        # print(full_auth, self.id, self.data_provider_type, self.config.to_json())

        res = await account_routes.update_account_name(full_auth=full_auth,
                                                       account_id=self.id,
                                                       account_name=account_name or self.name,
                                                       debug=debug, log_results=log_results, session=session)

        obj = res.response
        acc = await self.get_from_id(full_auth=full_auth, account_id=obj.get('id'))
        acc.status = res.status
        acc.is_success = res.is_success

        return acc

    def config_to_json(self):
        obj = {'displayName': self.name,
               'dataProviderType': self.data_provider_type,
               'name': self.data_provider_type,
               'configurations': self.config.to_json()}

        return obj

    async def create_account(self,
                             full_auth: dmda.DomoFullAuth = None,
                             #  config_body: dict,
                             debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):
        
        full_auth = full_auth or self.full_auth

        res = await account_routes.create_account(full_auth=full_auth,
                                                  config_body=self.config_to_json(),
                                                  debug=debug, log_results=log_results, session=session)

        if debug:
            print(res)
            
        if res.status != 200:
            return False

        obj = res.response
        acc = await self.get_from_id(full_auth=full_auth, account_id=obj.get('id'))
        acc.status = res.status
        acc.is_success = res.is_success
        return acc
    
    async def delete_account(self,
                             full_auth: dmda.DomoFullAuth = None,
                             #  config_body: dict,
                             debug: bool = False, log_results: bool = False, session: aiohttp.ClientSession = None):
        full_auth = full_auth or self.full_auth

        res = await account_routes.delete_account(full_auth=full_auth,
                                                  account_id = self.id,
                                                  debug=debug, log_results=log_results, session=session)

        if debug:
            print(res)
            
        if res.status != 200:
            return False

        return True
    
    async def share_account(self, 
                            full_auth : dmda.DomoFullAuth,
                            user_id: int,
                            is_v2: bool = False,
                            access_level: str = 'CAN_VIEW', # for v2 account_sharing beta CAN_VIEW, CAN_EDIT, CAN_SHARE
                            debug: bool = False,
                            log_results :bool = False,
                            session : aiohttp.ClientSession = None ):
        
        

        if is_v2:
            share_payload = account_routes.generate_share_account_payload_v2(user_id = user_id,
                                                                          access_level = access_level)
            return await account_routes.share_account_v2(full_auth = full_auth,
                                                  account_id = self.id,
                                                  share_payload = share_payload,
                                                  debug = debug, 
                                                  log_results = log_results,
                                                  session = session                                           
                                                 )
        
        share_payload = account_routes.generate_share_account_payload_v1(user_id = user_id)
        return await account_routes.share_account_v1(full_auth = full_auth,
                                                  account_id = self.id,
                                                  share_payload = share_payload,
                                                  debug = debug, 
                                                  log_results = log_results,
                                                  session = session                                           
                                                 )
        