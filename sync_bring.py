#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan.BringSync import *
from FoodScan import *
from config import *

BringSync(Bring(bring_sync_config), WuList(wunderlist_client_id, wunderlist_token, bring_sync_config["export_list_id"]))
