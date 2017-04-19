# -*- coding: utf-8 -*-
from FoodScan.items import *
import wunderpy2
from pysimplelog import Logger

import requests
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'


class WuList:
    def __init__(self, client_id, token, list_id):
        self.logger = Logger('Wunderlist')
        self.client = wunderpy2.WunderApi().get_client(token, client_id)
        self.list_id = list_id

    def create_web_hook(self, url, port):
        hooks = self.client.get_webhooks(self.list_id)
        for hook in hooks:
            self.client.delete_webhook(hook['id'], 0)

        self.client.create_webhook(self.list_id, url + ":" + str(port), "generic")

    def item_from_task(self, task, with_selects=True, unmark=False, split=True):
        notes = self.client.get_task_notes(task['id'])
        notes = notes[0]['content'] if len(notes) > 0 else u""

        sub_tasks = self.client.get_task_subtasks(task['id']) if with_selects else []

        item = Item.parse(task['title'], notes, sub_tasks)
        #if split:
        #    self.split_items(item, task['id'], sub_tasks, unmark)
        return item

    def create_item(self, item):
        task = self.client.create_task(self.list_id, title=item.title())
        iid = task['id']
        if item.note():
            self.client.create_note(iid, item.note())

        if item.position():
            self.task_position(iid, item.position())

        for s in item.sub_items():
            self.client.create_subtask(iid, s.title(), completed=s.selected())
        return iid

    def update_item(self, task, item, rebuild_notes=False, rebuild_subs=False):
        iid = task['id']

        if rebuild_subs:
            for sub in self.client.get_task_subtasks(iid):
                self.client.delete_subtask(sub['id'], sub['revision'])

            for sub_item in item.sub_items():
                self.client.create_subtask(iid, sub_item.title(), completed=sub_item.selected())

        if rebuild_notes:
            notes = self.client.get_task_notes(iid)
            if len(notes) == 1:
                if notes[0]['content'].encode('utf-8') != item.note():
                    self.client.delete_note(notes[0]['id'], notes[0]['revision'])
                    if item.note():
                        self.client.create_note(iid, item.note())
            else:
                if item.note():
                    self.client.create_note(iid, item.note())

        if 'title' in task and item.title() != task['title']:
            while True:
                try:
                    new_revision = self.client.get_task(iid)['revision']
                    resp = self.client.update_task(iid, new_revision, title=item.title())
                    return resp['revision']
                except ValueError:
                    pass

        if rebuild_notes or rebuild_subs:
            return self.client.get_task(iid)['revision']
        else:
            return task['revision']

    def task_position(self, iid, position):
        pos = self.client.get_task_positions_objs(self.list_id)[0]
        v = pos['values']
        if len(v) <= abs(position) or iid != v[position]:
            if iid in v:
                v.remove(iid)
            if position == -1:
                v.append(iid)
            else:
                if position < 0:
                    position += 1
                v.insert(position, iid)
            self.client.update_task_positions_obj(pos['id'], pos['revision'], v)

    def split_items(self, item, iid, sub_tasks, unmark):
        task = self.client.get_task(iid)
        if task['completed']:
            self.logger.info("task got completed before split: " + item.name.encode('utf-8'))
            return

        selected_shop_items = [shop_item for shop_item in item.shop_items if shop_item.selected()]

        if 0 < len(selected_shop_items) < len(item.shop_items):
            if len(selected_shop_items) > 1:
                completed = True
                for t in sub_tasks:
                    completed = completed and t['completed']
                if completed:
                    self.logger.info("all subtasks completed before split: " + item.name.encode('utf-8'))
                    return

                while len(selected_shop_items) > 1:
                    shop_item = selected_shop_items.pop()
                    self.logger.info("splitting of: " + shop_item.name.encode('utf-8'))
                    new_item = Item(name=shop_item.name, price=shop_item.price, url=shop_item.link)
                    new_item.select_shop_item(shop_item)
                    self.create_item(new_item)
                    shop_item.select = False
                    if unmark:
                        for sub in sub_tasks:
                            if shop_item == ShopItem.parse(sub['title']):
                                self.client.update_subtask(sub['id'], sub['revision'], completed=False)
            item.select_shop_item(selected_shop_items.pop())
