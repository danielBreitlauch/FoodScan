#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan.BarcodeSync.BarcodeDecoder.cascadingBarcodeDecoder import CascadingBarcodeDecoder
from FoodScan.BarcodeSync.barcodeSync import BarcodeSync
from FoodScan.BarcodeSync.barcodereader import BarcodeReader
from FoodScan.wunderlist import *
from config import *

wl = WuList(wunderlist_client_id, wunderlist_token)
reader = BarcodeReader(barcode_sync_config['barcode_device'])
barcode_transformer = CascadingBarcodeDecoder()

# Syncer:
BarcodeSync(barcode_transformer, reader, wl, shopping_wunderlist_list_id, async=False)
