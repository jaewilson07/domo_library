import aiohttp
from dataclasses import dataclass, field
import pandas as pd

from ..utils.DictDot import DictDot

from .DomoAuth import DomoFullAuth
from .routes import job_routes, application_routes
import Library.DomoClasses.DomoJob as dmdj


@dataclass
class DomoApplication:
    id: str
    customer_id: str = None
    name: str = None
    description: str = None
    version: str = None
    execution_class: str = None
    grants: [str] = None
    jobs: [dmdj.DomoJob] = field(default=None)
    jobs_schedule: pd.DataFrame = field(default=None, repr=False)
    full_auth: DomoFullAuth = field(repr=False, default=None)

    @classmethod
    def _from_json(cls, obj, full_auth: DomoFullAuth = None):
        dd = DictDot(obj)

        return cls(
            id=dd.applicationId,
            customer_id=dd.customerId,
            name=dd.name,
            description=dd.description,
            version=dd.version,
            execution_class=dd.executionClass,
            grants=dd.authorities,
            full_auth=full_auth)

    @classmethod
    async def get_from_id(cls, full_auth: DomoFullAuth, application_id=None):
        res = await application_routes.get_application_by_id(application_id=application_id, full_auth=full_auth or self.full_auth)

        if res.status == 200:
            return cls._from_json(obj=res.response, full_auth=full_auth)

    async def get_jobs(self, full_auth: DomoFullAuth = None,
                       application_id: str = None,
                       debug: bool = False, session: aiohttp.ClientSession = None, return_raw: bool = False):

        res = await job_routes.get_jobs(full_auth=full_auth or self.full_auth,
                                        application_id=application_id or self.id,
                                        debug=debug,
                                        session=session)
        if debug:
            print('Getting Domostats jobs')

        if res.status == 200 and not return_raw:
            self.jobs = [dmdj.DomoJob._from_json(job) for job in res.response]
            return self.jobs

        if res.status == 200 and return_raw:
            return res.response

    async def get_all_schedules(self, full_auth: DomoFullAuth = None):
        if not self.jobs and (self.full_auth or full_auth):
            await self.get_jobs()

        elif not self.jobs and not (self.full_auth or full_auth):
            raise Exception("pass a full_auth object")

        schedules = pd.DataFrame([{'hour': trigger.schedule.hour,
                                   'minute': trigger.schedule.minute,
                                   'job_id': job.id,
                                   'job_name': job.name,
                                   'trigger_id': trigger.id} for job in self.jobs for trigger in job.triggers])

        self.jobs_schedule = schedules.sort_values(
            ['hour', 'minute'], ascending=True).reset_index(drop=True)
        return self.jobs_schedule

    async def find_next_job_schedule(self) -> dmdj.DomoTrigger_Schedule:
        if not isinstance(self.jobs_schedule, pd.DataFrame) and (self.full_auth or full_auth):
            await self.get_all_schedules()

        elif not isinstance(self.jobs_schedule, pd.DataFrame) and not (self.full_auth or full_auth):
            raise Exception("pass a full_auth object")

        df_all_hours = pd.DataFrame(range(0, 23), columns=['hour'])
        df_all_minutes = pd.DataFrame(range(0, 60), columns=['minute'])

        df_all_hours['tmp'] = 1
        df_all_minutes['tmp'] = 1
        df_all = pd.merge(df_all_hours, df_all_minutes,
                          on='tmp').drop(columns=['tmp'])

        # get the number of occurencies of each hour and minutes
        schedules_grouped = self.jobs_schedule.groupby(
            ['hour', 'minute']).size().reset_index(name='cnt_schedule')

        # print(schedules_grouped)
        # print(df_all)

        schedules_interpolated = pd.merge(
            df_all, schedules_grouped, how='left', on=['hour', 'minute'])

        schedules_interpolated['cnt_schedule'] = schedules_interpolated['cnt_schedule'].fillna(
            value=0)
        schedules_interpolated.sort_values(
            ['cnt_schedule', 'hour', 'minute'], ascending=True, inplace=True)

        schedules_interpolated.reset_index(drop=True, inplace=True)

        return dmdj.DomoTrigger_Schedule(
            hour=int(schedules_interpolated.loc[0].get('hour')),
            minute=int(schedules_interpolated.loc[0].get('minute')))
