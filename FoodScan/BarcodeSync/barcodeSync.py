# -*- coding: utf-8 -*-
import pickle
from thread import start_new_thread
from pysimplelog import Logger
import traceback


class BarcodeSync:
    def __init__(self, barcode_descriptor, barcode_reader, wu_list, async=True):
        self.logger = Logger('BarcodeSync')
        self.barcode_descriptor = barcode_descriptor
        self.barcode_reader = barcode_reader
        self.wu_list = wu_list
        self.file_name = "barcode.db"
        self.matches = self.load()
        if async:
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
            return self.matches[barcode]
        else:
            return None

    def listen(self):
        while True:
            try:
                barcode = self.barcode_reader.q.get()
                item = self.match(barcode)
                if not item:
                    item = self.barcode_descriptor.item(barcode)
                    if item:
                        self.remember_choice(barcode, item)
                if item:
                    self.logger.info("Detected: " + item.name.encode('utf-8'))
                    self.add_barcode(item)
            except Exception:
                traceback.print_exc()

    def add_barcode(self, item):
        tasks = self.wu_list.client.get_tasks(self.wu_list.list_id)

        for task in tasks:
            if item.name.lower() in task['title'].lower():
                existing = self.wu_list.item_from_task(task, with_selects=False)
                existing.inc_amount()
                self.wu_list.client.update_task(task['id'], task['revision'], title=existing.title())
                return

        for task in tasks:
            existing = self.wu_list.item_from_task(task)
            if existing.synced() and item.name.lower() in existing.selected_shop_item().name.lower():
                existing.inc_amount()
                self.wu_list.client.update_task(task['id'], task['revision'], title=existing.title())
                return

        self.wu_list.create_item(item)


