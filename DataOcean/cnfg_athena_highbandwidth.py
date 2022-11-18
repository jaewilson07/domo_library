import Transport as tr


def con_athena_highbandwidth(database_name,
                             qry_tableName=None,
                             qry_whereClause=None,
                             qry_limitClause: str = None,
                             account_id=None,
                             ds_name=None,
                             ds_description=None,
                             query=None,
                             schedule: tr.Schedule = None
                             ):
    cnfg = tr.Config.ATHENA_HIGHBANDWIDTH.value

    if not query:
        query = f"SELECT * \nFROM {database_name}.{qry_tableName} \n{qry_whereClause} "
        if qry_limitClause:
            query += f"\n{qry_limitClause}"

    configuration = [
        tr.ConfigurationParam(
            name='queryType',
            value='customQuery'),
        tr.ConfigurationParam(
            name="dataCatalogName",
            value="AwsDataCatalog"
        ),
        tr.ConfigurationParam(
            name='databaseName',
            value=database_name),
        tr.ConfigurationParam(
            name='enteredCustomQuery',
            value=query),
        tr.ConfigurationParam(
            name='bypassDataUpload',
            value=True

        ),
        tr.ConfigurationParam(
            name="keepUnloadExecutedFiles",
            value=True)
    ]

    config = tr.Configuration(transport=tr.Transport(type=cnfg.get('type'),
                                                     description=cnfg.get(
                                                         'description'),
                                                     version=cnfg.get('version')),
                              account=tr.Account(id=account_id),
                              configuration=configuration,
                              updateMethod=tr.UpdateMethod.REPLACE.value,
                              dataProvider=tr.DataProvider(
                                  key=cnfg.get('dataProvider_key')),
                              dataSource=tr.Datasource(
                                  name=ds_name, description=ds_description),
                              advancedScheduleJson=schedule)

    return config
