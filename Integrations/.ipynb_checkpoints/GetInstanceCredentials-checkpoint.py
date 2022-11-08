from dataclasses import dataclass, field

import pandas as pd
import importlib
import datetime as dt

import Library.DomoClasses.DomoAuth as dmda

class Error(Exception):
    """Base class for other exceptions"""
    pass

class InvalidAccountTypeError(Error):
    """raised when account type is not abstract credentials"""
    pass

class InvalidAccountNameError(Error):
    """raised when account name does not follow format string"""

    def __init__(self, account_name= None, regex_pattern=None):
        account_str = f'"{account_name}" '
        regex_str = f'"{regex_pattern}"'
        
        message = f"string {account_str if account_name else ''}does not match regex pattern {regex_str or ''}"
        self.message = message
        
        super().__init__(self.message)
    
class NoInstanceError(Error):
    """ raised when required domo_instance argument has not been supplied"""
    def __init__(self):
        self.message = "must pass a domo_instance argument"
        super().__init__(self.message)
    
class NoConfigCompanyError(Error):
    def __init__(self, sql):
        message = f'SQL "{sql}" returned no results'
        self.message = message
        super().__init__(self.message)



@dataclass
class DomoInstanceAuth:
    account_name: str 
    
    domo_username : str = None
    display_name: str = field(repr = False, default = None)
    
    domo_instance : str = field(repr = False, default = None)
    domo_instance_ls : list = field(repr= False, default = None)

    raw_cred : dict = field(repr = False, default = None)
    domo_password : str = field(repr = False, default = None)
    
    full_auth_ls : list = field(repr = False, default = None)
    
    account_name_mask = '^dj_.*_acc'
    
    def __post_init__(self):
        import re
        if not self.display_name:
            clean_text = re.sub('@.*$', '', self.domo_username)
            
            self.display_name = clean_text

        
    
    @staticmethod
    def _test_regex_mask(test_string, regex_mask )-> bool:
        """tests if a string matches the regex pattern
        
        :param str test_string: the string to test
        :param str regex_mask : the regex expression to test
        :return: boolean result of re match
        """        
        import re
        
        return bool(re.match(regex_mask , test_string))
    
    @staticmethod
    def _clean_account_str(account_name):
        import re 
        
        clean_str = re.sub('^dj_', '', account_name)
        clean_str = re.sub('_acc$', '', clean_str)
        
        return clean_str
        
        
    @classmethod
    def get_domo_account(cls, account_name, domo_instance = None):
        import json
        import domojupyter as dj

        if not cls._test_regex_mask(account_name, cls.account_name_mask):
            raise InvalidAccountNameError(account_name, cls.account_name_mask)

        if dj.get_account_property_keys(account_name) != ['credentials']:
            raise InvalidAccountTypeError
        
        creds = json.loads(dj.get_account_property_value(account_name, 'credentials'))
        
        return cls(
            account_name = account_name,
            raw_cred = creds,
            domo_username = creds.get('DOMO_USERNAME'),
            domo_password = creds.get('DOMO_PASSWORD'),
            domo_instance = creds.get('DOMO_INSTANCE')
        )
        
    def generate_full_auth_ls(self,
                              domo_instance_ls : list = None):
        
        import Library.DomoClasses.DomoAuth as dmda
        
        self.full_auth_ls = None
        self.domo_instance = None
        
        self.domo_instance_ls =  list(set(domo_instance_ls or self.domo_instance_ls))
        
        if not self.domo_instance_ls:
            return None
        
        for domo_instance in self.domo_instance_ls:
            full_auth = dmda.DomoFullAuth(domo_instance = domo_instance, 
                                          domo_username = self.domo_username, 
                                          domo_password = self.domo_password)
            if self.full_auth_ls is None:
                self.full_auth_ls = [full_auth]
            else:
                self.full_auth_ls.append(full_auth)
        return self.full_auth_ls
                
    def generate_full_auth(self,
                           domo_instance : str = None):        
        import Library.DomoClasses.DomoAuth as dmda
        
        self.full_auth_ls = None
        self.domo_instance_ls = None
        
        self.domo_instance =  domo_instance or self.domo_instance
        
        if not self.domo_instance:
            raise NoInstanceError
        
        full_auth = dmda.DomoFullAuth(domo_instance = domo_instance,
                                      domo_username = self.domo_username, 
                                      domo_password = self.domo_password)
        
        self.full_auth_ls = [full_auth]
        
        return full_auth
    
    def generate_user(self, display_name : str = None) -> dict:
        return {
            'domo_username' : self.domo_username,
            'domo_password' : self.domo_password ,
            'display_name' : display_name or self.display_name}

async def get_domains_with_global_config_auth(config_auth: dmda.DomoFullAuth,
                                              dataset_id: str,
                                              global_auth : dmda.DomoFullAuth,
                                              exception_auth : dmda.DomoFullAuth,
                                              sql: str = "select domain from table",
                                              debug: bool = False) -> pd.DataFrame:
    
    import Library.DomoClasses.DomoDataset as dmds
    
    ds = await dmds.DomoDataset.get_from_id(full_auth=config_auth,
                                            id=dataset_id, debug=debug)

    print(f"⚙️ START - Retrieving company list \n{ds.display_url()}")
    print(f"⚙️ SQL = {sql}")

    df = await ds.query_dataset_private(full_auth=config_auth,
                                        dataset_id=dataset_id,
                                        sql=sql,
                                        debug=debug)
    if len(df.index) == 0:
        raise NoConfigCompanyError(sql)
        
    print(f"\n⚙️ SUCCESS 🎉 Retrieved company list \nThere are {len(df.index)} companies to update")
    
    for index, instance in df.iterrows():
        creds = global_auth 

        if instance['config_exception_pw'] == 1 :
            creds = exception_auth

        full_auth = dmda.DomoFullAuth(domo_instance = instance['domo_instance'],
                                  domo_username = creds.domo_username,
                                  domo_password = creds.domo_password)
        try:
            await full_auth.get_auth_token(debug = False)
        
        except dmda.InvalidCredentialsError as e:
            print(e)
        
        df.at[index, 'instance_auth'] = full_auth
        df.at[index, 'is_valid'] = 1 if (full_auth.token) else 0
    
    return df

async def get_domains_with_instance_auth(config_auth: dmda.DomoFullAuth,
                                         dataset_id: str,
                                         pa_auth,
                                         pa_test_auth,
                                         other_auth,
                                         other_test_auth,
                                         sql: str = "select domain from table",
                                         debug: bool = False
                                        ) -> pd.DataFrame:
    
    import Library.DomoClasses.DomoDataset as dmds
    
    ds = await dmds.DomoDataset.get_from_id(full_auth=config_auth,
                                            id=dataset_id, debug=debug)

    print(f"⚙️ START - Retrieving company list \n{ds.display_url()}")
    print(f"⚙️ SQL = {sql}")

    df = await ds.query_dataset_private(full_auth=config_auth,
                                        dataset_id=dataset_id,
                                        sql=sql,
                                        debug=debug)
    if len(df.index) == 0:
        raise NoConfigCompanyError(sql)
        
    print(f"\n⚙️ SUCCESS 🎉 Retrieved company list \nThere are {len(df.index)} companies to update")
    
    for index, instance in df.iterrows():
        creds = other_auth 

        if instance['project'] == 'pa' and instance['config_useprod'] == 1:
            creds = pa_auth
        elif instance['project'] == 'pa' and instance['config_useprod'] == 0:
            creds = pa_test_auth     
        elif instance['project'] == 'other' and instance['config_useprod'] == 0:
            creds = other_test_auth

        full_auth = dmda.DomoFullAuth(domo_instance = instance['domo_instance'],
                                  domo_username = creds.domo_username,
                                  domo_password = creds.domo_password,
                                      token_name = 'instance'
                                     )
        try:
            await full_auth.get_auth_token(debug = False)
        
        except dmda.InvalidCredentialsError as e:
            print(e)
        
        df.at[index, 'instance_auth'] = full_auth
        df.at[index, 'is_valid'] = 1 if (full_auth.token) else 0
    
    return df
