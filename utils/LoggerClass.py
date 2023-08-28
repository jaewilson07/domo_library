from ..DomoClasses.DomoAuth import DomoDeveloperAuth, DomoFullAuth
import aiohttp
import asyncio
import Library.DomoClasses.DomoDataset as dmds
import pandas as pd
from datetime import datetime
import traceback


class MyLogger:
    app_name : str = ''
    output_ds : str = ''
    instance_auth : DomoFullAuth = None
    logs_df : pd.DataFrame = pd.DataFrame()
    breadcrumbs : list = []
    
    def __init__(self, app_name, output_ds, instance_auth):
        self.app_name = app_name
        self.output_ds = output_ds
        self.instance_auth = instance_auth
        breadcrumbs = []
        logs_df = pd.DataFrame()
        
    def add_crumb(self, crumb):
        if crumb not in self.breadcrumbs:
            self.breadcrumbs.append(crumb)
        
    def remove_crumb(self, crumb):
        if crumb in self.breadcrumbs:
            self.breadcrumbs.remove(crumb)

    def log_info(self, message, is_print = True):
        self.__AddLog(message = message,
                      type_str = "Info", 
                     is_print=is_print)

    def log_error(self, message, is_print = True):
        self.__AddLog(message = message,
                      type_str = "Error", 
                     is_print=is_print)

    def log_warning(self, message, is_print = True):
        self.__AddLog(message = message,
                      type_str = "Warning", 
                     is_print=is_print)


    def __AddLog(self, message: str, type_str : str, is_print = True):
        traceback_ls = []
        
        for line in traceback.format_stack():
            if not line.strip().startswith('File "/home/domo/.conda'):
                traceback_ls.append(line.strip())
        
        new_row = pd.DataFrame({'date_time':datetime.now(), 'application':self.app_name, 'type':type_str, 'message': message, 'breadcrumbs': None if self.breadcrumbs is None else '->'.join(self.breadcrumbs), 'traceback':None if traceback_ls is None else ' '.join(traceback_ls)}, index=[0])
        if is_print:
            print (message)
        self.logs_df = pd.concat([new_row,self.logs_df.loc[:]]).reset_index(drop=True)
    
    async def write_logs (self, upload_method: str = 'APPEND'):
        dataset = dmds.DomoDataset(full_auth = self.instance_auth,
                                    id = self.output_ds)
        await dataset.upload_csv(upload_df = self.logs_df,upload_method = upload_method)
        await asyncio.sleep(10)
        await dataset.index_dataset()
        #remove all rows
        self.logs_df = self.logs_df.head(0)
        print ('sucess, logs are saved')

