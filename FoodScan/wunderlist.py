# -*- coding: utf-8 -*-
from FoodScan.ShopList import ShopList
from FoodScan.ShopSync.metaShop import MetaShopItem
from FoodScan.items import *
import wunderpy2
from pysimplelog import Logger

import requests
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'


class WuList(ShopList):

    def __init__(self, config):
        ShopList.__init__(self)
        self.logger = Logger('Wunderlist')
        self.client = wunderpy2.WunderApi().get_client(config['wunderlist_token'], config['wunderlist_client_id'])
        self.list_id = config['wunderlist_list_id']

    def is_meta_item(self, task):
        return MetaShopItem.is_meta_item(task)

    def create_web_hook(self, url, port):
        hooks = self.client.get_webhooks(self.list_id)
        for hook in hooks:
            self.client.delete_webhook(hook['id'], 0)

        self.client.create_webhook(self.list_id, url + ":" + str(port), "generic")

    def list_tasks(self):
        return self.client.get_tasks(self.list_id)

    def list_revision(self):
        return self.client.get_list(self.list_id)['revision']

    def task_sub_tasks(self, iid):
        return self.client.get_task_subtasks(iid)

    def item_from_task(self, task, with_selects=True):
        notes = self.client.get_task_notes(task['id'])
        notes = notes[0]['content'] if len(notes) > 0 else u""

        sub_tasks = self.client.get_task_subtasks(task['id']) if with_selects else []
        return Item.parse(task['title'], notes, sub_tasks)

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
        else:
            for sub in self.client.get_task_subtasks(iid):
                for sub_item in item.sub_items():
                    if sub_item.title() == sub['title']:
                        self.client.update_subtask(sub['id'], sub['revision'], completed=sub_item.selected())
                        break

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

    def delete_item(self, task):
        while True:
            try:
                new_revision = self.client.get_task(task['id'])['revision']
                self.client.delete_task(task['id'], new_revision)
                return
            except ValueError:
                pass

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
