# -*- coding: utf-8 -*-
from item import *
import wunderpy2


class WuList:

    def __init__(self, allyouneed, codecheck, bring, client_id, token, ayn_wunderlist_list_id, bring_export_list_id):
        self.bring = bring
        self.codecheck = codecheck
        self.allyouneed = allyouneed
        self.bring_export_list_id = bring_export_list_id
        self.ayn_list_id = ayn_wunderlist_list_id
        self.api = wunderpy2.WunderApi()
        self.client = self.api.get_client(token, client_id)
        self.ayn_list_rev = 0
        self.ayn_task_revs = {}
        self.ayn_items = {}

    def check_action(self):
        # self.transfer_bring_list_action()
        self.detect_ayn_list_change()
        # detect chosen variants
        #   add variant to ayn + check the item
        #   remember choice

    def detect_ayn_list_change(self):
        if self.ayn_list_rev == self.client.get_list(self.ayn_list_id)['revision']:
            return

        new, changed, deleted_ids = self.detect_changed_tasks()
        for iid in deleted_ids:
            self.remove_item_by_id(iid)

        for task in new:
            self.new_item(task)

        for task in changed:
            self.update_item(task)

    def transfer_bring_list_action(self):
        tasks = self.client.get_tasks(self.bring_export_list_id)
        if len(tasks) > 0:
            items = []
            for task in tasks:
                items.append(self.read_task(task))
            self.bring.upload(items)
            for task in tasks:
                self.client.delete_task(task['id'], task['revision'])

    def add_barcode(self, barcode):
        item = self.codecheck.get_description(barcode)

        for task in self.client.get_tasks(self.ayn_list_id):
            if item.name in task['title']:
                existing = self.item_from_task(task)
                existing.inc_amount()
                self.client.update_task(task['id'], task['revision'], title=existing.title())
                return

        task = self.client.create_task(self.ayn_list_id, title=item.title())
        iid = task['id']
        self.client.create_note(iid, item.note())
        self.ayn_items[iid] = item
        self.ayn_task_revs[iid] = task['revision']

    def remove_item_by_id(self, iid):
        item = self.ayn_items.pop(iid)
        if item.synced():
            self.allyouneed.delete(item.synced_shop_item())

    def new_item(self, task):
        iid = task['id']
        item = self.item_from_task(task)
        ayn_items = self.allyouneed.search(item.name)
        item.add_shop_items(ayn_items)

        if len(ayn_items) == 1 and not item.synced():
            item.set_synced()
            self.allyouneed.take(item.synced_shop_item())

        for sub in self.client.get_task_subtasks(iid):
            self.client.delete_subtask(sub['id'], sub['revision'])

        for ayn_item in ayn_items:
            self.client.create_subtask(iid, str(ayn_item.price / 100.0) + u'€ ' + ayn_item.name + u' (' + ayn_item.link + u')')

        notes = self.client.get_task_notes(iid)
        if len(notes) == 1 and notes[0]['content'] != item.note():
            self.client.delete_note(notes[0]['id'], notes[0]['revision'])
        if len(notes) == 0:
            self.client.create_note(iid, item.note())

        self.ayn_items[iid] = item
        new_revision = self.client.get_task(iid)['revision']
        self.ayn_task_revs[iid] = new_revision
        self.client.update_task(iid, new_revision, title=item.title())

    def update_item(self, task):
        iid = task['id']
        item = self.item_from_task(task)
        existing = self.ayn_items[iid]

        if item != existing:
            self.remove_item_by_id(iid)
            self.new_item(task)
        elif existing.amount != item.amount:
            existing.amount = item.amount
            if existing.synced():
                self.allyouneed.take(existing.synced_shop_item())

    def detect_changed_tasks(self):
        self.ayn_list_rev = self.client.get_list(self.ayn_list_id)['revision']
        new_tasks = self.client.get_tasks(self.ayn_list_id)
        changed = []
        new = []
        for new_task in new_tasks:
            iid = new_task['id']
            revision = new_task['revision']
            if iid in self.ayn_task_revs:
                if self.ayn_task_revs[iid] != revision:
                    self.ayn_task_revs[iid] = revision
                    changed.append(new_task)
            else:
                self.ayn_task_revs[iid] = revision
                new.append(new_task)

        deleted = []
        for iid in self.ayn_task_revs:
            found = False
            for new_task in new_tasks:
                if iid == new_task['id']:
                    found = True
                    break
            if not found:
                deleted.append(iid)

        for iid in deleted:
            self.ayn_task_revs.pop(iid)

        return new, changed, deleted

    def item_from_task(self, task):
        notes = self.client.get_task_notes(task['id'])
        if len(notes) > 0:
            notes = notes[0]['content']
        else:
            notes = u""

        return Item.parse(task['title'], notes)
