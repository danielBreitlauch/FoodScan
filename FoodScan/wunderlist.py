# -*- coding: utf-8 -*-
from item import *
import wunderpy2
from pysimplelog import Logger


class WuList:
    def __init__(self, shop, code_check, bring, client_id, token, shop_list_id, bring_export_list_id):
        self.logger = Logger('Wunderlist')
        self.client = wunderpy2.WunderApi().get_client(token, client_id)
        self.bring = bring
        self.code_check = code_check
        self.shop = shop
        self.bring_export_list_id = bring_export_list_id
        self.shop_list_id = shop_list_id
        self.shop_list_rev = 0
        self.shop_task_revs = {}
        self.shop_items = {}

    def check_action(self):
        # self.transfer_bring_list_action()
        self.detect_shop_list_change()
        self.sync_list_shop()

    def sync_list_shop(self):
        cart_items = self.shop.cart()
        tasks = self.client.get_tasks(self.shop_list_id)
        shop_items = []

        for task in tasks:
            item = self.item_from_task(task, with_selects=True)
            shop_item = item.selected_shop_item()
            if shop_item:
                shop_items.append(shop_item)

        for shop_item in shop_items:
            if shop_item not in cart_items:
                self.logger.warn("Task item without shop item: " + shop_item.name)

        for cart_item in cart_items:
            if cart_item not in shop_items:
                self.logger.warn("Cart item without task: " + cart_item.name)

    def detect_shop_list_change(self):
        if self.shop_list_rev == self.client.get_list(self.shop_list_id)['revision']:
            return

        new, changed, deleted_ids = self.detect_changed_tasks()
        for iid in deleted_ids:
            self.remove_item_by_id(iid)

        for task in new:
            self.new_item(task, with_selects=True)

        for task in changed:
            self.update_item(task)

    def transfer_bring_list_action(self):
        tasks = self.client.get_tasks(self.bring_export_list_id)
        if len(tasks) > 0:
            items = []
            for task in tasks:
                items.append(self.item_from_task(task))
            self.bring.upload(items)
            for task in tasks:
                self.client.delete_task(task['id'], task['revision'])

    def add_barcode(self, barcode):
        item = self.code_check.get_description(barcode)

        for task in self.client.get_tasks(self.shop_list_id):
            if item.name in task['title']:
                existing = self.item_from_task(task)
                existing.inc_amount()
                self.client.update_task(task['id'], task['revision'], title=existing.title())
                # next round will detect change and update internal items and shop
                return

        task = self.client.create_task(self.shop_list_id, title=item.title())
        iid = task['id']
        self.client.create_note(iid, item.note())
        self.shop_items[iid] = item
        self.shop_task_revs[iid] = task['revision']

    def remove_item_by_id(self, iid):
        item = self.shop_items.pop(iid)
        self.logger.info("delete - " + item.name)

        if item.synced():
            self.shop.delete(item.selected_shop_item())

    def new_item(self, task, with_selects=False):
        self.logger.info("new - " + task['title'])
        iid = task['id']
        item = self.item_from_task(task, with_selects=with_selects)
        shop_items = self.shop.search(item.name)
        item.add_shop_items(shop_items)

        if len(shop_items) == 1 and not item.synced():
            item.select_shop_item(item.shop_items[0])
            self.shop.take(item.selected_shop_item())

        checked = []
        for sub in self.client.get_task_subtasks(iid):
            if sub['completed']:
                checked.append(ShopItem.parse(sub['title']))
            self.client.delete_subtask(sub['id'], sub['revision'])

        for shop_item in item.shop_items:
            comp = shop_item in checked or len(item.shop_items) == 1
            self.client.create_subtask(iid, unicode(shop_item), completed=comp)

        notes = self.client.get_task_notes(iid)
        if len(notes) == 1 and notes[0]['content'] != item.note():
            self.client.delete_note(notes[0]['id'], notes[0]['revision'])
        if len(notes) == 0:
            self.client.create_note(iid, item.note())

        self.shop_items[iid] = item
        while True:
            try:
                new_revision = self.client.get_task(iid)['revision']
                self.shop_task_revs[iid] = new_revision
                self.client.update_task(iid, new_revision, title=item.title())
                break
            except ValueError:
                pass

    def update_item(self, task):
        self.logger.info("Update - " + task['title'])
        iid = task['id']
        item = self.item_from_task(task, with_selects=True)
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
                new_revision = self.client.get_task(iid)['revision']
                self.shop_task_revs[iid] = new_revision
                self.client.update_task(iid, new_revision, title=existing.title())

    def detect_changed_tasks(self):
        self.shop_list_rev = self.client.get_list(self.shop_list_id)['revision']
        new_tasks = self.client.get_tasks(self.shop_list_id)
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

    def item_from_task(self, task, with_selects=False):
        notes = self.client.get_task_notes(task['id'])
        if len(notes) > 0:
            notes = notes[0]['content']
        else:
            notes = u""

        sub_filter = []
        if with_selects:
            for sub in self.client.get_task_subtasks(task['id'], completed=True):
                if sub['completed']:
                    sub_filter.append(sub)

        return Item.parse(task['title'], notes, sub_filter)
