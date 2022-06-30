from random import randint, random
import re
from time import sleep
import requests
import json
import threading

ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'

def LOG(text):
    print(text)
    pass

def callback(order_id):
    # url = 'http://175.178.150.157:9666/api/pay/callBack?offOrderNo=' + str(order_id)
    url = 'http://175.178.167.28:9666/api/pay/callBack?offOrderNo=' + str(order_id)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    res = requests.get(url, headers=head)
    if 'not exist' in res.text:
        return False
    LOG('callback:' + str(order_id) + res.text)
    return True

class callback_yunsheng:
    def __init__(self, ck):
        self.ck = ck
        # self.cookies_dict = requests.utils.dict_from_cookiejar(self.cks)
        
    def ids_login(self, url):
        pass

    def update_ck(self, headers):
        set_cookies = str(headers['set-cookie'])
        for i in set_cookies.split(';'):
            if i not in self.ck:
                self.ck = self.ck + '; ' + i
            for j in str(self.ck).split(';'):
                if i.split('=')[0] == j.split('=')[0]:
                    self.ck = self.ck.replace(j, i)
        # print(self.ck)


    def get_list(self, limit):
        url = 'https://jdcardsys.whkv.net/user/order/oil.html?page=1&limit=' + limit
        head = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://jdcardsys.whkv.net/user/order/oil.html',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'accept-encoding': 'gzip, deflate, br',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
            'cookie': self.ck
        }
        # self.cookies_dict = requests.utils.dict_from_cookiejar(self.cks)
        res = requests.get(url, headers=head)
        if res.status_code == 200:
            self.update_ck(res.headers)
            ret_json = json.loads(res.text)
            if '您尚未登录' in ret_json['msg']:
                print('未登录,请更新店铺后台cookie')
                return None
            if "获取成功" in ret_json['msg']:
                print('回调任务正常执行中...')
                return ret_json['data']
            else:
                print(ret_json['msg'])
                return None
        return None
    
    def callback_orders(self, orders):
        threads = []
        for order in orders:
            t = threading.Thread(target=callback, args=(order['fillOrderNo'], ))
            threads.append(t)
        for t in threads:
            t.start()
        for i in threads:
            t.join()

def callback_task(ck):
    callback_client = callback_yunsheng(ck)
    while(True):
        try:
            orders = callback_client.get_list('30')
            if orders == None:
                return
            callback_client.callback_orders(orders)
            sleep(randint(9,15))
        except:
            print('unknow error')

# ck = ''
ck = 'PHPSESSID=8789f16a6949a3f22a6b697a4ccc37a6; security_session_verify=64cab70a8023993eea77ee45362a9cd1'
callback_task(ck)
