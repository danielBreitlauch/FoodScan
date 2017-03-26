#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.BarcodeDecoder.cascadingBarcodeDecoder import CascadingBarcodeDecoder
from FoodScan.Synchronizer.barcodeSync import BarcodeSync
from FoodScan.Synchronizer.wunderlist import *
from FoodScan.barcodereader import BarcodeReader
from config import *


wl = WuList(wunderlist_client_id, wunderlist_token)
reader = BarcodeReader(barcode_device)
barcode_transformer = CascadingBarcodeDecoder()

# Syncer:
BarcodeSync(barcode_transformer, reader, wl, shopping_wunderlist_list_id, async=False)
