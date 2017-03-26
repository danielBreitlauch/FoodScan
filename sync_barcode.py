#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan import *
from FoodScan.BarcodeSync import *
from config import *

wl = WuList(wunderlist_client_id, wunderlist_token)
reader = BarcodeReader(barcode_sync_config['barcode_device'])

BarcodeSync(CascadingBarcodeDecoder(), reader, wl, barcode_sync_config['wunderlist_list_id'], async=False)
