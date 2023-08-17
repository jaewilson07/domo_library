import json

import Transport as tr

# class Snowflake_DatabaseObjects(Enum):
#     TABLES = 'tables'


def con_s3(warehouse_name,
           database_name,
           schema_name,
           table_name,
           database_objects: Snowflake_DatabaseObjects = Snowflake_DatabaseObjects.TABLES,

           qry_whereClause=None,
           qry_limitClause: str = None,

           account_id=None,
           ds_name=None,
           ds_description=None,
           query=None,
           schedule: tr.Schedule = None
           ):
    cnfg = tr.Config.SNOWFLAKE_UNLOADv2.value

    if not query:
        query = f"SELECT * \nFROM {table_name} \n{qry_whereClause} "
        if qry_limitClause:
            query += f"\n{qry_limitClause}"

    configuration = [
        tr.ConfigurationParam(
            name='importDataMethod',
            value="noPartiionAndUpsert"),
        tr.ConfigurationParam(
            name='warehouseName',
            value=warehouse_name),
        tr.ConfigurationParam(
            name='databaseName',
            value=database_name),
        tr.ConfigurationParam(
            name='schemaName',
            value=schema_name),
        tr.ConfigurationParam(
            name='databaseObjects',
            value=database_objects.value),
        tr.ConfigurationParam(
            name='tableName',
            value=table_name),
        tr.ConfigurationParam(
            name='queryType',
            value='customQuery'),
        tr.ConfigurationParam(
            name='query',
            value=query),

    ]

    config = tr.Configuration(transport=tr.Transport(type=cnfg.get('type'),
                                                     description=cnfg.get(
                                                         'description'),
                                                     version=cnfg.get('version')),
                              account=tr.Account(id=account_id),
                              configuration=configuration,
                              updateMethod=tr.UpdateMethod.APPEND.value,
                              dataProvider=tr.DataProvider(
                                  key=cnfg.get('dataProvider_key')),
                              dataSource=tr.Datasource(
                                  name=ds_name, description=ds_description),
                              advancedScheduleJson=schedule
                              )

    return config


cnfg_pgsql = con_snowflake(warehouse_name="WH_BIS_PARTNER_ANALYTICS_HEAVY_NONPROD",
                           database_objects=Snowflake_DatabaseObjects.TABLES,
                           schema_name="PUBLIC",
                           database_name="BIS_PRD_01_REF",
                           table_name="HASH_ACCOUNT_ID_MAPPING",
                           account_id=3,
                           ds_name='hello world',
                           ds_description='config works?',

                           query="SELECT \nha.\"ACCT_ID\", \nha.\"HASH_ACCT_ID\" ,\nem.\"HASHED_EMAIL_ADDRESS\"\n\nFROM \"BIS_PRD_01_REF\".\"PUBLIC\".\"HASH_ACCOUNT_ID_MAPPING\" ha\n\nINNER JOIN PS_PRD_01_USERODS.PUBLIC.CCRM_ACCT_HASHED_EMAIL_MAP em\n\nON\n\nha.\"ACCT_ID\" = em.\"ACCT_ID\""
                           )

# pprint(cnfg_pgsql.to_dict())


print(json.dumps(cnfg_pgsql.to_dict()))
