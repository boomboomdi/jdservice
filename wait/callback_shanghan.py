from cgi import print_directory
from random import randint, random
from time import sleep, time
import requests
import json
import threading

ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'

def LOG(text):
    print(text)
    pass

def callback(order_id):
    # print(order_id)
    url = 'http://175.178.150.157:9666/api/pay/callBack?offOrderNo=' + str(order_id)
    # url = 'http://175.178.167.28:9666/api/pay/callBack?offOrderNo=' + str(order_id)
    head = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    res = requests.get(url, headers=head)
    if 'not exist' in res.text:
        return False
    LOG('callback:' + str(order_id) + res.text)
    return True

class callback_shanghan:
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


    def get_list(self):
        url = 'http://oil.open.j5y.com/data?search=&_=' + str(int(time()) * 1000)
        head = {
            'Referer': 'http://oil.open.j5y.com/',
            'Content-type': 'application/json',
            'Accept-encoding': 'gzip, deflate, br',
            'Cookie': self.ck
        }
        # self.cookies_dict = requests.utils.dict_from_cookiejar(self.cks)
        order_list = []
        res = requests.get(url, headers=head)
        if res.status_code == 200:
            if 'fillOrderNo' in res.text:
                print('尚菡生活回调任务正常执行中...')
            ret_json = json.loads(res.text)
            for i in range(30):
                order_list.append(ret_json[i])
            return order_list
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
    callback_client = callback_shanghan(ck)
    while(True):
        try:
            orders = callback_client.get_list()
            if orders == None:
                return
            callback_client.callback_orders(orders)
            sleep(randint(9,15))
        except:
            print('unknow error')

# ck = 'session=.eJwdj0tuwzAMBe-idRYSPyaVyxgkRSFtgbawnVXQu1ftdh4GmPcq-zzyfJT7dTzzVva3Ue5FAcCkSncWrM5Maq7N0juAkg-ttbex2USYojn7HILAmYSdsw1lmE20MudY60gZDU2DFWnbDKEte6sdM1OgUyUIjohpUwi43ErY9xUPWzHHO9sfOI-5X18f-bkYSVhqHSgR5ODmgkS1qYdLI1T3AS6wvOeZx_-r9vMLGvNDfw.YiR3NQ.ZJryZam775sQMaa_HMN0OAoptZ0'
# ck = 'session=.eJwdj0tuwzAMBe-idRYSPyaVyxgkRSFtgbawnVXQu1ftdh4GmPcq-zzyfJT7dTzzVva3Ue5FAcCkSncWrM5Maq7N0juAkg-ttbex2USYojn7HILAmYSdsw1lmE20MudY60gZDU2DFWnbDKEte6sdM1OgUyUIjohpUwi43ErY9xUPWzHHO9sfOI-5X18f-bkYSVhqHSgR5ODm1T3AS6wvOeZx_-r9vMLGvNDfw.YiR3NQ.ZJryZam775sQMaptZ0'
ck = ''
callback_task(ck)

