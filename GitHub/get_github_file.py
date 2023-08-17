import io
import pandas as pd
import requests


def get_github_file(gh_username, gh_pat, file_url) -> pd.DataFrame:

    gh_session = requests.Session()
    gh_session.auth = (gh_username, gh_pat)

    download = gh_session.get(file_url).content

    return pd.read_csv(io.StringIO(download.decode('utf-8')))
