# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/integrations/Automation.ipynb.

# %% auto 0
__all__ = ['remove_partition_by_x_days', 'get_company_domains']

# %% ../../nbs/integrations/Automation.ipynb 2
import datetime as dt
from dataclasses import dataclass
import pandas as pd

import domolibrary.client.DomoAuth as dmda
import domolibrary.classes.DomoDataset as dmds

# %% ../../nbs/integrations/Automation.ipynb 3
async def remove_partition_by_x_days(
    auth: dmda.DomoFullAuth,
    dataset_id: str,
    x_last_days: int = 0,
    separator: str = None,
    date_index: int = 0,
    date_format: str = "%Y-%m-%d",
):
    domo_ds = dmds.DomoDataset(auth=auth, id=dataset_id)

    list_partition = await domo_ds.list_partitions(auth=auth, dataset_id=dataset_id)

    today = dt.date.today()
    days_ago = today - dt.timedelta(days=x_last_days)
    for i in list_partition:
        compare_date = ""
        if separator is not None and separator != "":
            compare_date = i["partitionId"].split(separator)[date_index]
        else:
            compare_date = i["partitionId"]

        try:
            d = dt.datetime.strptime(compare_date, date_format).date()
        except ValueError:
            d = None
        if d is not None and d < days_ago:
            print(
                auth.domo_instance,
                ": 🚀  Removing partition key : ",
                (i["partitionId"]),
                " in ",
                dataset_id,
            )
            await domo_ds.delete_partition(
                dataset_partition_id=i["partitionId"], dataset_id=dataset_id, auth=auth
            )

# %% ../../nbs/integrations/Automation.ipynb 5
async def get_company_domains(
    auth: dmda.DomoFullAuth,
    dataset_id: str,
    handle_err_fn: callable,
    sql: str = "select domain from table",
    global_admin_username: str = None,
    global_admin_password: str = None,
    execution_env: str = None,
    debug_api: bool = False,
) -> pd.DataFrame:
    ds = await dmds.DomoDataset.get_from_id(
        auth=auth, id=dataset_id, debug_api=debug_api
    )

    print(f"⚙️ START - Retrieving company list \n{ds.display_url()}")
    print(f"⚙️ SQL = {sql}")

    df = await ds.query_dataset_private(
        auth=auth,
        dataset_id=dataset_id,
        sql=sql,
        loop_until_end=True,
        debug_api=debug_api,
    )

    df["domo_instance"] = df["domain"].apply(lambda x: x.replace(".domo.com", ""))

    if global_admin_username:
        df["domo_username"] = global_admin_username
    if global_admin_password:
        df["domo_password"] = global_admin_password

    if execution_env:
        df["env"] = execution_env or "manual"

    if df.empty:
        raise Exception("no companies retrieved")
        return False

    print(
        f"\n⚙️ SUCCESS 🎉 Retrieved company list \nThere are {len(df.index)} companies to update"
    )

    return df
