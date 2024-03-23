import domojupyter as domo
import json


def get_account_credentials(account_name, is_abstract_account: bool = True):
    """handles retrieving account properties in domo jupter"""

    account_properties = domo.get_account_property_keys(account_name)
    res = {
        prop: domo.get_account_property_value(account_name, prop)
        for prop in account_properties
    }
    return json.loads(res["credentials"])
