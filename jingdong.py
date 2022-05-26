# -*- coding: utf-8 -*-
"""
-------------------------------------------------
    Author: qinLess
    File: test.py
    Time: 2022/2/27 9:26 下午
-------------------------------------------------
    Change Activity: 2022/2/27 9:26 下午
-------------------------------------------------
    Desc: 
"""
import base64
import hashlib
from pydoc import resolve
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
client_version = '10.4.0'
client = 'android'

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

def get_ip():
    for i in range(3):
        url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions=&username=chukou01&spec=1'
        response = requests.get(url)
        if response.status_code == 200:
            print(response.text)
            ip = response.text
            ip = ip.replace('\n', '')
            ip = ip.replace('\r', '')
            if (test_proxy(ip)):
                return ip
    return None

def getip_uncheck():
    url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=0&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&username=chukou01&spec=1'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
        if '请添加白名单' in response.text:
            return None
        ip = response.text
        ip = ip.replace('\n', '')
        ip = ip.replace('\r', '')
        return ip

def test_proxy(proxy_ip, times=2):
    proxy = {
          'http': proxy_ip,
          'https': proxy_ip
        }
    url = "http://2021.ip138.com"
    head = {
        "sec-ch-ua-platform": "\"Windows\"",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-ch-ua": "\"Chromium\";v=\"94\", \"Microsoft Edge\";v=\"94\", \";Not A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "iframe",
        "Referer": "https://www.ip138.com/",
        "Accept-Encoding": "deflate, br"
    }
    for i in range(times):
        try:
            re = requests.get(url, headers=head, proxies=proxy, timeout=5)
            print('代理:' + proxy_ip + '可用')
            return True
        except:
            pass
        i += 1
    print('代理:' + proxy_ip + '不可用')
    return False


class jd:

    def __init__(self, ck, proxy_ip=None):
        self.ck = ck
        if proxy_ip == None:
            self.proxy = None
        else:
            self.proxy = {
                'http': proxy_ip,
                'https':proxy_ip 
            }

    def cart(self):
        LOG('==== cart ====')
        function_id = 'cart'
        ts = str(float(time.time() * 1000))
        body = '{"hdid":"","ts":' + ts + ',"ridx":-1,"cipher":{"body":""},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"}'
        sv = '120'
        client_version = '10.4.0'
        client = 'android'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            LOG('=== NETWOTK_ERROR ====')
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            LOG(resp.text)
            return SUCCESS, resp.text

    def test():
        function_id = 'cart'
        body = '{"addressId":"","appleCare":0,"businessId":"","cartBundleVersion":"9200","cartuuid":"","coord_type":"","cvhv":"","hitNewUIStatus":1,"homeWishListUserFlag":"3","latitude":"37.83512","longitude":"112.50392","mqTriggerStatus":"0","showPlusEntry":"2","syntype":"1","userType":"1"}'
        ts = str(int(time.time() * 1000))
        sv = '120'
        client_version = '10.4.0'
        client = 'android'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)

        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': ck
        }

        data = {
            'clientVersion': client_version,
            'client': client,
            'd_brand': client,
            'd_model': 'iPhone12,1',
            'osVersion': '14.1.3',
            'screen': '2392*1440',
            'uuid': uuid_str,
            'aid': uuid_str,
            'networkType': 'wifi',
            'wifiBssid': 'b2f80b2b651458871cec8df33057db68',
            'st': ts,
            'sign': sign,
            'sv': sv,
            'body': body
        }

        resp = requests.post(url=url + params, data=urlencode(data), headers=headers)
        print(resp.text)

    def cart_add(self, skuid):
        print('======== cart_add =========')
        sv = '120'
        function_id = 'cartAdd'
        ts = str(int(time.time() * 1000))
        body = '{"addressId":"","appleCare":0,"businessId":"","cartBundleVersion":"10400","cartuuid":"","cvhv":"","hitNewUIStatus":1,"homeWishListUserFlag":"3","mqTriggerStatus":"0","operations":[{"TheSkus":[{"Id":"' + skuid + '","num":"1","skuUuid":""}],"carttype":"3"}],"syntype":"1","updateTag":false,"userType":"1"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            if resp.status_code == 200:
                print(resp.text)
                return SUCCESS
        except:
            return NETWOTK_ERROR
        pass

    # get account address info
    def get_address(self):
        print('======== get_address =========')
        sv = '120'
        function_id = 'getAddressByPin'
        ts = str(int(time.time() * 1000))
        body = '{"isLastOrder":true,"latitudeString":"","longitudeString":"","settlementVersionCode":1600,"supportNewParamEncode":true}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            print(resp.text)
            if ret_json['addressList'] == '':
                return CK_NO_ADDRESS, None
            return SUCCESS, json.dumps(ret_json['addressList'][0])
        return RET_CODE_ERROR, None


    def current_order(self, good_id, order_str):
        print('======= current_order =======')
        sv = '120'
        function_id = 'currentOrder'
        ts = str(int(time.time() * 1000))
        body = '{"CartStr":{"TheSkus":[{"Id":"' + good_id + '","num":"1"}]},"OrderStr":"' + order_str + '",' + \
            '"addressGlobal":true,"addressTotalNum":1,"appEID":"","cartAdd":{"extFlag":{"balance_locServiceList":"[]","carModelId":"",' + \
            '"qualiId":""},"wareId":"","wareNum":"1"},"decryptType":"2","giftType":0,"hasDefaultAddress":true,"hasSelectedOTC":"0",' + \
            '"isLastOrder":true,"isRefreshOrder":false,"isSupportAllInvoice":true,"operationType":0,"otcMergeSwitch":"1",' + \
            '"settlementVersionCode":1600,"skuSource":0,"sourceType":2,"supportAllEncode":true,"supportNewParamEncode":true,"wareId":"","wareNum":1}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR
        return SUCCESS

    def submit_order(self, good_id, order_str):
        print('======= submit_order ========')
        sv = '120'
        function_id = 'submitOrder'
        ts = str(int(time.time() * 1000))
        body= '{"AppKeplerParams":{"otherData":{"mopenbp5":""}},"CartStr":{"TheSkus":[{"Id":"' + good_id + '","num":"1"}]},"OrderStr":' + order_str + ',"SupportJdBean":true,"appEID":"","cartuuid":"","decryptType":"2","fk_appId":"com.jingdong.app.mall","fk_terminalType":"02","fk_traceIp":"10.1.10.1","jdvTime":"","se":"","settlementVersionCode":1600,"si":"","supportAllEncode":true,"supportNewParamEncode":true,"syntype":"1"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, ret_json['submitOrder']['OrderId']
            else:
                return CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def gen_app_payid(self, order_id, order_type, payable_price):
        print('gen_app_payid')
        order_id = str(order_id)
        order_type = str(order_type)
        payable_price = str(payable_price) + '.00'
        sv = '120'
        function_id = 'genAppPayId'
        raw_payinfo = 'jd_android_app4;' + order_id + ';' + order_type + ';' + payable_price + ';e53jfgRgd7Hk'
        pay_sign = md5(raw_payinfo.encode('utf-8')).hexdigest()
        ts = str(int(time.time() * 1000))
        body= '{"appId":"jd_android_app4","fk_aid":"","fk_appId":"com.jingdong.app.mall","fk_latitude":"",' + \
            '"fk_longtitude":"","fk_terminalType":"","fk_traceIp":"10.1.10.1","orderId":"' + order_id + '","orderType":"' + order_type + '",' + \
            '"orderTypeCode":"0","paySourceId":"0","payablePrice":"' + payable_price + '","paysign":"' + pay_sign + '","unJieSuan":"0"}'
        print(body)
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, ret_json['payId']
            else:
                return CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def pay_index(self, pay_id):
        print('pay_index')
        sv = '120'
        function_id = 'payIndex'
        ts = str(int(time.time() * 1000))
        body= '{"appId":"jd_android_app4","hasCyberMoneyPay":"0","hasHuaweiPay":"0","hasOCPay":"0","hasUPPay":"0","payId":"' + pay_id + '","supportNFC":"1"}'
        # body= '{"appId":"jd_android_app4","hasCyberMoneyPay":"0","hasHuaweiPay":"0","hasOCPay":"0","hasUPPay":"0","payId":"' + pay_id + '","supportNFC":"1"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            print(resp.text)
        except:
            return NETWOTK_ERROR
        # print(resp.text)
        # if resp.status_code == 200:
            # ret_json = json.loads(resp.text)
            # if ret_json['code'] == '0':
                # return SUCCESS
        # return RET_CODE_ERROR

    def cart_check_single(self, theskus):
        print('cart_check_single')
        sv = '120'
        function_id = 'cartCheckSingle'
        ts = str(int(time.time() * 1000))
        body = '{"addressId":"","appleCare":0,"businessId":"","cartBundleVersion":"10400","cartuuid":"","coord_type":"","cvhv":"","hitNewUIStatus":1,"homeWishListUserFlag":"3","latitude":"","longitude":"","mqTriggerStatus":"0","operations":[{"TheSkus":' + theskus + ',"carttype":""}],"syntype":"1","updateTag":false,"userType":"1"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        # print(body)
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            print(resp.text)
        except:
            return NETWOTK_ERROR

    def cart_remove(self, theskus):
        print('======= cart_remove =========')
        sv = '120'
        function_id = 'cartRemove'
        ts = str(float(time.time() * 1000))
        body = '{"addressId":"","appleCare":0,"businessId":"","cartBundleVersion":"10400","cartuuid":"","coord_type":"","cvhv":"","hitNewUIStatus":1,"homeWishListUserFlag":"3","latitude":"","longitude":"","mqTriggerStatus":"0","operations":[{"TheSkus":' + theskus + ',"carttype":""}],"syntype":"1","updateTag":false,"userType":"1"}'
        sv = '120'
        client_version = '10.4.0'
        client = 'android'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;android;version/10.4.0;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        LOG(body)
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR
        if resp.status_code == 200:
            # print(resp.text)
            return SUCCESS


    # success: https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx32e4d3446c02b4b5&redirect_uri=http%3A%2F%2Fpay.m.jd.com%2Fpay%2Fother-pay.html%3FappId%3Djd_android_app4%26payId%3D62d9529bb3694590b4b5e29502d969f4&response_type=code&scope=snsapi_base&state=123#wechat_redirect 
    def df_pay(self, pay_id):
        print('df_pay')
        sv = '120'
        function_id = 'weiXinDFPay'
        ts = str(int(time.time() * 1000))
        body= '{"appId":"jd_android_app4","payId":"' + pay_id + '"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;android;version/10.4.0;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            LOG(resp.text)
        except:
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                share_url = str(ret_json['shareInfo']['shareUrl'])
                # share_url = share_url.replace('jd_android_app4', 'jd_m_xnjyk')
                # share_url = share_url.replace('Fother-pay-jdpay', 'Fother-pay')
                return SUCCESS, share_url
        return RET_CODE_ERROR, None


    def df_pay_test(self, pay_id):
        print('df_pay')
        sv = '120'
        function_id = 'weiXinDFPay'
        ts = str(int(time.time() * 1000))
        body= '{"appId":"pg_android","payId":"' + pay_id + '"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}&client=pg_android'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            print(resp.text)
        except:
            return NETWOTK_ERROR, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, ret_json['shareInfo']['shareUrl']
        return RET_CODE_ERROR, None


    def confirm_recv(self, order_id):
        sv = '120'
        function_id = 'confirm'
        ts = str(int(time.time() * 1000))
        body= '{"deis":"dy","orderId":"' + order_id + '","orderType":"22","plugin_version":104000}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR
        print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS
        return RET_CODE_ERROR


    def yk_submit(self, user_id, phone, card_id, sku_id):
        print('========= yk_submit =========')
        ts = str(int(time.time() * 1000))
        url = 'https://api.m.jd.com/client.action?functionId=oilcardSubmitOrder&body=%7B%22userPin%22%3A%22' + user_id + \
            '%22%2C%22source%22%3A8%2C%22callId%22%3A%223c' + str(uuid.uuid4()) + '%22%2C%22voiceCode%22%3Anull%2C%22promotionDiscount%22%3A0' + \
            '%2C%22dongCouponPay%22%3A0%2C%22balancePay%22%3A0%2C%22phone%22%3A%22' + phone + '%22%2C%22salePrice%22%3A50500%2C%22promoRfId%22%3Anull' + \
            '%2C%22onlinePay%22%3A50500%2C%22jingdouPay%22%3A0%2C%22skuId%22%3A%22' + sku_id + '%22%2C%22payType%22%3A1%2C%22couponIds%22%3A%5B%5D%2C%22' + \
            'cardNum%22%3A%22' + card_id + '%22%2C%22brand%22%3A%222%22%2C%22jingCouponPay%22%3A0%2C%22facePrice%22%3A50000%7D&appid=youka_H5&client=youka_H5' + \
            '&clientVersion=1.0.0&jsonp=jsonp_' + ts + '_98652'
        print(unquote(url))
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        try:
            resp = requests.post(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = resp.text.split('(')[1]
            ret_json = ret_json.split(')')[0]
            ret_json = json.loads(ret_json)
            if ret_json['msg'] == 'SUCCESS':
                return SUCCESS, ret_json['data']['orderId'], ret_json['data']['payId']
            else:
                return CK_UNVALUE, None, None
        return RET_CODE_ERROR, None, None







    def web_getunpay(self, amount, order_id):
        print('web_getunpay')
        amount = str(int(amount) * 100)
        ts = str(int(time.time() * 1000))
        url = 'https://wq.jd.com/bases/orderlist/list?order_type=1&start_page=1&last_page=0&page_size=10&callersource=mainorder&t=' + \
                ts + '&traceid=&_=' + ts + '&sceneval=2&g_login_type=1&callback=list_Cb&g_ty=ls'
        # url = 'https://wq.jd.com/bases/orderlist/list?order_type=1&start_page=1&last_page=0&page_size=10&callersource=mainorder&t=1646124297507&traceid=1399508969181056390&_=1646124297509&sceneval=2&g_login_type=1&callback=list_Cb&g_ty=ls'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'x-requested-with': 'com.ajiejd',
            'referer': 'https://wqs.jd.com/order/orderlist_merge.shtml?sceneval=2',
            'cookie': self.ck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        print(resp.text[0:1000])
        if resp.status_code == 200:
            ret_json = json.loads(resp.text.replace('list_Cb(', '').replace(')', ''))
            if ret_json['errCode'] == '0':
                order_list = ret_json['orderList']
                for order in order_list:
                    print(order['orderId'])
                    print(order['factPrice'])
                    factprice = str(int(int('10001')/100) * 100)
                    if str(order_id) == order['orderId']:
                        print('===========', order['orderId'])
                        return SUCCESS, order['orderId']
            elif ret_json['errCode'] == '13':
                return WEB_CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def web_jdappmpay(self, deal_id):
        print('web_jdappmpay')
        url = 'https://wq.jd.com/jdpaygw/jdappmpay?dealId=' + deal_id + '&backUrl=' + \
            'https%3A%2F%2Fwqs.jd.com%2Forder%2Fpaysuc.shtml%3FdealId%3D' + deal_id + '%26normal%3D1%26sourcefrom%3Dorder&' + \
            'r=&traceid=&_=&sceneval=2&g_login_type=1&callback=jdappmpay_Cb&g_ty=ls'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'x-requested-with': 'com.ajiejd',
            'referer': 'https://wqs.jd.com/order/orderlist_merge.shtml?sceneval=2',
            'cookie': self.ck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        print(resp.text)
        ret = resp.text.replace('jdappmpay_Cb(', '')
        ret = ret.replace(')', '')
        print(ret)
        ret_json = json.loads(ret)
        if ret_json['errno'] == 0 and ret_json['msg'] == '':
            return SUCCESS, ret_json['data']['jumpurl']
        else:
            return WEB_CK_UNVALUE, None


    def web_cpay_newpay(self, pay_id):
        print('web_cpay_newpay')
        url = 'https://pay.m.jd.com/cpay/newPay-index.html?payId=' + pay_id + '&appId=jd_m_pay&sceneval=2&jxsid=&__navVer=1'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'x-requested-with': 'com.ajiejd',
            'referer': 'https://wqs.jd.com/order/orderlist_merge.shtml?sceneval=2',
            'cookie': self.ck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR
        if resp.status_code == 200:
            return SUCCESS
        return RET_CODE_ERROR

    def web_newpay(self, pay_id):
        print('web_newpay')
        url = 'https://pay.m.jd.com/newpay/index.action'
        param = 'lastPage=https%3A%2F%2Fwqs.jd.com%2Forder%2Forderlist_merge.shtml%3Fsceneval%3D2&appId=jd_m_pay&payId=' + pay_id + '&_format_=JSON'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://pay.m.jd.com',
            'referer': 'https://pay.m.jd.com/cpay/newPay-index.html?payId=' + pay_id + '&appId=jd_m_pay&sceneval=2&jxsid=&__navVer=1',
            'cookie': self.ck
        }
        try:
            resp = requests.post(url=url, headers=headers, data=param, proxies=self.proxy)
        except:
            return NETWOTK_ERROR
        if resp.status_code == 200:
            return SUCCESS
        return RET_CODE_ERROR


    def web_wxpay(self, pay_id):
        url = 'https://pay.m.jd.com/index.action?functionId=wapWeiXinPay&body=%7B%22__navVer%22%3A%221%22%2C%22jxsid%22%3A%22%22%2C%22sceneval%22%3A%222%22%2C%22appId%22%3A%22jd_m_pay%22%2C%22payId%22%3A%22' + pay_id + '%22%2C%22eid%22%3A%22%22%7D&appId=jd_m_pay&payId=' + pay_id + '&_format_=JSON'
        print(url)
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'referer': 'https://pay.m.jd.com/cpay/newPay-index.html?payId=' + pay_id + '&appId=jd_m_pay&sceneval=2&jxsid=&__navVer=1',
            'cookie': self.ck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            print(resp.text)
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, ret_json['deepLink']
            else:
                return CK_PAY_FAIL, None
        return RET_CODE_ERROR, None

    def gen_token(self, url):
        sv = '120'
        function_id = 'genToken'
        ts = str(int(time.time() * 1000))
        body= '{"to":"' + quote(url, safe='') + '"}'
        # body = '{"to":"https%3a%2f%2fplogin.m.jd.com%2fjd-mlogin%2fstatic%2fhtml%2fappjmp_blank.html"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            print(resp)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, str(ret_json['tokenKey'])
        return RET_CODE_ERROR       

    def submit_appstore(self, skuid, price):
        url = 'https://gamerecg.m.jd.com/game/submitOrder.action'
        data = 'chargeType=13759&skuId=' + skuid + '&brandId=999440&payPwd=&customs=&gamearea=&gamesrv=&accounttype=&chargetype=&eid=&skuName=App&buyNum=1&type=1&couponIds=&useBean=&payMode=0&totalPrice=' + price
        headers = {
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'x-requested-with': 'com.jingdong.app.mall',
            'origin': 'https://gamerecg.m.jd.com',
            'content-type': "application/x-www-form-urlencoded",
            'cookie': self.ck
        }
        print(data)
        try:
            resp = requests.post(url=url, data=data, headers=headers, proxies=self.proxy, allow_redirects=False)
            # resp = requests.post(url=url, data=data, headers=headers, proxies=self.proxy)
            print(resp.status_code)
            print(resp.text)
            print(resp.headers)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR
        if resp.status_code == 302:
            if 'payId' in resp.headers['location']:
                return SUCCESS
        return CK_UNVALUE




def clear_cart(jd_client):
    print('======= clear_cart ======')
    code, info = jd_client.cart()
    if code != SUCCESS:
        return code
    if 'vendors' not in info:
        print('cart is empty')
        return code
    cart_info = json.loads(info)
    theskus = []
    for vendor in cart_info['cartInfo']['vendors']:
        sorted = vendor['sorted']
        for sort_item in sorted:
            item = sort_item['item']
            skuuid = item['skuUuid']
            id = item['Id']
            num = str(item['Num'])
            skus = {
                'Id': id,
                'num': num,
                'skuUuid': skuuid
            }
            theskus.append(json.dumps(skus))
    theskus = str(theskus).replace('\'', '')
    code = jd_client.cart_remove(theskus)
    return code
    

def create_order(account, ck, amount, good_id):
    LOG('====create_order=== ' , account )
    proxy_ip = get_ip()
    if proxy_ip == None:
        return NETWOTK_ERROR, None, None
    jd_client = jd(ck, proxy_ip)
    code = jd_client.cart_add(good_id)
    if code != SUCCESS:
        return code, None, None
    code, address = jd_client.get_address()
    if code != SUCCESS:
        return code, None, None
    code = jd_client.current_order(good_id, address)
    if code != SUCCESS:
        return code, None, None
    code, order_id = jd_client.submit_order(good_id, address)
    if code != SUCCESS:
       return code, None, None   
    # LOG('submit order:', order_id)
    code, order_id = jd_client.web_getunpay(amount, order_id)
    if code != SUCCESS:
        # LOG('web ck is unvalue')
        return code, None, None
    code, jump_url = jd_client.web_jdappmpay(order_id)
    if code != SUCCESS:
        return code, None, None
    # LOG(jump_url)
    pay_id = jump_url.split('payId=')[1].split('&')[0]
    # LOG(pay_id)
    code = jd_client.web_newpay(pay_id)
    if code != SUCCESS:
        return code, None, None
    code, pay_url = jd_client.web_wxpay(pay_id)
    if code != SUCCESS:
        return code, None, None
    return SUCCESS, pay_url, order_id

def create_df_order(account, ck, amount, good_id):
    LOG('====create_order=== ' , account )
    # proxy_ip = get_ip()
    # proxy_ip = getip_uncheck()
    # if proxy_ip == None:
        # return NETWOTK_ERROR, None, None
    proxy_ip = None
    jd_client = jd(ck, proxy_ip)
    # jd_client = jd(ck)
    code = clear_cart(jd_client)
    if code != SUCCESS:
        return NETWOTK_ERROR, None, None
    code = jd_client.cart_add(good_id)
    if code != SUCCESS:
        return code, None, None
    code, address = jd_client.get_address()
    if code != SUCCESS:
        return code, None, None
    code = jd_client.current_order(good_id, address)
    if code != SUCCESS:
        return code, None, None
    code, order_id = jd_client.submit_order(good_id, address)
    if code != SUCCESS:
       return code, None, None   
    code, pay_id = jd_client.gen_app_payid(order_id, '22', amount)
    if code != SUCCESS:
       return code, None, None   
    jd_client.pay_index(pay_id)
    code, pay_url = jd_client.df_pay(pay_id)
    if code != SUCCESS:
        return code, None, None
    return SUCCESS, pay_url, order_id

def create_waitpay_order(account, ck, amount, good_id):
    proxy_ip = getip_uncheck()
    if proxy_ip == None:
        return NETWOTK_ERROR, None, None
    jd_client = jd(ck, proxy_ip)
    # jd_client = jd(ck)
    code = clear_cart(jd_client)
    if code != SUCCESS:
        return NETWOTK_ERROR, None, None
    code = jd_client.cart_add(good_id)
    if code != SUCCESS:
        return code, None, None
    code, address = jd_client.get_address()
    if code != SUCCESS:
        return code, None, None
    code = jd_client.current_order(good_id, address)
    if code != SUCCESS:
        return code, None, None
    code, order_id = jd_client.submit_order(good_id, address)
    if code != SUCCESS:
       return code, None, None
    # code, pay_id = jd_client.gen_app_payid(order_id, '22', amount)
    # if code != SUCCESS:
    #    return code, None, None   
    # jd_client.pay_index(pay_id)
    # code, pay_url = jd_client.df_pay(pay_id)
    # if code != SUCCESS:
        # return code, None, None
    # return SUCCESS, pay_url, order_id


 
def create_df_order_test(account, ck, amount, good_id):
    LOG('====create_order=== ' , account )
    proxy_ip = get_ip()
    if proxy_ip == None:
        return NETWOTK_ERROR, None, None
    jd_client = jd(ck, proxy_ip)
    code, address = jd_client.get_address()
    if code != SUCCESS:
        return code, None, None
    code = jd_client.current_order(good_id, address)
    if code != SUCCESS:
        return code, None, None
    code, order_id = jd_client.submit_order(good_id, address)
    if code != SUCCESS:
       return code, None, None   
    code, pay_id = jd_client.gen_app_payid(order_id, '99', amount)
    if code != SUCCESS:
       return code, None, None   
    jd_client.pay_index(pay_id)
    code, pay_url = jd_client.df_pay(pay_id)
    if code != SUCCESS:
        return code, None, None
    return SUCCESS, pay_url, order_id
 
def pc_test():
    url = 'https://kami.jd.com/order/getJmiUrl/243798120543/39'
    ck = 'TrackID=1X8xAALyJawdGeT9hQ_53o1z5g9Z_0kV2OfCFaOZAW4luPclJd0MedAFUlK6Gkg0yje0vbzXWQYNAyNBuc3pWclkMrt5KC_Ag65_XKMjWkV2PfyU96ox50Qs3D4Gi3UQQ'
    head = {
        'Referer': 'https://order.jd.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
        'Cookie': ck
    }
    res = requests.get(url, headers=head)
    print(res.text)
    print(res.headers)


if __name__ == '__main__':
    good_id = '10045398811484'
    amount = '103'
    good_id_206 = '10045398948206'
    good_id_309 = '10045399054885'

    # ck = 'guid=4cc65ef73044e4b6d9ebc28504f045c14c7cb58fa4adf7f6ff5487aee0f4afe0; pt_key=app_openAAJiJLg9ADBrCoEvieCKoWXOcQMHI38gSkJyE4d5UOT8_bxD31V6-VO3V1MBfNcCiBaebT7iAhg; pt_pin=jd_vpFZBbkbmUDj; pwdt_id=jd_vpFZBbkbmUDj; sid=b28c104e4a1a8b40d0ba62fb8efc2c7w; pin=jd_vpFZBbkbmUDj; wskey=AAJhxu6tAEApGfg7qm4G3qC793tIFd6VALD089ojkOCJrvfz2T-BqMBzjxEvG1lgWNI6o_C0f-u94g5RMwdaWSVPhP8eCN1e'

    ck = 'pin=jd_44caafd969f84; wskey=AAJiJa5TAED47O93IqYS3ZE8MLHQoY2ji-jVgpACm8A2EDKvUM3ydLUaOatBSCgRdCeWrJqwj-TGphznd6MnofyfjDNrxk3T;'
    for i in ck.split(';'):
        if 'pt_pin' in i:
            user = i.split('=')[1].strip()

    # ck = 'pin=jd_4669b501d6aaf; wskey=AAJiJa7kAECULkYddy8LrrDHTs41P3qFSsOi2rI2AInyJFKO0YpF3fRkG3Zc1zAAESOYWvbGqUyg8CmVRV3-sYeYJG2tH5Vj;'

    # ck = 'pin=jd_4d9b500034155; wskey=AAJiYEIdAED5b-Vp4EDWh0KvEwEIbqyh4GXv7EFT_FmuUwfVvqWRBxHw9h1S_CVOzcVyeIoghZG6qbhy7o_B455iPTM_cqaH'
    # ck = 'pin=%E7%BB%86%E5%85%AB%E5%AE%8C%E5%85%A5; wskey=AAJiNW1dAED4C_lIGM1bsmJQ8U5yBvkZ3O03FZl0-VyuBWqfspTeiEtOiMPtr7Rq4mquSrCznFtj6xaZlbwcgjcI8JWsaaPZ;'
    ck = 'pin=bb17108392702; wskey=AAJijhQVAEAUuK5yxaGAiLVqJz3vy2eDcw4Mbk13xp2KJWAMbw8Ni2ihRP8D9e-mIYOsLhbPWOLy8edS4GfgUOx6trKMts4f;'
    ck = 'pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E8%8A%B1%E4%B9%8B%E9%9F%B5%E5%9B%AD%E8%89%BA%E6%9C%89; wskey=AAJij2V5AFBDC74mQXCVuZ2Fhxt7ZV5oxTsT1D0oJMIgyjg-Aq-A-_vE1pboEP6E0AsSxg1tmF9IIaUnpyC0qjl3J_0uZc5SUQ3vwov6IS0oHwpXyzQUMA;'
    # ck = 'pin=aa17108392698; wskey=AAJiiSo3AEBJB-dWUsuCrAPJmoSgvQ0fVhJ6z5YTJ8TZLh2ZfXhQiLmwtgkG90h8Uq7tt-ydge_d2JwmyDuQ9JX_hpMOaeBK;'
    # ck = 'pin=%E7%BB%86%E5%9B%BA%E5%A8%9F%E8%8B%B1; wskey=AAJiNW1bAEDagQKqDECetiXtITfrWXlhk5Np-mL2RsRrGgsF0r_fs8ABYMKpfMxgTi5OrUhGUFIXPhp-oNRGCUIGVYt0tElE;'
    for i in ck.split(';'):
        if 'pin' in i:
            user = i.split('=')[1].strip()

    phone = '13356749345'
    amount = '505'
    id = '10047077591909'

    # create_df_order(user, ck, amount, id)
    # create_waitpay_order(user, ck, amount, id)

    # ip = get_ip()
    ip = None
    jd_client = jd(ck, ip)




    # code = jd_client.cart_add(good_id)
    # code, address = jd_client.get_address()
    # code = jd_client.current_order(good_id, address)
    # code, order_id_s = jd_client.submit_order(id, address)
    # url = 'weixin://wxpay/bizpayurl?pr=W0VhsEuzz'
    # url = 'https://wqs.jd.com/order/n_detail_jdm.shtml?deal_id=247761070918&sceneval=2'
    url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=48c18f25d448764fa41ce8138a42c7d76c91bff55c0588e17069616d75f8b376effddfd64321df81febbe99b0816b6c97fbd03300ab7e2ace58ab06ead2a3128ca6ce6e5705410517c18220000f4be1334af41273e8fe32548929db9a7001d32'
    status, token = jd_client.gen_token(url)
    pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
    print(pay_url)

    # jd_client.submit_appstore('11183343342', '100')

    # code, order_id, pay_id = jd_client.yk_submit(user, phone, card_id, id)
    # code, pay_id = jd_client.gen_app_payid(order_id, '22', amount)
    # jd_client.pay_index(pay_id)
    # code, pay_url = jd_client.df_pay(pay_id)
    # if code != SUCCESS:
    # print(pay_url)
        
    # jd_client.df_pay_test(pay_id)
    # jd_client.cart_add(good_id_309)
    # jd_client.cart()
    # jd_client.cart_remove()

    # create_df_order_test('', ck, amount, id)

    # create_order(ck, amount, good_id)
    # order_id = '237094591161'
    # confirm_recv(ck, order_id)
    # get_ip()
    # test_proxy('106.110.195.22:4264')
    # gen_app_payid('237172412720', '22', '206.00')
    # pc_test()