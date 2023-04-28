# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/integrations/Automation.ipynb.

# %% auto 0
__all__ = []

# %% ../../nbs/integrations/Automation.ipynb 2
import csv
import datetime as DT
import os
from dataclasses import dataclass

import domolibrary.client.DomoAuth as dmda
import domolibrary.classes.DomoInstanceConfig  as dmic
import domolibrary.classes.DomoDataset as dmds


import utils.Exceptions as ex
import pandas as pd


@dataclass
class LogError:
    def __init__(self):
        pass

    function_str: str
    message_str: str
    domo_instance: str


def write_error(file_path, log_err: LogError):
    file_exists = os.path.isfile(file_path)

    with open(file_path, 'a+') as log_file:
        headers = list(log_err.__dict__.keys())
        writer = csv.DictWriter(log_file, fieldnames=headers)

        if not file_exists:
            writer.writeheader()

        writer.writerows([log_err.__dict__])

        


async def get_ip_whitelist_config(auth: dmda.DomoFullAuth,
                                  dataset_id: str,
                                  handle_err_fn: callable,
                                  sql: str = "select addresses from table",
                                  debug_api: bool = False):
    try:
        sync_ip_ds = await dmds.DomoDataset.get_from_id(auth=auth,
                                                        dataset_id=dataset_id,
                                                        debug_api=debug_api)
        if debug_api:
            print(sync_ip_ds)

        print(
            f"⚙️ START - Retrieving whitelist configuration \n{sync_ip_ds.display_url()}")

        sync_ip_df = await sync_ip_ds.query_dataset_private(auth=auth,
                                                            dataset_id=dataset_id,
                                                            loop_until_end = True,
                                                            sql=sql)

        if sync_ip_df.empty:
            raise Exception('no whitelist returned')
            return False

        print(
            f"\n⚙️ SUCCESS 🎉 Retrieved whitelist configuration  \nThere are {len(sync_ip_df.index)} ip addresses to sync")

        return list(sync_ip_df['addresses'])

    except ex.InvalidDataset:
        print('invalid dataset')

        handle_err_fn(log_err=LogError(function_str='get_ip_whitelist_config',
                                       message_str=f'invalid dataset {dataset_id} not matched in {auth.domo_instance}',
                                       domo_instance=auth.domo_instance))
        return False

    except Exception:
        print("did it fail?")
        handle_err_fn(log_err=LogError(function_str='get_ip_whitelist_config',
                                       message_str=f'undefined error',
                                       domo_instance=auth.domo_instance))
        return False


async def remove_partition_by_x_days(auth: dmda.DomoFullAuth,
                                     dataset_id: str,
                                     x_last_days: int = 0,
                                     separator: str = None,
                                     date_index: int = 0,
                                     date_format: str = '%Y-%m-%d'):
    domo_ds = dmds.DomoDataset(auth=auth, id=dataset_id)

    list_partition = await domo_ds.list_partitions(auth=auth, dataset_id=dataset_id)

    today = DT.date.today()
    days_ago = today - DT.timedelta(days=x_last_days)
    for i in list_partition:
        compare_date = ''
        if separator is not None and separator != '':
            compare_date = i['partitionId'].split(separator)[date_index]
        else:
            compare_date = i['partitionId']

        try:
            d = DT.datetime.strptime(compare_date, date_format).date()
        except ValueError:
            d = None
        if d is not None and d < days_ago:
            print(auth.domo_instance, ': 🚀  Removing partition key : ',
                  (i['partitionId']), ' in ', dataset_id)
            await domo_ds.delete_partition(dataset_partition_id=i['partitionId'], dataset_id=dataset_id,
                                           auth=auth)


async def get_instance_whitelist_df(auth: dmda.DomoFullAuth
                                        ) -> pd.DataFrame:
    """return a dataframe data in the correct shape for upload for ONE instance"""
    instance_whitelist = await dmic.DomoInstanceConfig.get_whitelist(auth=auth)

    if instance_whitelist == ['']:
        instance_whitelist = ['no_ip_whitelist']

    upload_df = pd.DataFrame(instance_whitelist, columns=['address'])
    upload_df['instance'] = auth.domo_instance
    upload_df['url'] = f'https://{auth.domo_instance}.domo.com/admin/security/whitelist'

    return upload_df


async def get_company_domains(auth: dmda.DomoFullAuth,
                              dataset_id: str,
                              handle_err_fn: callable,
                              sql: str = "select domain from table",
                              global_admin_username: str = None,
                              global_admin_password: str = None,
                              execution_env: str = None,
                              debug_api: bool = False) -> pd.DataFrame:
    ds = await dmds.DomoDataset.get_from_id(auth=auth,
                                            id=dataset_id, debug_api=debug_api)

    print(f"⚙️ START - Retrieving company list \n{ds.display_url()}")
    print(f"⚙️ SQL = {sql}")

    df = await ds.query_dataset_private(auth=auth,
                                        dataset_id=dataset_id,
                                        sql=sql,
                                        loop_until_end = True,
                                        debug_api=debug_api)

    df["domo_instance"] = df["domain"].apply(
        lambda x: x.replace('.domo.com', ''))

    if global_admin_username:
        df["domo_username"] = global_admin_username
    if global_admin_password:
        df["domo_password"] = global_admin_password

    if execution_env:
        df['env'] = execution_env or 'manual'

    if df.empty:
        raise Exception('no companies retrieved')
        return False

    print(
        f"\n⚙️ SUCCESS 🎉 Retrieved company list \nThere are {len(df.index)} companies to update")

    return df