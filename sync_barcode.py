#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.BarcodeDescriptors.barcodeDescriptorCombiner import BarcodeDescriptorCombiner
from FoodScan.Synchronizer.barcodeSync import BarcodeSync
from FoodScan.Synchronizer.wunderlist import *
from FoodScan.barcodereader import BarcodeReader
from config import *


wl = WuList(wunderlist_client_id, wunderlist_token)
reader = BarcodeReader(barcode_device)
barcode_transformer = BarcodeDescriptorCombiner()

# Syncer:
BarcodeSync(barcode_transformer, reader, wl, shopping_wunderlist_list_id, async=False)
