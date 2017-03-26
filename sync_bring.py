#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan.BringSync.bring import Bring
from FoodScan.BringSync.bringSync import BringSync
from FoodScan.wunderlist import *
from config import *
from config_example import bring_sync_config

BringSync(Bring(bring_sync_config), WuList(wunderlist_client_id, wunderlist_token), bring_sync_config["export_list_id"])
