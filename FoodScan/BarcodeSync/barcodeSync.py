# -*- coding: utf-8 -*-
import pickle
from _thread import start_new_thread
from pysimplelog import Logger
import traceback

from FoodScan.BarcodeSync import BarcodeReader


class BarcodeSync:
    def __init__(self, barcode_descriptor, config, shopList, asynchron=True):
        self.logger = Logger('BarcodeSync')
        self.barcode_descriptor = barcode_descriptor
        self.barcode_reader = BarcodeReader(config['barcode_device_name'])
        self.shop_list = shopList
        self.file_name = "barcode.db"
        self.matches = self.load()
        if asynchron:
            start_new_thread(self.listen, ())
        else:
            self.listen()

    def save(self):
        with open(self.file_name, 'w') as f:
            pickle.dump(self.matches, f)

    def load(self):
        try:
            with open(self.file_name) as f:
                return pickle.load(f)
        except IOError:
            return {}

    def remember_choice(self, barcode, item):
        self.matches[barcode] = item
        self.save()

    def match(self, barcode):
        if barcode in self.matches:
            self.logger.info("Use old match for: " + barcode)
            return self.matches[barcode]
        else:
            return None

    def listen(self):
        while True:
            try:
                barcode = self.barcode_reader.q.get()
                self.logger.info("Work on: " + barcode)
                item = self.match(barcode)
                if not item:
                    item = self.barcode_descriptor.item(barcode)
                    if item:
                        self.remember_choice(barcode, item)
                if item:
                    self.logger.info("Detected: " + item.name.encode('utf-8'))
                    self.add_barcode(item)
                else:
                    self.logger.info("Could not id: " + barcode)
            except Exception:
                traceback.print_exc()

    def add_barcode(self, item):
        for task, existing in self.shop_list.list_items():
            if existing.synced() and item.name.lower() in existing.selected_shop_item().name.lower():
                existing.inc_amount()
                self.shop_list.update_item(task, existing)
                return

        self.shop_list.create_item(item)
