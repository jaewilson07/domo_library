import requests


def get_accounts(domo_instance: str, headers: dict) -> requests.models.Response:
    """fuction queries providers api and returns a list of all accounts authenticated user has access to"""

    url = f"https://{domo_instance}.domo.com/api/data/v2/datasources/providers"

    return requests.request(method="GET", url=url, headers=headers)
