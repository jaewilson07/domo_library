import domojupyer as dj


def read_domo_jupyter_account(account_name):

    account_properties = dj.get_account_property_keys(account_name)

    creds = {
        prop: dj.get_account_property_value(account_name, prop)
        for prop in account_properties
    }  # in python this technique is called a "list comprehension" its similar to a for loop

    return creds
