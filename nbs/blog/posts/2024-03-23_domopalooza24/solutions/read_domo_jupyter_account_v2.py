import json
import domojupyter as dj


def read_domo_jupyter_account(account_name, is_abstract: bool = False):

    account_properties = dj.get_account_property_keys(account_name)

    creds = {
        prop: dj.get_account_property_value(account_name, prop)
        for prop in account_properties
    }

    if not is_abstract:
        return creds

    return json.loads(creds["credentials"])
