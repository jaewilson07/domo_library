import csv
import datetime as DT
import os
from dataclasses import dataclass

import aiohttp
import Library.DomoClasses.DomoAuth as dmda
import Library.DomoClasses.DomoDataset as dmds
import Library.DomoClasses.DomoInstanceConfig as dmic
import Library.utils.Exceptions as ex
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

        # res = log_file.write(f"{log_err.domo_instance}, {log_err.function_str}, {log_err.message_str}\n")


async def get_ip_whitelist_config(config_full_auth: dmda.DomoFullAuth,
                                  dataset_id: str,
                                  handle_err_fn: callable,
                                  sql: str = "select addresses from table",
                                  debug: bool = False):
    try:
        sync_ip_ds = await dmds.DomoDataset.get_from_id(full_auth=config_full_auth,
                                                        id=dataset_id,
                                                        debug=debug)
        if debug:
            print(sync_ip_ds)

        print(
            f"⚙️ START - Retrieving whitelist configuration \n{sync_ip_ds.display_url()}")

        sync_ip_df = await sync_ip_ds.query_dataset_private(full_auth=config_full_auth,
                                                            dataset_id=dataset_id,
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
                                       message_str=f'invalid dataset {dataset_id} not matched in {config_full_auth.domo_instance}',
                                       domo_instance=config_full_auth.domo_instance))
        return False

    except Exception:
        print("did it fail?")
        handle_err_fn(log_err=LogError(function_str='get_ip_whitelist_config',
                                       message_str=f'undefined error',
                                       domo_instance=config_full_auth.domo_instance))
        return False


async def remove_partition_by_x_days(full_auth: dmda.DomoFullAuth,
                                     dataset_id: str,
                                     x_last_days: int = 0,
                                     separator: str = None,
                                     date_index: int = 0,
                                     date_format: str = '%Y-%m-%d',
                                     session: aiohttp.ClientSession = None
                                     ):
    domo_ds = dmds.DomoDataset(full_auth=full_auth, id=dataset_id)

    list_partition = await domo_ds.list_partitions(full_auth=full_auth, dataset_id=dataset_id)

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
            print(full_auth.domo_instance, ': 🚀  Removing partition key : ',
                  (i['partitionId']), ' in ', dataset_id)
            await domo_ds.delete_partition(dataset_partition_id=i['partitionId'], dataset_id=dataset_id,
                                           full_auth=full_auth, session=session)


async def get_instance_whitelist_df(instance_auth: dmda.DomoFullAuth,
                                    session: aiohttp.ClientSession = None,
                                    debug: bool = False) -> pd.DataFrame:
    """return a dataframe data in the correct shape for upload for ONE instance"""
    instance_whitelist = await dmic.DomoInstanceConfig.get_whitelist(full_auth=instance_auth, session=session)

    if instance_whitelist == ['']:
        instance_whitelist = ['no_ip_whitelist']

    upload_df = pd.DataFrame(instance_whitelist, columns=['address'])
    upload_df['instance'] = instance_auth.domo_instance
    upload_df['url'] = f'https://{instance_auth.domo_instance}.domo.com/admin/security/whitelist'

    return upload_df


async def get_company_domains(config_full_auth: dmda.DomoFullAuth,
                              dataset_id: str,
                              handle_err_fn: callable,
                              sql: str = "select domain from table",
                              global_admin_username: str = None,
                              global_admin_password: str = None,
                              execution_env: str = None,
                              debug: bool = False) -> pd.DataFrame:
    ds = await dmds.DomoDataset.get_from_id(full_auth=config_full_auth,
                                            id=dataset_id, debug=debug)

    print(f"⚙️ START - Retrieving company list \n{ds.display_url()}")
    print(f"⚙️ SQL = {sql}")

    df = await ds.query_dataset_private(full_auth=config_full_auth,
                                        dataset_id=dataset_id,
                                        sql=sql,
                                        debug=debug)

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
