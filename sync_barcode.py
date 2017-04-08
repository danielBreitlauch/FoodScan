#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan import *
from FoodScan.BarcodeSync import *
from config import *

wl = WuList(wunderlist_client_id, wunderlist_token, barcode_sync_config['wunderlist_list_id'])
reader = BarcodeReader(barcode_sync_config['vendor'], barcode_sync_config['product'])

BarcodeSync(CascadingBarcodeDecoder(), reader, wl, async=False)
