from requests import *

from FoodScan.ShopList import ShopList, Item
from FoodScan.items import is_int


class BringList(ShopList):

    bringRestURL = "https://api.getbring.com/rest/"
    bringUUID = ""
    bringListUUID = ""

    def __init__(self, config):
        ShopList.__init__(self)
        self.login(config['email'], config['password'])

        self.auth_headers = {
            'X-BRING-API-KEY': config['api_key'],
            'X-BRING-CLIENT': 'android',
            'X-BRING-USER-UUID': self.bringUUID,
            'X-BRING-VERSION': '303070050',
            'X-BRING-COUNTRY': 'de',
        }

    def is_meta_item(self, task):
        return False

    def create_web_hook(self, url, port):
        pass

    def list_tasks(self):
        items = get(self.bringRestURL + "bringlists/" + self.bringListUUID, headers=self.auth_headers).json()
        return items['purchase']

    def item_from_task(self, task, with_selects=True):
        if 'specification' in task and is_int(task['specification']):
            amount = int(task['specification'])
        else:
            amount = 1
        return Item(name=task['name'], amount=amount)

    def create_item(self, item):
        headers = self.auth_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        put(self.bringRestURL + "bringlists/" + self.bringListUUID, params={'purchase': item.name, 'specification': str(item.amount)}, headers=headers)

    def update_item(self, task, item, rebuild_notes=False, rebuild_subs=False):
        self.create_item(item)

    def delete_item(self, task):
        headers = self.auth_headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        put(self.bringRestURL + "bringlists/" + self.bringListUUID, params={'remove': task['name']}, headers=headers)

    def list_revision(self):
        raise NotImplementedError('users must define __str__ to use this base class')

    def task_sub_tasks(self, iid):
        raise NotImplementedError('users must define __str__ to use this base class')

    def task_position(self, iid, position):
        raise NotImplementedError('users must define __str__ to use this base class')

    def login(self, email, password):
        response = get(self.bringRestURL + "bringlists", params={'email': email, 'password': password})
        if response.status_code == 200:
            json = response.json()
            if json != "":
                self.bringUUID = json['uuid']
                self.bringListUUID = json['bringListUUID']
                return

        print("Wrong credentials")
        exit(1)

    def search(self, name):
        return get(self.bringRestURL + "bringlistitemdetails/", params={'listUuid': self.bringListUUID, 'itemId': name}, headers=self.auth_headers).json()

    def lists(self):
        return get(self.bringRestURL + "bringusers/" + self.bringUUID + "/lists", headers=self.auth_headers).json()

    def user_settings(self):
        return get(self.bringRestURL + "bringusersettings/" + self.bringUUID, headers=self.auth_headers).json()
