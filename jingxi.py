# -*- coding: utf-8 -*-
import base64
from distutils.command.build import build
from distutils.errors import LibError
from email import header
import hashlib
import time
from tkinter.messagebox import NO
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
import uuid
import requests
import json
from hashlib import md5
from jingdong import jd
from tools import LOG_D, parse_card_info, get_jd_account, getip_uncheck
from ip_sqlite import ip_sql
import re
from tools import get_area, LOG_D, getip_uncheck

client_version = '10.4.0'
client = 'android'

SUCCESS = 1
WEB_CK_UNVALUE = 2
CK_UNVALUE = 3
CK_PAY_FAIL = 4
NETWOTK_ERROR = 5
RET_CODE_ERROR = 6
CK_NO_ADDRESS = 7
from hashlib import sha256
import hmac
 
def LOG(text, text1='', text2='', text3=''):
    print(text, text1, text2, text3)
    pass

def bytes2hex(byte_arr: bytes) -> str:
    return ''.join(['%02x' % b for b in byte_arr])

def get_sign(data, key='9233a33500244a8eb90b17e1006b6af9'):
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    sign = hmac.new(key, message, digestmod=sha256).digest()
    sign = bytes2hex(sign)
    return sign

class jx:

    build = '18771'

    def __init__(self, ck, proxy_ip=None):
        self.ck = ck
        if proxy_ip == None:
            self.proxy = None
        else:
            self.proxy = {
                'http': proxy_ip,
                'https':proxy_ip 
            }

    def order_list(self):
        # url = 'https://api.m.jd.com/api?functionId=pingou_unideal_list&t=1657732912216&appid=wxsq_jdpingou&
        # 'clientVersion=5.6.0&build=18771&client=pg_android&d_brand=OnePlus&d_model=ONEPLUSA5010&osVersion=10&screen=2118*1080&partner=ucpp01&oaid=&openudid=66f73810b5782a7b&eid=eidA137f41225cl567c918d12a03e5be5952acde2eb34bb772fe8d9crEMaZE2xswsHa9ak6ta6of7VJB+51BaoziWy6zzNytcyfzpFR6ID/oPUIG+3&sdkVersion=29&lang=zh_CN&uuid=66f73810b5782a7b&aid=66f73810b5782a7b&networkType=wifi&wifiBssid=unknown&referer=wq.jd.com%2Fjdpingouapp%2Forderlist&sign=70c59327ebe4c398890d6d350b5fdc66f22df4623fe40da1c5c99888cfe5ae80'
        function_id = 'pingou_unideal_list'
        ts = str(int(time.time() * 1000))
        appid = 'wxsq_jdpingou'
        client_version = '5.6.0'
        client = 'pg_android'
        build = '18771'
        body = '{"callersource":"newbiz","last_page":0,"order_type":"3","page_size":10,"sceneval":"2","start_page":1}'
        sign = f'{appid}&{body}&{build}&{client}&{client_version}&{function_id}&{ts}'
        print(sign)
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/api?functionId=' + function_id
        params = f'&t={ts}&appid={appid}&clientVersion={client_version}&build={build}&client={client}&t={ts}&sign={sign}'
        url=url + params
        headers = {
            'charset': "UTF-8",
            'user-agent': "jdpingou",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        print(url)
        body = 'body=' + quote(body)
        print(body)
        try:
            resp = requests.post(url, data=body, headers=headers, proxies=self.proxy)
            print(resp.text)
        except:
            return NETWOTK_ERROR



if __name__ == '__main__':
    ck = 'pin=jd_4d9b500034155;wskey=AAJizuyLAEAyNCekQkBpn71NXGjZb-fQvibwJ5UYcTkxE5H5kBgFIbHfTOHEUt5AAS5pZntCQu7fimt1REzSU0Esev3N2ruv;'
    ck = 'pin=jd_4d9b500034155;wskey=AAJivYZfAEA9Kl4698fhBk5uBPVgm0D_CNhk9u7XBM0oaDlez_LvcYFlrWBHWVGWGXoCO6-GNrXReR3oFU_EAjzzaAvn4Y4X;'
    # ck = 'guid=3ec12f0b16179e693dd283b6da62cac02a6cb5c02195f6b2d78e75d243ec5ae5; pt_key=app_openAAJizw8nADDQ3P-brXs8_cFHBaGqHgNS4XxXMyk7qItBhziMBF2w8yU2Kq8C8aYSIAD6sxpk-Do; pt_pin=jd_YdfEMkJzddOf; pwdt_id=jd_YdfEMkJzddOf; sid=5fcb800f9981a174ebfa77e4104be56w; pin=jd_YdfEMkJzddOf; wskey=AAJhWsoxAECPB_0XvHSGz8IwmvHooMFWSpigsD9_kIpsAJlAYWhqFXY6pSgqUOj2U8i31vZyOYN4jr5IgUEKcIEAlPHVosFD'
    client = jx(ck)
    client.order_list()

    # a = '66f73810b5782a7b&wxsq_jdpingou&{"callersource":"newbiz","last_page":0,"order_type":"3","page_size":10,"sceneval":"2","start_page":1}&18771&pg_android&5.6.0&OnePlus&ONEPLUSA5010&eidA137f41225cl567c918d12a03e5be5952acde2eb34bb772fe8d9crEMaZE2xswsHa9ak6ta6of7VJB 51BaoziWy6zzNytcyfzpFR6ID/oPUIG 3&pingou_unideal_list&zh_CN&wifi&66f73810b5782a7b&10&ucpp01&wq.jd.com/jdpingouapp/orderlist&2118*1080&29&1657734941259&66f73810b5782a7b&unknown'
    # sign = get_sign(a)
    # print(sign)