# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoApplication.ipynb.

# %% auto 0
__all__ = []

# %% ../../nbs/classes/50_DomoApplication.ipynb 2
import domolibrary.routes.job as job_routes
import domolibrary.routes.application as application_routes
import domolibrary.classes.DomoJob as dmdj
import pandas as pd
from dataclasses import dataclass

from pprint import pprint

import datetime as dt
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

import json
import io

import httpx
import asyncio

import domolibrary.utils.DictDot as DictDot
import domolibrary.client.DomoAuth as dmda

from enum import Enum


