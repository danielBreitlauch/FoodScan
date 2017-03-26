import requests
import json
from time import sleep


class AntiCaptcha:

    def __init__(self, api_key):
        self.api_key = api_key
        self.url = 'https://api.anti-captcha.com/'
        self.header = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json'
        }

    def create(self, website_url, website_key):
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": website_url,
                "websiteKey": website_key
            }
        }

        response = requests.post(self.url + 'createTask', json.dumps(data), self.header).json()
        if response['errorId'] == 0:
            return response['taskId']

    def result(self, task_id):
        data = {
            "clientKey": self.api_key,
            "taskId": task_id
        }

        response = requests.post(self.url + 'getTaskResult', json.dumps(data), self.header).json()
        if response['errorId'] == 0:
            if response['status'] == "processing":
                sleep(5)
                return self.result(task_id)
            if response['status'] == "ready":
                return response['solution']['gRecaptchaResponse']

    def balance(self):
        response = requests.post(self.url + 'getBalance', json.dumps({"clientKey": self.api_key}), self.header).json()
        if response['errorId'] == 0:
            return response['balance']
        return None
