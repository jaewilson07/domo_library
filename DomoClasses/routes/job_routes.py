import aiohttp
from pprint import pprint

from .get_data import get_data, looper
from ..DomoAuth import DomoFullAuth
from ...utils.ResponseGetData import ResponseGetData


# get RemoteDomostats job names
async def get_jobs(full_auth: DomoFullAuth,
                   application_id: str,
                   debug: bool = False, log_results: bool = False,
                   session: aiohttp.ClientSession = None):
    try:
        is_close_session = False

        if not session:
            session = aiohttp.ClientSession()
            is_close_session = True

        offset_params = {
            'offset': 'offset',
            'limit': 'limit'}

        offset = 60
        limit = 10

        url = f'https://{full_auth.domo_instance}.domo.com/api/executor/v2/applications/{application_id}/jobs'

        if debug:
            print(url)

        def arr_fn(res) -> list[dict]:
            return res.response.get('jobs')

        def alter_maximum_fn(res):
            return res.response.get('totalResults')

        res = await looper(auth=full_auth,
                           method='GET',
                           url=url,
                           arr_fn=arr_fn,
                           limit=100,
                           # fixed_params=fixed_params,
                           alter_maximum_fn=alter_maximum_fn,
                           offset_params=offset_params,

                           session=session,
                           # maximum=maximum,
                           debug=debug)

        return ResponseGetData(
            status=200,
            response=res,
            is_success=True)
    except:
        return ResponseGetData(
            status=400,
            is_success=False)

    finally:
        if is_close_session:
            await session.close()


# create the new RemoteDomostats job
async def add_job(full_auth: DomoFullAuth,
                  body: dict,
                  application_id: str,
                  session: aiohttp.ClientSession = None,
                  debug: bool = False,
                  log_results: bool = False
                  ):

    url = f'https://{full_auth.domo_instance}.domo.com/api/executor/v1/applications/{application_id}/jobs'

    if debug:
        print(url)

    return await get_data(
        auth=full_auth,
        url=url,
        method='POST',
        body=body,
        log_results=log_results,
        debug=debug,
        session=session
    )


def generate_body_remote_domostats(target_instance: str,
                                   report_dict: dict,
                                   output_dataset_id: str,
                                   account_id: str,
                                   schedule_ls: list,
                                   execution_timeout: int = 1440,
                                   debug: bool = False):

    instance_url = f"{target_instance}.domo.com"

    body = {
        "jobName": instance_url,
        "jobDescription": f'Get Remote stat from {instance_url}',
        "executionTimeout": execution_timeout,
        "executionPayload": {
            "remoteInstance": instance_url,
            "policies": report_dict,
            "metricsDatasetId": output_dataset_id},
        "accounts": [account_id],
        "executionClass": "com.domo.executor.subscriberstats.SubscriberStatsExecutor",
        "resources": {
            "requests": {"memory": "256M"},
            "limits": {"memory": "256M"}},
        "triggers": schedule_ls
    }

    if debug:
        pprint(body)

    return body


def generate_body_watchdog_generic(job_name: str,
                                        notify_user_ids_ls: list,
                                        notify_group_ids_ls: list,
                                        notify_emails_ls: list,
                                        entity_ids_ls: list,
                                        entity_type : str,
                                        metric_dataset_id: str,
                                        schedule_ls: list,
                                        job_type : str,
                                        execution_timeout: int = 1440,
                                        debug: bool = False):

    body = {
        "jobName": job_name,
        "jobDescription": f'Watchdog for {job_name}',
        "executionTimeout": execution_timeout,
        "accounts": [],
        "executionPayload": {
            "notifyUserIds": notify_user_ids_ls or [],
            "notifyGroupIds": notify_group_ids_ls or [],
            "notifyEmailAddresses": notify_emails_ls or [],
        "watcherParameters": {
          "entityIds": entity_ids_ls,
          "type": job_type,
          "entityType": entity_type
            },
        "metricsDatasetId": metric_dataset_id
          },
        "resources": {
            "requests": {"memory": "256Mi"},
            "limits": {"memory": "256Mi"}
        },
        "triggers": schedule_ls
    }

    if debug:
        pprint(body)

    return body

# update the job
async def update_job(full_auth: DomoFullAuth,
                  body: dict,
                  job_id :str,
                  application_id: str,
                  session: aiohttp.ClientSession = None,
                  debug: bool = False,
                  log_results: bool = False
                  ):

    url = f'https://{full_auth.domo_instance}.domo.com/api/executor/v1/applications/{application_id}/jobs/{job_id}'

    if debug:
        print(url)

    return await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        log_results=log_results,
        debug=debug,
        session=session
    )

#update trigger

async def update_job_trigger(full_auth: DomoFullAuth,
                  body: dict,
                  job_id :str,
                  trigger_id : str,  
                  application_id: str,
                  session: aiohttp.ClientSession = None,
                  debug: bool = False,
                  log_results: bool = False
                  ):

    url = f'https://{full_auth.domo_instance}.domo.com/api/executor/v1/applications/{application_id}/jobs/{job_id}/triggers/{trigger_id}'

    if debug:
        print(url)

    return await get_data(
        auth=full_auth,
        url=url,
        method='PUT',
        body=body,
        log_results=log_results,
        debug=debug,
        session=session
    )
