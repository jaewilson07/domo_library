# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/convert.ipynb.

# %% auto 0
__all__ = ['convert_epoch_millisecond_to_datetime', 'convert_datetime_to_epoch_millisecond', 'convert_snake_to_pascal',
           'InvalidEmail', 'test_valid_email', 'convert_string_to_bool', 'ConcatDataframe_InvalidElement',
           'concat_list_dataframe']

# %% ../../nbs/utils/convert.ipynb 2
import datetime as dt
import pandas as pd
import re

# %% ../../nbs/utils/convert.ipynb 5
def convert_epoch_millisecond_to_datetime(epoch: int):
    """convert Epoch time with miliseconds to Date time"""
    return dt.datetime.fromtimestamp(epoch / 1000.0) if epoch else None

# %% ../../nbs/utils/convert.ipynb 6
def convert_datetime_to_epoch_millisecond(datetime: dt.datetime):
    """convert DateTime to Epoch time with Miliseconds"""
    return int(datetime.timestamp() * 1000) if datetime else None

# %% ../../nbs/utils/convert.ipynb 10
def convert_snake_to_pascal(clean_str):
    """converts 'snake_case_str' to 'snakeCaseStr'"""

    clean_str = clean_str.replace("_", " ").title().replace(" ", "")
    return clean_str[0].lower() + clean_str[1:]

# %% ../../nbs/utils/convert.ipynb 13
class InvalidEmail(Exception):
    def __init__(self, email):

        super().__init__(f'invalid email: "{email}" provided')


def test_valid_email(email):
    """tests if provided string is a for valid email"""

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(pattern, email):
        return True

    else:
        raise InvalidEmail(email=email)

# %% ../../nbs/utils/convert.ipynb 16
def convert_string_to_bool(v):
    return v.lower() in ("yes", "true", "t", "1")

# %% ../../nbs/utils/convert.ipynb 18
class ConcatDataframe_InvalidElement(Exception):
    def __init__(self, elem):
        message = f"{type(elem)} passed into dataframe"
        super().__init__(message)


def concat_list_dataframe(df_ls: list[pd.DataFrame]) -> pd.DataFrame:
    """take a list of dataframes and collapse into one dataframe"""

    df = None
    for elem in df_ls:
        if not isinstance(elem, pd.DataFrame):
            raise ConcatDataframe_InvalidElement(elem)

        if len(elem.index) == 0:
            pass

        if df is None:
            df = elem

        else:
            df = pd.concat([df, elem], join="inner").reset_index(drop=True)
    return df
