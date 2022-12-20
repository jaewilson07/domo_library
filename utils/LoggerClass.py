from ..DomoClasses.DomoAuth import DomoDeveloperAuth, DomoFullAuth
import aiohttp
import asyncio
import Library.DomoClasses.DomoDataset as dmds
import pandas as pd
from datetime import datetime



class MyLogger:
    app_name : str = ''
    output_ds : str = ''
    instance_auth : DomoFullAuth = None
    logs_df : pd.DataFrame = pd.DataFrame()
    
    def __init__(self, app_name, output_ds, instance_auth):
        self.app_name = app_name
        self.output_ds = output_ds
        self.instance_auth = instance_auth
        logs_df = pd.DataFrame()

    def log_info(self, message, debug = False):
        self.__AddLog(message = message,
                      type_str = "Info", 
                      debug = debug)

    def log_error(self, message, debug = False):
        self.__AddLog(message = message,
                      type_str = "Error", 
                      debug = debug)

    def log_warning(self, message, debug = False):
        self.__AddLog(message = message,
                      type_str = "Warning", 
                      debug = debug)


    def __AddLog(self, message: str, type_str : str, debug = False):
        new_row = pd.DataFrame({'date_time':datetime.now(), 'application':self.app_name, 'type':type_str, 'message':message}, index=[0])
        if debug:
            print (new_row)
        self.logs_df = pd.concat([new_row,self.logs_df.loc[:]]).reset_index(drop=True)
    
    async def write_logs (self, upload_method: str = 'APPEND'):
        dataset = dmds.DomoDataset(full_auth = self.instance_auth,
                                    id = self.output_ds)
        await dataset.upload_csv(upload_df = self.logs_df,upload_method = upload_method)
        await asyncio.sleep(10)
        await dataset.index_dataset()
        #remove all rows
        self.logs_df = self.logs_df.head(0)
        print ('sucess')

