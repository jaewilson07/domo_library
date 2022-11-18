from dataclasses import dataclass, field
from enum import Enum
import datetime as dt
import aiohttp

import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.routes.account_routes as account_routes

import importlib
importlib.reload(account_routes)

import Library.utils.DictDot as dcd



@dataclass
class DomoAccount_Config_HighBandwidthConnector:
    aws_access_key :str
    aws_secret_key: str
    s3_staging_dir : str
    region:str = 'us-west-2'
    
    @classmethod
    def _from_json(cls, obj):
        dd = dcd.DictDot(obj)
        
        return cls(
            aws_access_key = dd.awsAccessKey,
            aws_secret_key = dd.awsSecretKey,
            s3_staging_dir = dd.s3StagingDir,
            region = dd.region
        )
    
    def to_json(self):
        return { "awsAccessKey": self.aws_access_key,
                 "awsSecretKey": self.aws_secret_key,
                 "s3StagingDir": self.s3_staging_dir,
                 "region": self.region}

class AccountConfig(Enum):
    amazon_athena_high_bandwidth = DomoAccount_Config_HighBandwidthConnector
    
@dataclass
class DomoAccount:
    id : int
    name : str
    data_provider_type: str
    created_dt : dt.datetime
    modified_dt: dt.datetime
    full_auth: dmda.DomoFullAuth  = field(repr = False, default = None)
    
    config :  AccountConfig  = None
    
    
    @classmethod
    def _from_json(cls, obj: dict, full_auth:dmda.DomoFullAuth = None):
        import Library.utils.convert as cd
        
        dd = dcd.DictDot(obj)
        
        return cls(id = dd.id,
            name = dd.name,
            data_provider_type = dd.dataProviderType,
            created_dt = cd.convert_epoch_millisecond_to_datetime(dd.createdAt),
            modified_dt = cd.convert_epoch_millisecond_to_datetime(dd.modifiedAt),
                  full_auth = full_auth)
            
    
    @classmethod
    async def get_from_id(cls, full_auth :dmda.DomoFullAuth, account_id:int, session: aiohttp.ClientSession = None):
        res = await account_routes.get_account_from_id(full_auth = full_auth, account_id = account_id,
                                                       session = session
                                                      )
        
        import re
        
        if res.status != 200 :
            return None
        
        obj = res.response
        acc =  cls._from_json(obj, full_auth)
        
        res_config = await account_routes.get_account_config(full_auth = full_auth,
                                                             account_id = acc.id,
                                                             data_provider_type = acc.data_provider_type,
                                                             session = session)
        
        if res_config.status != 200:
            return acc
        
        enum_clean = re.sub("-", '_', acc.data_provider_type)
        
        
        account_config_names = [member.name for member in AccountConfig]
        
        if enum_clean not in account_config_names:
            return acc
        
        acc.config = AccountConfig[enum_clean].value._from_json(res_config.response)
        
        return acc
    
    
    async def update_config(self, 
                            full_auth: dmda.DomoFullAuth = None, 
                            debug:bool = False, log_results:bool = False, session : aiohttp.ClientSession = None):
        
        full_auth = full_auth or self.full_auth
        
        print(full_auth,self.id,self.data_provider_type,self.config.to_json())
        
        res = await account_routes.update_account_config(full_auth = full_auth,
                                                         account_id = self.id,
                                                         data_provider_type = self.data_provider_type,
                                                         config_body = self.config.to_json(),
                                                         debug=debug, log_results = log_results, session = session)
        
        return res.response
                                                         
                                                        
  