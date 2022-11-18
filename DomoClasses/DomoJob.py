from dataclasses import dataclass

from pprint import pprint

import aiohttp
import datetime as dt

from Library.utils.DictDot import DictDot
from ..utils.DictDot import DictDot
from .DomoAuth import DomoFullAuth

from .routes import job_routes


@dataclass
class DomoTrigger_Schedule:
    schedule_text: str = None
    schedule_type: str = 'scheduleTriggered'

    minute: int = None
    hour: int = None

    @classmethod
    def _from_str(cls, s_text, s_type):
        sched = cls(
            schedule_type=s_type,
            schedule_text=s_text)

        try:
            sched.hour = int(float(s_text.split(' ')[2]))
            sched.minute = int(float(s_text.split(' ')[1]))

            # print(sched)

            return sched

        except Exception as e:
            print(f"unable to parse schedule {s_text}")
            print(e)

    def to_obj(self):
        return {'hour': int(self.hour),
                'minute': int(self.minute)}

    def to_schedule_obj(self):
        return {
            "eventEntity": f'0 {self.minute} {self.hour} 1/1 * ? *',
            "eventType": self.schedule_type
        }


@dataclass
class DomoTrigger:
    id: str
    job_id: str
    schedule: [DomoTrigger_Schedule] = None


@dataclass
class DomoJob:
    id: str
    name: str
    remote_instance: str
    user_id: int
    application_id: str
    customer_id: str
    triggers: [DomoTrigger] = None

    @classmethod
    def _from_json(cls, obj):
        dd = DictDot(obj)

        triggers_ls = obj.get('triggers', None)

        triggers_dj = [DomoTrigger(
            id=tg.get('triggerId'),
            job_id=tg.get('jobId'),

            schedule=DomoTrigger_Schedule._from_str(
                s_text=tg.get('eventEntity'),
                s_type=tg.get('eventType'))
        ) for tg in triggers_ls]

        # pprint(dd)

        return cls(id=dd.jobId,
                   name=dd.jobName,
                   user_id=dd.userId,
                   remote_instance=dd.executionPayload.remoteInstance.replace(
                       '.domo.com', '') if dd.executionPayload.remoteInstance else None,
                   application_id=dd.applicationId,
                   customer_id=dd.customerId,
                   triggers=triggers_dj)

    @classmethod
    async def create_domostats_job(cls,
                                   full_auth: DomoFullAuth,
                                   domostats_schedule: DomoTrigger_Schedule,
                                   application_id: str,
                                   target_instance: str,
                                   report_dict: dict,
                                   output_dataset_id: str,
                                   account_id: str,
                                   execution_timeout: int = 1440,
                                   debug: bool = False, log_results: bool = False,
                                   session: aiohttp.ClientSession = None):

        schedule_obj = domostats_schedule.to_schedule_obj()

        body = job_routes.generate_body_remote_domostats(target_instance=target_instance,
                                                         report_dict=report_dict,
                                                         output_dataset_id=output_dataset_id,
                                                         account_id=account_id,
                                                         schedule_ls=[
                                                             schedule_obj],
                                                         execution_timeout=execution_timeout)

        res = await job_routes.add_job(full_auth=full_auth,
                                       application_id=application_id,
                                       body=body,
                                       debug=debug,
                                       log_results=log_results,
                                       session=session)

#         if debug:
#             print(res)

        if res.status != 200:
            return False

        return True
