import asyncio

import aiohttp
import pandas as pd

import domolibrary.client.Logger as lc


async def upload_data(instance_auth,
                      consol_auth,
                      data_fn,
                      consol_ds,
                      is_index: bool = False,
                      debug: bool = False,
                      debug_prn: bool = False,
                      logger: lc.Logger = None):

    try:
        # await asyncio.sleep(randrange(5))
        if logger:
            logger.log_info(
                f" Upload_data function - starting {instance_auth.domo_instance} - {data_fn.__name__}")
        if debug_prn:
            print(
                f"starting {instance_auth.domo_instance} - {data_fn.__name__}")

        instance_session = aiohttp.ClientSession()

        upload_df = await data_fn(instance_auth, instance_session)

        if upload_df is None or len(upload_df.index) == 0:
            return None

        await instance_session.close()

        return await consol_ds.upload_csv(upload_df=upload_df,
                                          full_auth=consol_auth,
                                          upload_method='APPEND',
                                          partition_key=instance_auth.domo_instance,
                                          is_index=is_index)

    except Exception as e:
        print(f"upload_data : unexpected error: {e}")
        if logger:
            logger.log_error(f"upload_data : unexpected error: {e}")
        return None

    finally:
        await instance_session.close()


async def upload_data_with_date(instance_auth,
                                consol_auth,
                                data_fn,
                                consol_ds,
                                partition_date_col,
                                partition_delimiter,
                                start_date,
                                end_date,
                                debug: bool = False,
                                debug_prn: bool = False):

    instance_session = aiohttp.ClientSession()

    print(
        f"'🎬 upload_with_data: starting retrieval {start_date}, {end_date}, {instance_auth.domo_instance}")

    upload_df = await data_fn(instance_auth=instance_auth,
                              session=instance_session,
                              start_date=start_date,
                              end_date=end_date,
                              debug=debug)

    await instance_session.close()

    if not isinstance(upload_df, pd.DataFrame):
        print(f"🛑 error no data returned {instance_auth.domo_instance}")
        print(upload_df)
        return None

    if debug_prn:
        print(
            f'🧻 upload_with_data: starting upload {len(upload_df)} rows for {instance_auth.domo_instance}')

    task = []

    for index, partition_set in upload_df.drop_duplicates(subset=[partition_date_col]).iterrows():
        partition_date = partition_set[partition_date_col]

        partition_key = f"{instance_auth.domo_instance}{partition_delimiter}{str(partition_date)}"

        task.append(consol_ds.upload_csv(upload_df=upload_df[(upload_df[partition_date_col] == partition_date)],
                                         upload_method='REPLACE',
                                         debug=debug,
                                         partition_key=partition_key,
                                         is_index=False))

    res = await asyncio.gather(*task)

    if debug_prn:
        print(
            f'🎉 upload_with_data : finished uploading {len(upload_df)} rows for {instance_auth.domo_instance}')
    return res
