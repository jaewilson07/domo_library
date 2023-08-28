# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/chunk_execution.ipynb.

# %% auto 0
__all__ = ['run_sequence', 'chunk_list']

# %% ../../nbs/utils/chunk_execution.ipynb 2
from typing import Any, Awaitable

# %% ../../nbs/utils/chunk_execution.ipynb 3
async def run_sequence(*functions: Awaitable[Any] # comma separated list of functions
 ) -> None: # no explicit return
    """executes a sequence of functions"""

    return [ await function for function in functions]
        

# %% ../../nbs/utils/chunk_execution.ipynb 6
def chunk_list(obj_ls :list[any],  # list of entities to split into n chunks
               chunk_size:int  # entities per sub list
               ) -> list[list[dict]]:  # returns a list of chunk_size lists of objects

    return [obj_ls[i * chunk_size:(i + 1) * chunk_size] for i in range((len(obj_ls) + chunk_size - 1) // chunk_size)]

