#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan.BringSync.bring import Bring
from FoodScan.BringSync.bringSync import BringSync
from FoodScan.wunderlist import *
from config import *

wl = WuList(wunderlist_client_id, wunderlist_token)

# Syncer:
BringSync(Bring(bring_user_uuid, bring_api_key, bring_authorization, bring_cookie), wl, bring_export_list_id)
