import Transport as tr


def con_pgsql(qry_tableName=None,
              qry_whereClause=None,
              qry_limitClause: str = None,

              partition_col: str = None,
              partition_relativedays: int = None,
              account_id=None,
              ds_name=None,
              ds_description=None,
              fetch_size: int = None,
              query=None,
              schedule: tr.Schedule = None
              ):
    cnfg = tr.Config.PGSQL_PARTITION.PGSQL.value if not partition_col else tr.Config.PGSQL_PARTITION.value

    if not query:
        query = f"SELECT * \nFROM {qry_tableName} \n{qry_whereClause} "
        if qry_limitClause:
            query += f"\n{qry_limitClause}"

    configuration = [
        tr.ConfigurationParam(
            name='fetch_size',
            value=str(fetch_size) or '400'),

        tr.ConfigurationParam(
            name='query',
            value=query)
    ]
    if not partition_col:
        configuration += [
            tr.ConfigurationParam(
                name="queryType",
                value="customQuery"
            )
        ]

    if partition_col:
        configuration += [
            tr.ConfigurationParam(
                name="tableName",
                value=qry_tableName),
            tr.ConfigurationParam(
                name="partitionColumnName",
                value=partition_col),
            tr.ConfigurationParam(
                name="updatemode.mode",
                value="APPEND"),
            tr.ConfigurationParam(
                name="relavtiveDays",
                value=partition_relativedays)
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


# cnfg_pgsql = con_pgsql(account_id=1,
#                        ds_name='hello world',
#                        ds_description='config works?',
#                        qry_tableName='public$tlm_tx_fb_v1_siea',
#                        query="SELECT\n*\nFROM tlm_tx_fb_v1_siea\nWHERE aep_batch_date = current_date  - INTERVAL '1 DAY'\nLIMIT 20000"
#                        )

# pprint(cnfg_pgsql.to_dict())

# import json

# print(json.dumps(cnfg_pgsql.to_dict()))
