# -*- coding: utf-8 -*-
import base64
from cgi import print_directory
import hashlib
import time
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
import uuid
import requests
import json
from hashlib import md5

# ck = 'pin=jd_4d9b500034155;wskey=AAJiGxaRAEDyfsdhBlmqAMrbqNdctzFATFzy7Vz7yL0BM3sab-sf2vZW8visccwGzSPJ2rW4XLJ2rYsDEaPRVbtOBASmZeca;whwswswws=wFIRcJyGMvZtnzHnGmdkKEwwApu7kCbUjeZMtYPcVJt3L1Mei1Zg8r8MV4e9F0boa;unionwsws={"devicefinger":"eidA8f8f8120cds10KoCHNU0TZ678jnQ7RG0gtCqA5wPA+GhsjzzH4trRGr+spYPXNa+80JjjsCXkWXo8SJXT+ok4+SC\/Y5plzZd89a3OWc+nWcNMiU3","jmafinger":"wFIRcJyGMvZtnzHnGmdkKEwwApu7kCbUjeZMtYPcVJt3L1Mei1Zg8r8MV4e9F0boa"};'
# ck = 'guid=90a4e8eb581c46800c0dc683b549f64180f19e5948f4c8b0da68643cf2537e5c; pt_pin=jd_OVOrCCjugivK;pt_key=app_openAAJiHdt9ADAZs-xzs_buSpo9LrWUvuI4ftCRnnYun3gmSeey6LTOfhwXcgsWEVlaiVSCbODrqZE; pwdt_id=jd_OVOrCCjugivK; sid=94ccb59b6262f3679ee18d594edf8e4w; pin=jd_OVOrCCjugivK; wskey=AAJgrI8rAECQVyDqdSqW1VcS2hi95qyv6De0-sAeBJLcgjJt_335Hyb9la4CIv-6THJkfsMJegW0wCt59ePb0km1BHS0QhaP'
client_version = '5.6.2'
build = '18780'
client = 'pg_android'

SUCCESS = 1
WEB_CK_UNVALUE = 2
CK_UNVALUE = 3
CK_PAY_FAIL = 4
NETWOTK_ERROR = 5
RET_CODE_ERROR = 6
CK_NO_ADDRESS = 7


def LOG(text, text1='', text2='', text3=''):
    print(text, text1, text2, text3)
    pass

def get_sign(text):
    text1 = text.encode()
    sl = [55, 146, 68, 104, 165, 61, 204, 127, 187, 15, 217, 136, 238, 154, 233, 90]
    sh = [56, 48, 51, 48, 54, 102, 52, 51, 55, 48, 98, 51, 57, 102, 100, 53]
    result = ''
    for i in range(len(text1)):
        v18 = sl[i & 15]
        r0 = ((v18 ^ text1[i]) ^ sh[i & 7]) + v18
        b1 = (v18 ^ r0)
        rr = b1 ^ sh[i & 7]
        result += hex(rr & 0xff).replace('0x', '').rjust(2, '0')
    md5_str = hashlib.md5(base64.b64encode(bytes.fromhex(result)))
    return md5_str.hexdigest()

def pingou_createorder():
    print('======== cart_add =========')
    sv = '120'
    function_id = 'pingou_wqvir_kmqb_createorder'
    ts = str(int(time.time() * 1000))
    body = '{"appId":null,"bizKey":null,"bizValue":null,"couponIdList":"","index":null,"jingdouCount":0,"pwd":"","qq":"1149375463","skuId":200144761539,"type":1}'
    uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
    sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&t={ts}'
    sign = get_sign(sign)
    print(sign)
    url = 'https://api.m.jd.com/client.action?functionId=' + function_id
    params = f'&clientVersion={client_version}&build={build}&client={client}&uuid={uuid_str}&t={ts}&sign={sign}'
    headers = {
        'charset': "UTF-8",
        'user-agent': "jdpingou",
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'cookie': ck
    }
    body = 'body=' + quote(body)
    try:
        resp = requests.post(url=url + params, data=body, headers=headers)
        if resp.status_code == 200:
            print(resp.text)
            return SUCCESS
    except:
        return NETWOTK_ERROR
    pass

ck = 'pin=jd_4d9b500034155;wskey=AAJhY_ouAEBdr1eQcLI4lGAtP4wpVNP-j_EDveLeBqKHmNy9dr5SLNqhpv-1iAXeXRR7bdv6pshxlnRbVXLeXlfBgrIg1FlV;defaultHeadId=8212230;gHeadPlanId=33280;gHeadAddressId=1_2901_55555_0;gSId=4;gDSId=281;__jda=122270672.16344655393851189730149.1634465539.1634548027.1634549942.5;__jdv=122270672%7Cdirect%7C-%7Cnone%7C-%7C1634465539387|1634549966;unpl=;clientid=66f73810b5782a7b;_mkjdcn='

pingou_createorder()