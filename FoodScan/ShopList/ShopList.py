# -*- coding: utf-8 -*-
from FoodScan.items import *


class ShopList:

    def __init__(self):
        pass

    @abc.abstractmethod
    def is_meta_item(self, task):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def create_web_hook(self, url, port):
        raise NotImplementedError('users must define __str__ to use this base class')

    def list_tasks(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    def list_items(self):
        for task in self.list_tasks():
            if not self.is_meta_item(task):
                yield task, self.item_from_task(task)

    @abc.abstractmethod
    def list_revision(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def task_sub_tasks(self, iid):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def item_from_task(self, task, with_selects=True):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def create_item(self, item):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def update_item(self, task, item, rebuild_notes=False, rebuild_subs=False):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def delete_item(self, task):
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def task_position(self, iid, position):
        raise NotImplementedError('users must define __str__ to use this base class')
