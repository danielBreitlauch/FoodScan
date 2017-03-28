# -*- coding: utf-8 -*-
import pickle
from thread import start_new_thread
from time import sleep
import traceback
from pysimplelog import Logger

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple


class ShopSync:
    def __init__(self, shop, wu_list, web_hook_url=None, web_server_ip=None, web_server_port=8080, async=True):
        self.logger = Logger('ShopSync')
        self.shop = shop
        self.wu_list = wu_list
        self.shop_list_rev = 0
        self.shop_task_revs = {}
        self.shop_items = {}
        self.choice = Choice("choices.db")
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
        if self.shop_list_rev == self.wu_list.client.get_list(self.wu_list.list_id)['revision']:
            return False

        new, changed, deleted_ids = self.detect_changed_tasks()
        for iid in deleted_ids:
            self.remove_item_by_id(iid)

        for task in new:
            self.new_item(task)

        for task in changed:
            self.update_item(task)

        return len(new) + len(changed) + len(deleted_ids) > 0

    def detect_cart_list_differences(self):
        cart_items = self.shop.cart()
        tasks = self.wu_list.client.get_tasks(self.wu_list.list_id)
        shop_items = []
        change = False

        for task in tasks:
            item = self.wu_list.item_from_task(task)
            shop_item = item.selected_shop_item()
            if shop_item:
                shop_items.append(shop_item)
                if shop_item not in cart_items:
                    self.logger.warn("Task item without shop item: " + shop_item.name.encode('utf-8'))
                    change = True
                    existing = self.shop_items[task['id']]
                    if existing.selected_shop_item():
                        self.shop.take(existing.selected_shop_item())

        for cart_item in cart_items:
            if cart_item not in shop_items:
                self.logger.warn("Cart item without task: " + cart_item.name.encode('utf-8'))
        return change

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

        for sub in self.wu_list.client.get_task_subtasks(iid):
            self.wu_list.client.delete_subtask(sub['id'], sub['revision'])

        for shop_item in item.shop_items:
            self.wu_list.client.create_subtask(iid, unicode(shop_item), completed=shop_item.selected)

        notes = self.wu_list.client.get_task_notes(iid)
        if len(notes) == 1:
            if notes[0]['content'] != item.note():
                self.wu_list.client.delete_note(notes[0]['id'], notes[0]['revision'])
                self.wu_list.client.create_note(iid, item.note())
        else:
            self.wu_list.client.create_note(iid, item.note())

        self.shop_items[iid] = item
        while True:
            try:
                new_revision = self.wu_list.client.get_task(iid)['revision']
                self.shop_task_revs[iid] = new_revision
                self.wu_list.client.update_task(iid, new_revision, title=item.title())
                break
            except ValueError:
                pass

    def update_item(self, task):
        self.logger.info("Update - " + task['title'].encode('utf-8'))
        iid = task['id']
        item = self.wu_list.item_from_task(task, unmark=True)
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
                new_revision = self.wu_list.client.get_task(iid)['revision']
                self.shop_task_revs[iid] = new_revision
                self.wu_list.client.update_task(iid, new_revision, title=existing.title())

    def detect_changed_tasks(self):
        self.shop_list_rev = self.wu_list.client.get_list(self.wu_list.list_id)['revision']
        new_tasks = self.wu_list.client.get_tasks(self.wu_list.list_id)
        changed = []
        new = []
        for new_task in new_tasks:
            iid = new_task['id']
            revision = new_task['revision']
            if iid in self.shop_task_revs:
                if self.shop_task_revs[iid] != revision:
                    self.shop_task_revs[iid] = revision
                    changed.append(new_task)
            else:
                self.shop_task_revs[iid] = revision
                new.append(new_task)

        deleted = []
        for iid in self.shop_task_revs:
            found = False
            for new_task in new_tasks:
                if iid == new_task['id']:
                    found = True
                    break
            if not found:
                deleted.append(iid)

        for iid in deleted:
            self.shop_task_revs.pop(iid)

        return new, changed, deleted


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
