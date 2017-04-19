# -*- coding: utf-8 -*-
import pickle
from thread import start_new_thread
from time import sleep
import traceback
from pysimplelog import Logger
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from FoodScan.ShopSync.metaShop import MetaShop, MetaShopItem


class ShopSync:
    def __init__(self, shop, wu_list, web_hook_url=None, web_server_ip=None, web_server_port=8080, async=True):
        self.logger = Logger('ShopSync')
        self.shop = shop
        self.wu_list = wu_list
        self.meta = MetaShop(self, wu_list)
        self.shop_list_rev = 0
        self.shop_task_revs = {}
        self.shop_items = {}
        self.choice = Choice("choices-" + shop.__class__.__name__ + ".db")
        if web_hook_url:
            self.web_hook_url = web_hook_url
            self.web_server_ip = web_server_ip
            self.web_server_port = web_server_port
            function = self.start_hook
        else:
            function = self.listen
        if async:
            start_new_thread(function, ())
        else:
            function()

    def start_hook(self):
        self.sync_shop_list()
        self.sync_shop_list()
        self.wu_list.create_web_hook(self.web_hook_url, self.web_server_port)
        run_simple(self.web_server_ip, self.web_server_port, self.hook)

    @Request.application
    def hook(self, _):
        self.sync_shop_list()
        return Response()

    def listen(self):
        wait = [10, 30, 60, 120, 240, 480]
        wait_index = 0
        while True:
            try:
                change = self.sync_shop_list()
                if change:
                    wait_index = 0
                else:
                    sleep(wait[wait_index])
                    wait_index = min(wait_index + 1, len(wait) - 1)
            except Exception:
                traceback.print_exc()

    def sync_shop_list(self):
        if self.shop_list_rev == self.wu_list.list_revision():
            return False

        new, changed, deleted_ids, meta_changed = self.detect_changed_tasks()
        for iid in deleted_ids:
            self.remove_item_by_id(iid)

        for task in new:
            self.new_item(task)

        for task in changed:
            self.update_item(task)

        if meta_changed:
            self.meta.sync()

        self.update_meta()

        return len(new) + len(changed) + len(deleted_ids) > 0 or meta_changed

    def update_meta(self):
        shop_items = [item.selected_shop_item() for item in self.shop_items.values() if item.synced()]
        price = 0
        for s in shop_items:
            price += s.amount * s.price

        self.meta.set_price(price)

    def detect_changed_tasks(self):
        self.shop_list_rev = self.wu_list.list_revision()
        new_tasks = self.wu_list.list_items()

        meta_changed = self.meta.detect_changes(new_tasks)

        changed = []
        new = []
        for new_task in new_tasks:
            if MetaShopItem.is_meta_item(new_task):
                continue
            iid = new_task['id']
            revision = new_task['revision']
            if iid in self.shop_task_revs:
                if self.shop_task_revs[iid] != revision:
                    self.shop_task_revs[iid] = revision
                    changed.append(new_task)
            else:
                self.shop_task_revs[iid] = revision
                new.append(new_task)

        deleted_ids = []
        for iid in self.shop_task_revs:
            found = False
            for new_task in new_tasks:
                if iid == new_task['id']:
                    found = True
                    break
            if not found:
                deleted_ids.append(iid)

        for iid in deleted_ids:
            self.shop_task_revs.pop(iid)

        return new, changed, deleted_ids, meta_changed

    def remove_item_by_id(self, iid):
        item = self.shop_items.pop(iid)
        self.logger.info("delete - " + item.name.encode('utf-8'))

        if item.synced():
            self.shop.delete(item.selected_shop_item())

    def new_item(self, task):
        self.logger.info("new - " + task['title'].encode('utf-8'))
        iid = task['id']
        item = self.wu_list.item_from_task(task)

        shop_items = self.shop.search(item.name, item.sub_name)
        item.set_shop_items(shop_items)
        if item.selected_item:
            self.choice.remember_choice(item)
        else:
            self.choice.match(item)

        if item.selected_item:
            self.shop.take(item.selected_shop_item())

        self.shop_items[iid] = item
        self.wu_list.update_item(task, item, rebuild_notes=True, rebuild_subs=True)

    def update_item(self, task):
        self.logger.info("Update - " + task['title'].encode('utf-8'))
        iid = task['id']
        item = self.wu_list.item_from_task(task)
        existing = self.shop_items[iid]

        if item != existing:
            self.remove_item_by_id(iid)
            self.new_item(task)
        else:
            update = False
            if item.synced() and not existing.synced():
                existing.select_shop_item(item.selected_shop_item())
                self.shop.take(existing.selected_shop_item())
                update = True
            if not item.synced() and existing.synced():
                self.shop.delete(existing.selected_shop_item())
                existing.select_shop_item(None)
                update = True

            if existing.amount != item.amount:
                existing.amount = item.amount
                if existing.synced():
                    self.shop.take(existing.selected_shop_item())
                    update = True
            if update:
                self.choice.remember_choice(existing)
                self.shop_task_revs[iid] = self.wu_list.update_item(task, existing)


class Choice:
    def __init__(self, file_name):
        self.file_name = file_name
        self.matches = self.load()

    def save(self):
        with open(self.file_name, 'w') as f:
            pickle.dump(self.matches, f)

    def load(self):
        try:
            with open(self.file_name) as f:
                return pickle.load(f)
        except IOError:
            return {}

    def remember_choice(self, item):
        if item.synced():
            self.matches[item.name] = item.selected_shop_item().name
            self.save()

    def match(self, item):
        if item.name in self.matches:
            shop_item_name = self.matches[item.name]
            for shop_item in item.shop_items:
                if shop_item.name == shop_item_name:
                    item.select_shop_item(shop_item)
