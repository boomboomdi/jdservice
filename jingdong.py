# -*- coding: utf-8 -*-
import base64
from distutils.errors import LibError
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
from jd_app_web import get_ip
from tools import LOG_D, parse_card_info, get_jd_account, getip_uncheck
from ip_sqlite import ip_sql
import re

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
        # raw_payinfo = 'jd_iphone_app4;' + order_id + ';' + order_type + ';' + payable_price + ';e53jfgRgd7Hk'
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
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy, timeout=3)
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
        # body= '{"appId":"jd_android_app4","hasCyberMoneyPay":"0","hasHuaweiPay":"0","hasOCPay":"0","hasUPPay":"0","payId":"' + pay_id + '","supportNFC":"1"}'
        body= '{"appId":"jd_iphone_app4","hasCyberMoneyPay":"0","hasHuaweiPay":"0","hasOCPay":"0","hasUPPay":"0","payId":"' + pay_id + '","supportNFC":"1"}'
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
            if 'orderId' in resp.text:
                return SUCCESS, resp.json()['orderId']
        except:
            return NETWOTK_ERROR, None
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
                share_url = share_url.replace('jd_android_app4', 'jd_m_xnjyk')
                share_url = share_url.replace('Fother-pay-jdpay', 'Fother-pay')
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

    def web_jdappmpay(self, mck, deal_id):
        print('web_jdappmpay')
        url = 'https://wq.jd.com/jdpaygw/jdappmpay?dealId=' + deal_id + '&backUrl=' + \
            'https%3A%2F%2Fwqs.jd.com%2Forder%2Fpaysuc.shtml%3FdealId%3D' + deal_id + '%26normal%3D1%26sourcefrom%3Dorder&' + \
            'r=&traceid=&_=&sceneval=2&g_login_type=1&callback=jdappmpay_Cb&g_ty=ls'
        url = 'https://wq.jd.com/jdpaygw/jdappmpay?call=jdappmpay_cb&dealId=' + deal_id + '&ufc=&r=&backUrl=https%3A%2F%2Fwqs.jd.com&umpKey=jdappmpay&sceneval=2&traceid=&dataType=jsonp&callback=jdappmpay_cb'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'x-requested-with': 'com.ajiejd',
            'referer': 'https://wqs.jd.com/order/orderlist_merge.shtml?sceneval=2',
            'cookie': mck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR, None
        ret = resp.text.replace('jdappmpay_cb(', '')
        ret = ret.replace(')', '')
        # print(ret)
        ret_json = json.loads(ret)
        if ret_json['errno'] == 0 and ret_json['msg'] == '' and 'jumpurl' in resp.text:
            return SUCCESS, ret_json['data']['jumpurl']
        else:
            return CK_UNVALUE, None


    def web_cpay_newpay(self, mck, pay_id):
        print('web_cpay_newpay')
        url = 'https://pay.m.jd.com/cpay/newPay-index.html?payId=' + pay_id + '&appId=jd_m_pay&sceneval=2&jxsid=&__navVer=1'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'x-requested-with': 'com.ajiejd',
            'referer': 'https://wqs.jd.com/order/orderlist_merge.shtml?sceneval=2',
            'cookie': mck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except:
            return NETWOTK_ERROR
        if resp.status_code == 200:
            return SUCCESS
        return RET_CODE_ERROR

    def web_newpay(self, mck, pay_id):
        # print('web_newpay')
        url = 'https://pay.m.jd.com/newpay/index.action'
        param = 'lastPage=https%3A%2F%2Fwqs.jd.com%2Forder%2Forderlist_merge.shtml%3Fsceneval%3D2&appId=jd_m_pay&payId=' + pay_id + '&_format_=JSON'
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://pay.m.jd.com',
            'referer': 'https://pay.m.jd.com/cpay/newPay-index.html?payId=' + pay_id + '&appId=jd_m_pay&sceneval=2&jxsid=&__navVer=1',
            'cookie': mck
        }
        try:
            resp = requests.post(url=url, headers=headers, data=param, proxies=self.proxy)
            # print(resp.text)
        except:
            return NETWOTK_ERROR
        if resp.status_code == 200:
            return SUCCESS
        return RET_CODE_ERROR


    def web_wxpay(self, mck, pay_id):
        url = 'https://pay.m.jd.com/index.action?functionId=wapWeiXinPay&body=%7B%22__navVer%22%3A%221%22%2C%22jxsid%22%3A%22%22%2C%22sceneval%22%3A%222%22%2C%22appId%22%3A%22jd_m_pay%22%2C%22payId%22%3A%22' + pay_id + '%22%2C%22eid%22%3A%22%22%7D&appId=jd_m_pay&payId=' + pay_id + '&_format_=JSON'
        # print(url)
        headers = {
            'user-agent': "Mozilla/5.0 (Linux; Android 6; A31 Build/KTU84P; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
            'accept': '*/*',
            'referer': 'https://pay.m.jd.com/cpay/newPay-index.html?payId=' + pay_id + '&appId=jd_m_pay&sceneval=2&jxsid=&__navVer=1',
            'cookie': mck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
            # print(resp.text)
        except:
            return NETWOTK_ERROR
        if resp.status_code == 200:
            # print(resp.text)
            ret_json = json.loads(resp.text)
            if '交易受限' not in resp.text:
                    # return SUCCESS, ret_json['deepLink']
                    return SUCCESS
            else:
                return CK_UNVALUE
        return RET_CODE_ERROR

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
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy, timeout=2)
            print(resp)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, str(ret_json['tokenKey'])
        return RET_CODE_ERROR, None       

    def get_mck(self, token_url):
        t = str(int(time.time()))
        try:
            resp = requests.get(url=token_url, proxies=self.proxy, allow_redirects=False)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if 'pt_key' in resp.headers['Set-Cookie']:
            jda = '__jda=122270672.' + t + '3191886255148.' + t + '.' + t + '.' + t + '.8'
            for item in re.split(";|,| ", resp.headers['Set-Cookie']):
                if 'pt_key' in item:
                    pt_key = item
                if 'pt_pin' in item:
                    pt_pin = item
                # print(item)
            new_ck = pt_pin + ';' + pt_key + ';' + jda
            return SUCCESS, new_ck
        else:
            return CK_UNVALUE, None


    def submit_appstore(self, mck, skuid, price):
        url = 'https://gamerecg.m.jd.com/game/submitOrder.action'
        data = 'chargeType=13759&skuId=' + skuid + '&brandId=999440&payPwd=&customs=&gamearea=&gamesrv=&accounttype=&chargetype=&eid=&skuName=App&buyNum=1&type=1&couponIds=&useBean=&payMode=0&totalPrice=' + price
        headers = {
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'x-requested-with': 'com.jingdong.app.mall',
            'origin': 'https://gamerecg.m.jd.com',
            'content-type': "application/x-www-form-urlencoded",
            'referer': 'https://gamerecg.m.jd.com/?skuId=' + skuid,
            'cookie': mck
        }
        try:
            resp = requests.post(url=url, data=data, headers=headers, proxies=self.proxy, allow_redirects=False)
            # resp = requests.post(url=url, data=data, headers=headers, proxies=self.proxy)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 302:
            if 'payId' in resp.headers['location']:
                for item in resp.headers['location'].split('?')[1].split('&'):
                    if 'payId' in item:
                        return SUCCESS, item.split('=')[1]
        return CK_UNVALUE, None


    def get_appstore_detail(self, order_id):
        sv = '120'
        function_id = 'getGPOrderDetail'
        ts = str(int(time.time() * 1000))
        body= '{"apiVersion":"new","appKey":"android","orderId":"' + order_id + '","rechargeversion":"10.9","version":"1.10"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        body = 'body=' + quote(body)
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except Exception as e:
            LOG_D(e)
            return NETWOTK_ERROR, None, None
        if resp.status_code == 200:
            if '响应成功' in resp.text:
                result = resp.json()['result']
                LOG_D(resp.text)
                if result['orderStatus'] == 8 and result['orderStatusName'] == '交易完成':
                    card_info = result['cardInfos']
                    card_no, card_pass = parse_card_info(card_info)
                    return SUCCESS, card_no, card_pass
                else:
                    return SUCCESS, None, None
            else:
                return CK_UNVALUE, None, None
        return RET_CODE_ERROR, None, None

    def delete_order(self, order_id):
        sv = '120'
        function_id = 'delHistoryOrder'
        ts = str(int(time.time() * 1000))
        body= '{"deis":"dy","orderId":"' + order_id + '","plugin_version":104000,"recyle":"1"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        body = 'body=' + quote(body)
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            LOG_D(resp.text)
            if 'true' in resp.text:
                return SUCCESS, True
            else:
                return SUCCESS, False
        return RET_CODE_ERROR, None


    def knowledge_submit(self, repeat_key, skuid, amount, charge_num):
        url = 'https://xmlya.m.jd.com/submitOrder.action'
        submit_param = '{"couponIds":"","orderAmount":"' + amount + '.00","payType":"0","brand":"64","skuId":"' + skuid + \
            '","dongquanAmount":"","jingquanAmount":"","onlineAmount":"' + amount + '.00","rechargeNum":"' + charge_num + \
            '","repeatKey":"' + repeat_key + '","featureParam":{},"eid":""}'
        params = 'submitParam=' + quote(submit_param)
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        try:
            resp = requests.post(url=url, data=params, headers=headers)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            if 'orderId' in resp.text:
                return SUCCESS, resp.json()['orderId']
            else:
                LOG_D(resp.text)
                return CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def weixin_pay(self, pay_id):
        sv = '120'
        function_id = 'weixinPay'
        ts = str(int(time.time() * 1000))
        # body= '{"appId":"jd_android_app4","payId":"' + pay_id + '","sdkToken":""}'
        body= '{"appId":"jd_iphone_app4","payId":"' + pay_id + '","sdkToken":""}'
        # body= '{"appId":"jd_ios_app","payId":"' + pay_id + '","sdkToken":""}'
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
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy, timeout=4)
            print(resp.text)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if 'partnerId' in resp.text:
                nonce_str = ret_json['payInfo']['nonceStr']
                partner_id = ret_json['payInfo']['partnerId']
                prepay_id =  ret_json['payInfo']['prepayId']
                times = ret_json['payInfo']['timeStamp']
                sign = ret_json['payInfo']['sign']
                pay_url = 'weixin://app/wxe75a2e68877315fb/pay/?nonceStr=' + nonce_str + '&package=Sign%253DWXPay&' + \
                    'partnerId=' + partner_id + '&prepayId=' + prepay_id + '&timeStamp=' + times + '&sign=' + sign + '&signType=MD5'
                return SUCCESS, pay_url
            return CK_UNVALUE, None


    def xlmy_load(self, skuid):
        url = 'https://xmlya.m.jd.com/?skuId=' + skuid
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }       
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy, timeout=4)
            # print(resp.text)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            for line in resp.text.split('\n'):
                if 'repeatKey' in line:
                    line = line.replace(' ', '').replace('\n', '')
                    repeat_key = line.replace('<inputtype="hidden"id="repeatKey"value="', '').replace('"/>', '')
                    print(repeat_key)
                    return SUCCESS,repeat_key 
            return CK_UNVALUE, None

    def xmly_qb_submit(self, skuid, repeat_key, amount, qq):
        url = 'https://xmlya.m.jd.com/submitOrder.action'
        data = '{"couponIds":"","orderAmount":"' + amount + '.00","payType":"0","brand":"64","skuId":"' + skuid +   \
            '","dongquanAmount":"","jingquanAmount":"","onlineAmount":"' + amount + '.00","rechargeNum":"' + qq +   \
                '","repeatKey":"' + '","featureParam":{},"eid":"GKTFQWUAFQT4WWHBFAEWQV3N7B6D7GVPMF6RDXF674E2SRF2UHKKOWUGEZH6PLFQEIRLY6DYGYTJ5FYFW7WQQ63F5Q"}'
        data = 'submitParam=' + quote(data)
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }       
        try:
            resp = requests.post(url=url, headers=headers, data=data, proxies=self.proxy, timeout=4)
            print(resp.text)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if 'orderId' in resp.text:
            return SUCCESS, resp.json()['orderId']
        return CK_UNVALUE, None

    def xmly_gopay(self, order_id, amount):
        url = 'https://xmlya.m.jd.com/goPay.action?orderId=' + order_id + '&onlineAmount=' + amount + '.00'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }       
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy, timeout=4, allow_redirects=False)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 302:
            if 'payId' in resp.headers['location']:
                return SUCCESS, resp.headers['location']
        else:
            return CK_UNVALUE, None


    def query_pczorder_detail(self, order_id):
        sv = '120'
        function_id = 'queryPczOrderInfo'
        ts = str(int(time.time() * 1000))
        body= '{"apiVersion":"new","orderId":"' + order_id + '","rechargeversion":"10.9"}'
        uuid_str = hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[0:16]
        sign = f'functionId={function_id}&body={body}&uuid={uuid_str}&client={client}&clientVersion={client_version}&st={ts}&sv={sv}'
        sign = get_sign(sign)
        # print(sign)
        url = 'https://api.m.jd.com/client.action?functionId=' + function_id
        params = f'&clientVersion={client_version}&build=92610&client={client}&uuid={uuid_str}&st={ts}&sign={sign}&sv={sv}'
        headers = {
            'charset': "UTF-8",
            'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'cookie': self.ck
        }
        body = 'body=' + quote(body)
        # print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy, timeout=4)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None, None
        if resp.status_code == 200:
            if 'orderId' in resp.text:
                if resp.json()['result']['orderStatusName'] == '充值成功':
                    return SUCCESS, True, resp.json()['result']['orderStatusName']
                else:
                    return SUCCESS, False,resp.json()['result']['orderStatusName']
            return CK_UNVALUE, None, None
        return CK_UNVALUE, None, None




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
    proxy_ip = getip_uncheck()
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


APPSTORE_SKUIDS = {
    '100': '11183343342',
    '200': '11183368356',
    '500': '11183445154' 
}

def create_order_appstore(ck, amount, proxy):
    LOG_D('create_order_appstore')
    client = jd(ck, proxy)
    url = 'https://pay.m.jd.com'
    code, token = client.gen_token(url)
    if code != SUCCESS:
        return code, None
    token_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
    code, mck = client.get_mck(token_url)
    if code != SUCCESS:
        return code, None
    # print(mck)
    code, pay_id = client.submit_appstore(mck, APPSTORE_SKUIDS[amount], amount)
    if code != SUCCESS:
        return code, None
    LOG_D('payid ' + pay_id)
    code, order_id = client.pay_index(pay_id)
    if code != SUCCESS:
        return code, None
    # check pay 
    code, jump_url = client.web_jdappmpay(mck, order_id)
    LOG('jump_url: ' + str(jump_url))
    if code != SUCCESS:
        return code, None
    pay_id = jump_url.split('payId=')[1].split('&')[0]
    LOG('pay_id: ' + str(pay_id))
    code = client.web_newpay(mck, pay_id)
    if code != SUCCESS:
        return code, None
    code = client.web_wxpay(mck, pay_id)
    if code != SUCCESS:
        return code, None
    return code, order_id


def order_appstore(ck, order_me, amount):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = get_jd_account(ck)
    LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_id = create_order_appstore(ck, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    upload_order_result(order_me, order_id, amount, ck_status)


def upload_order_result(order_me, order_id, amount, ck_status):
    url = 'http://127.0.0.1:9191/api/preparenotify/notifyjdurl0069'
    head = {
        'content-type': 'application/json'
    }
    # data = '{"prepare_status": "1", "ck_status": "1", "order_me": "' + order_me + '", "order_pay": "247775877802", "amount": "' + amount + '", "qr_url": "https://pcashier.jd.com/image/virtualH5Pay?sign=d6e2869be73c243c560393c09a7182ca89a1ed515bb088cc3ca08658daa14a0a6d4f8399eb23e3c53f93c113731f840e7fbd03300ab7e2ace58ab06ead2a3128ca6ce6e5705410517c18220000f4be1334af41273e8fe32548929db9a7001d32"}'
    data = {
        'prepare_status': '1',
        'ck_status': ck_status,
        'order_me': order_me,
        'order_pay': order_id,
        'amount': amount,
        'qr_url': order_id
    }
    if order_id == None:
        data['prepare_status'] = '0'
    data = json.dumps(data)
    LOG_D(data)
    res = requests.post(url, headers=head, data=data)
    print(res.text)


def upload_callback_result(result):
    url = 'http://127.0.0.1:9191/api/ordernotify/notifyorderstatus0069'
    head = {
        'content-type': 'application/json'
    }
    res = requests.post(url, headers=head, data=result).json()
    LOG_D(str(result) + '\nret:' + json.dumps(res))
    if res['code'] == 0:
        return True
    else:
        return False


def query_order_appstore(ck, order_me, order_no, amount):
    result = {
        'check_status': '1',
        'pay_status': '0',
        'ck_status': '1',
        'time': str(int(time.time())),
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    account = get_jd_account(ck)
    LOG_D(account)
    proxy = ip_sql().search_ip(account)
    LOG_D(proxy)
    if proxy == None:
        proxy = getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        client = jd(ck, proxy)
        code, card_no, card_pass = client.get_appstore_detail(order_no)
        print('query', code)
        if code == SUCCESS:
            if card_no != None and card_pass != None:
                result['card_name'] = card_no
                result['card_password'] = card_pass
                result['pay_status'] = '1'
                result = json.dumps(result)
                if upload_callback_result(result):
                    client.delete_order(order_no)
                    return
            else:
                result = json.dumps(result)
                upload_callback_result(result)
                return
            return
        elif code == NETWOTK_ERROR:
            proxy = getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1


def query_order_appstore_immediate(ck, order_me, order_no, amount):
    result = {
        'check_status': '1',
        'pay_status': '0',
        'ck_status': '1',
        'time': str(int(time())),
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    account = get_jd_account(ck)
    LOG_D(account)
    proxy = ip_sql().search_ip(account)
    LOG_D(proxy)
    if proxy == None:
        proxy = getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        client = jd(ck, proxy)
        code, card_no, card_pass = client.get_appstore_detail(order_no)
        if code == SUCCESS:
            if card_no != None and card_pass != None:
                result['card_name'] = card_no
                result['card_password'] = card_pass
                result['pay_status'] = '1'
                result = json.dumps(result)
                return result
            else:
                result = json.dumps(result)
                return result
            return
        elif code == NETWOTK_ERROR:
            proxy = getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            return result
        i += 1


def get_real_url(ck, order_id):
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    order_url= 'https://wqs.jd.com/order/n_detail_jdm.shtml?deal_id=' + order_id + '&sceneval=2&appCode=ms0ca95114'
    account = get_jd_account(ck)
    proxy = ip_sql().search_ip(account)
    if proxy == None:
        proxy = getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        app_client = jd(ck, proxy)
        LOG_D(order_url)
        code, token = app_client.gen_token(order_url)
        LOG_D(token)
        if code == NETWOTK_ERROR:
            proxy = getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['msg'] = 'ck unvalue'
            break
        elif code == SUCCESS:
            pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
            result['code'] = '0'
            result['data'] = pay_url
            result['msg'] = 'success'
            return json.dumps(result)
        i += 1
    return json.dumps(result)


def get_ios_wx(ck, order_id, amount, proxy):
    app_client = jd(ck, proxy)
    code, pay_id = app_client.gen_app_payid(order_id, '22', amount)
    if code != SUCCESS:
        return code, None
    code, order_id = app_client.pay_index(pay_id)
    if code != SUCCESS:
        return code, None
    code, pay_url = app_client.weixin_pay(pay_id)
    if code != SUCCESS:
        return code, None
    return SUCCESS, pay_url
 

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

    # ck = 'pin=%E7%BB%86%E5%85%AB%E5%AE%8C%E5%85%A5; wskey=AAJiNW1dAED4C_lIGM1bsmJQ8U5yBvkZ3O03FZl0-VyuBWqfspTeiEtOiMPtr7Rq4mquSrCznFtj6xaZlbwcgjcI8JWsaaPZ;'
    # ck = 'pin=bb17108392702; wskey=AAJijhQVAEAUuK5yxaGAiLVqJz3vy2eDcw4Mbk13xp2KJWAMbw8Ni2ihRP8D9e-mIYOsLhbPWOLy8edS4GfgUOx6trKMts4f;'
    # ck = 'pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%91%AB%E9%80%B8%E8%BE%BE%E7%89%A9%E4%B8%9A%E7%AE%A1%E7%90%86; wskey=AAJikRpnAEBSn56VNxXKM7FGynMVwUvaTCjZomnscFak0591ObICL6VOKuCBPfsfrkDwvf8uLau2utGH51MGR_MqiqribS8e;'
    # ck = 'pin=jd_JYAGIAzaLlWQ; wskey=AAJikS2nAEBWoqcfP9P0dQWfq4Y87A8LhEdaAlG-tt00ruaKXhnh2QzpNMfedSEVydE-y3OYmHYP0W7AzoR0dm9Ae4AvfDct;'
    # ck = 'pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E4%BD%B3%E6%89%AC%E8%A3%85%E9%A5%B0%E8%A3%85%E6%BD%A2%E6%9C%89;wskey=AAJikkYfAFAgXEakpQ3A5vKOv_XopdQHyNXwOgIyWzinpb4vJ4pEa5Ys-xdfUsiLo_eBT29DW0ZnrPoBmOlokxBZij94z8zPMvFLrI6HibdzBRaF5zv_UQ;'
    # ck = 'pin=%E8%AE%B7%E6%B2%B3%E5%B8%82%E9%B8%BF%E5%85%89%E7%83%AD%E5%8A%9B%E6%9C%89;wskey=AAJikkyeAFDY6a4fMRVCTVaFKsoHTAhCY1ufcASTPbKbz6MOYnJ3jDL44hfLhXuFW5gbns6Pb49g9uk-Je-S3wo7hJn11O9s0lBnReZx4z_cvN4mV1is_Q;'
    # ck = 'pin=jd%5FsDveqlanuYKn; wskey=AAJhtG6AAECcTpsu-ewvhw_uxJEalmnkdyXGtNNwbzZa5hbdnDdwJMMlZmA3uAQcTYkgQlWOaybm2w5Rn9Il7IK4nKiqL1-P;'
    # ck = 'pin=jd%5FPYOgqPwlOxMn; wskey=AAJhyyLLAEDMeSKbEdcqVPiZIkBkyqyXfShegIcv_gDJ9V01t3tJI2JzhG89Ehm4hgJ4wxc_uphMF6RkE-F76DR-CnX_1ZO5;'
    # ck = 'pin=jd_765b4a1d1ff32; wskey=AAJiJgvJAEAqD_hptV7sjtQjXV_O2P1PWtq_EZBf5bhi-ySWDl0ujIGfXHpHEikn6ecmHyjdrBg5--2wwZHPbW_HTjPZmQYy;'
    # ck = 'pin=%E5%8E%82%E9%80%82%E5%9C%86%E5%8F%A3; wskey=AAJiNcxIAEDF-beA1xlTtXHYonRHXWpW9Qmr3IfFQBypNmmEkYOS-8Kuq4--9o2nsEaBWyWSOul-oBfiRhKn6-swns1Y1f8M;'
    # ck = 'pin=jd_7b3b6c0bfbbbf; wskey=AAJiik8NAEDle7sy1ILxFTBQezCHqbTaSnxCubDeI6R2JkKxzs3UxmCRKF3drtQLB5bwya1CWmqypqGYEwVD_03mK303Klxz;'
    # ck = 'pin=jd%5FqCfPeqttaRcc; wskey=AAJhyxAEAEA3Y_TXrqD3L1EqBnhX6cieCTwRYCWIp6rSsxsrmnCBYBnHgrfDpJqM8dc00WwLJYown0l-tuK5Ig3zZ_Qx554P;'
    # ck = 'pin=yNzZeCwSs; wskey=AAJiV5ZpAEBKFGrEnbFTW778jOez30cUmOHdMXTyb1ErXQfIEQnKsJD2arMPB1yOv_zxPevGpZfsNr6uaf2z2z1SqbByZcbI;'
    # ck = 'pin=aa17108392698; wskey=AAJiiSo3AEBJB-dWUsuCrAPJmoSgvQ0fVhJ6z5YTJ8TZLh2ZfXhQiLmwtgkG90h8Uq7tt-ydge_d2JwmyDuQ9JX_hpMOaeBK;'
    # ck = 'pin=%E7%BB%86%E5%9B%BA%E5%A8%9F%E8%8B%B1; wskey=AAJiNW1bAEDagQKqDECetiXtITfrWXlhk5Np-mL2RsRrGgsF0r_fs8ABYMKpfMxgTi5OrUhGUFIXPhp-oNRGCUIGVYt0tElE;'
    # ck = 'pin=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU; wskey=AAJirKsBAFDqkoJnxGdwAnNoctk5_ILxI_8WiDLFGDhkRnpKFFiorpY90yx-HREZuJtamaumlWhjxh1qDG9oiD6zwHH9GnOQrRnI-3iGx8OULGhXXrN53w; '
    # ck = 'pin=%E5%9F%8B%E6%B3%89%E4%B8%8B%E6%B3%A5%E9%94%80%E9%AA%A8ergJU; wskey=AAJirLjEAFDfO37k10JsQmjMPg8Z9A2mbifa69OSGVmNgY3_NsoO1luEUCcjMfEmC76zaLM9g8v_K3PU_76w9wEYVyXtrnzRyK2EWwcT38BbyuelafZ-oQ; '

    ck = 'pin=jd_4d9b500034155; wskey=AAJiqgJZAECd9g_DDWxJo3YPVOaYWwvDsU_BCxK7nZcTma51_nkgmKL3e4RfmW8vZ0r1bdc0B2FISHUA0CaxqLYzyy02KqUH;'
    ck = 'pin=NKTYr%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; wskey=AAJirxk3AFBiEtYkE-qACcv_vrvMdXWspkdnZPSquKXQ4sEfD3jcCWQ_CQBEexl5AthJFdgaSXAKVJ6iW-dz_bjVtwyVoI7FG_BWdVMtiII0yoBQkD7giA; '
    # ck = 'pin=KLPQa%E5%B9%B3%E6%B1%9F%E5%8E%BF%E5%AE%89%E4%BF%9D; wskey=AAJirxlJAFAxh9EyD3dvVSxseGMy3ymEFokeROlblOuZPzm-KoqENyzbzQ5BUj55Wh39FUfeEWk8Hgw4CCOvlTPAHj91k5U1T2irDIsJ68uQVbiApFeyuA; '

    for i in ck.split(';'):
        if 'pin' in i:
            user = i.split('=')[1].strip()

    # ip = get_ip()
    skuid = '11183343342'


    # ck = 'mp=jd_7b6b4d6d0b4bc;  TrackID=1vN4FH6zMhiQVuVxhYz58lTYTVkHiZyPRqTAHY3Ea-fwGWri0FYVTGv10VUCvXaX0dA5S39PcbF113un8NPeOHzXHwIvT88-Uax4bKeFSJdbHgwoD6Gzu0sFGqmFqjofRshWfS-RJ5eLjnVfPme152g;  thor=E7E196E8A12A5CE173405235B9239BDA4C5EFE63D32FC15163BC2AE71D121CC7C871D4390F7718332F9F1DC201A5FE3F548D608FE276529CC728805AAD8EAEA47B2D574F8F039D4895E039000EAA74623413FC1A8EB76DB38E54522D89BADA03CA56F04E9E594102539DAE1D551FE808B5DA6CD70591125E04F086DE519E56C5079850FFBB336446C5520082080A509945CDD9341BF0B6CCA47E55A9C4CDF95A;  pinId=SBr-25ouTZE_8n6hcfrbebV9-x-f3wj7;  pin=jd_7b6b4d6d0b4bc;  unick=jd_7b6b4d6d0b4bc;  _tp=iNluJKUSrG9Estty85fNU%2B70gQrhhPR47VpXn6whI9Y%3D;  _pst=jd_7b6b4d6d0b4bc; pin=jd_7b6b4d6d0b4bc; wskey=AAJiik9kAEBdr2TwInWTnN3Jipm_5cfQmeC9WGnkbrVkScACgyTBgrwkXbooQBbKpIR1UjE4gEwR8ltRD-Pu4c9nFQHpIDAC; pt_pin=jd_7b6b4d6d0b4bc; pt_key=AAJiik9lADCZ4B4g_7nme68g60_4QSEX-9yBJJk2cXW0aGAA8MhC4sCnKyVsKW50XApcjrIlMJ4; unionwsws={"devicefinger":"eidAbcb4812178sbg2crCUSyRlSY7J3VMNsceINnLIow+GfKPl8Q/s4aF200XmwBM9SLz0lNiTCG6Q5SjOWe2wAfRNFNh1+EObxi1jKrfb/sVkNoz1Ra","jmafinger":"lhd7wQWZNVefTprrDLTR3toDMe10RpaIFbIkscMU7CgR7PyQrRbHHeUDhiatJeqQf"}'
    # ck = 'mp=jd_2IU8CuUAdQDl;  TrackID=1VYB2zCyFVXLBGOnW0JR7JX69bcjGVyPcg-YOlYzCPdHg_2cq2x7Jlg4KrpMkTK0AjWQDiUIFSBVcnCgZyrcgm_ZoPFShQxMc4tF6tw7KEpYtEaak_wECBtXCJ0FgJirf;  thor=089AD313F58DDAC701B41EEA5A0D2CBD08B96AD6709FA5C6162FDBB2860D909780AABD2E602E7F62D32E708C0936C5956362C1E55397A0ECADDC7B93DC81887BEC91AEE64A96461ED5287794A52948E384C0C2C6F99C68C4328C9828589A6D129AE02CD214376C6B54C4AE193770702EFD4874C451559F5EAAC8C02A8525853C7EE64197C951955404B642902EACAB6E8832CB8B2C388CB3FE623CF4AAD4ADF4;  pinId=VTx2BGFqgAMdwzRWCysLUA;  pin=jd_2IU8CuUAdQDl;  unick=jd_2IU8CuUAdQDl;  _tp=RDSrkxDoANK4TUuU0cYohw%3D%3D;  _pst=jd_2IU8CuUAdQDl;'

    # ck = 'mp=jd_7b6b4d6d0b4bc;  TrackID=1vN4FH6zMhiQVuVxhYz58lTYTVkHiZyPRqTAHY3Ea-fwGWri0FYVTGv10VUCvXaX0dA5S39PcbF113un8NPeOHzXHwIvT88-Uax4bKeFSJdbHgwoD6Gzu0sFGqmFqjofRshWfS-RJ5eLjnVfPme152g;  thor=E7E196E8A12A5CE173405235B9239BDA4C5EFE63D32FC15163BC2AE71D121CC7C871D4390F7718332F9F1DC201A5FE3F548D608FE276529CC728805AAD8EAEA47B2D574F8F039D4895E039000EAA74623413FC1A8EB76DB38E54522D89BADA03CA56F04E9E594102539DAE1D551FE808B5DA6CD70591125E04F086DE519E56C5079850FFBB336446C5520082080A509945CDD9341BF0B6CCA47E55A9C4CDF95A;  pinId=SBr-25ouTZE_8n6hcfrbebV9-x-f3wj7;  pin=jd_7b6b4d6d0b4bc;  unick=jd_7b6b4d6d0b4bc;  _tp=iNluJKUSrG9Estty85fNU%2B70gQrhhPR47VpXn6whI9Y%3D;  _pst=jd_7b6b4d6d0b4bc; '

    # ck = 'mp=5Y19QlPSdXZ0nIu;  TrackID=1QL70vtTuDzaff0BPWGd0OpZVyWDNrXcgfz31IGHXKSXWRczi8t7adk1tmEFF_XfkKnj-ctkN-l7WNIV_mP0WJ9xIjDwyRu7b02SkXzRzzppHd6BKR-DyI68m2y4av_8A;  thor=BCAC54CC1B2315EF1495D93A1A6B2AF16A64EE5056763C14D6A4E2C349C648648508F87F1F1385AD10642ED278CA4FD97350BAAC03C91E4C33E58DF5E577B76B5DBB0EF8E2F873F3A0F6BB31A0AAD2E730E9B83730946DD65A610F62637F4278640E199A418F8CB958057B50265975602FD575824E5BBC5904DBF9C11C31F57AC31CBB04022D18F17C8F8B20EDD50D8012DB02A5F07A91A84C33FDF94B24A13A;  pinId=NZ3IDQW-M5PMvYCv7PWLSg;  pin=5Y19QlPSdXZ0nIu;  unick=5Y19QlPSdXZ0nIu;  _tp=yhaAyCLYMqnbTcc7MKbWXg%3D%3D;  _pst=5Y19QlPSdXZ0nIu; pin=5Y19QlPSdXZ0nIu; wskey=AAJiqueFAED66ZZIzs23Uaeetyp1HmjkuVbcdh4o-AhCiRsobhQeq3-ILeE_q1XqnLRAfFmNXms4BgNv6mPF0L7NTEqQpRPb; pt_pin=5Y19QlPSdXZ0nIu; pt_key=AAJiqueGADDmv8gPRlz6fbvijF9fC_1vKU5wGyApUV4e_DM3tdXMV8_NjpDIlF6uDw1nHlQf0t4; unionwsws={"devicefinger":"eidAb6118120e8s2y+T2+gulRo2IXV6QVO1Xdsvk+Ht3PaoVXKrIKqZHRoUIDZ1SnE1492NmwThRnGlyP4aU97un2an/rxyNNlL77HR/NFgt0J4P0s54","jmafinger":"uFBrLn2iUVIoFlm5uzlBTlra9OJOOQ7g6mPvCJ5f-9LMEbPrXpAxVQuW4w1tlSFU-"}'
    # ck = 'guid=47de2fb25294f66142674a6a29785e98daa924467b3f9e1d5349df39d4bbcf35; pt_key=app_openAAJiqtmqADAjTH2ShkBeaq1qCjaVdcv4U7ngsnVuzz71w3-Q_XuHNRV9r3PHEoaf3bxFTxiJv6o; pt_pin=jd_m3nGd7xgKCzs; pwdt_id=jd_m3nGd7xgKCzs; sid=e03a86472146848d71be27a4eabe79aw; pin=jd_m3nGd7xgKCzs; wskey=AAJiaOSmAECT_6zUtAs0lauy9irIqLgbIZfF85X6Sow1jOgLUrbPyaJUqc2F7dU-nnC3kKWZz1uWHTQz0ZSjigQeigjzkDj0;'
    # ck = 'pin=8hIdWHSGZjAqMhJ; wskey=AAJiqze6AEAmkBoPNQmpSFCWkiXor_Ki8l7qxX5Wgge6EL-pcqOJtB_pSbQId5fQq5l1BIa3OIyuU9lumWq_ftgIc-WIAOtl; pt_pin=8hIdWHSGZjAqMhJ; pt_key=app_openAAJiqze7ADD9XBZEmJxiOggXDIBNHHpKZ5244XJ6KsS41J9PRXB8ehEeeZDzu_sejbeWu9aQ_xU; unionwsws={"devicefinger":"eidA8534812031s5h7XjPL59QIqJ5X/zbSbHIoe15L4rTvI9rsQTca5V9snD54HrOxbx+DBSyN49BEApZR61cqDH14B+2Sd9qjZKOXY2LbN76aGPqGdq","jmafinger":"iXMoamkDu7A1yKpzuK6XvuNKKJCduLfLU4nx-Jc4vO7U4spnqtxUWX_pVRogF5H3h"}; guid=e7e60e425161ab404a580249fe9fa761c9df7fc9533eeb7feaa8a3a08ae09f8d; pwdt_id=8hIdWHSGZjAqMhJ; sid=9825f3c7c522122fe89b0c7ebc0881dw'
    # ck = 'pin=N04CaREvkvIouigH; wskey=AAJiqzWpAEB9c3WKkJBqTBK6JjQ-mSQ6EcTFw2ZjsCn-Kdh9HIHvXgVhxNxGQv-JcxRJeV9Cvo8-f8f_VLrBEKqdEGTF37L0; pt_pin=N04CaREvkvIouigH; pt_key=app_openAAJiqzWqADCLVBYApe16n8H2AU6zoPkuIS7DAHm-sEzzOIq3IfXq6eiipUm3Cux6pv-TmAtVRo4; unionwsws={"devicefinger":"eidA3b648123fcs8/xNQusz5ReCnbkl2TpTeDv8TUjw5wuXEr+jnl3fvlRWuSUCq+h2T7nBoUVdtT7w2ugCprW9OVKz7vMqniBEqBVxtB4YPgLqzSppD","jmafinger":"pH0ve8ig_tNIRN1tLnBsjAGS34eVWZ1mJKuMQrHW2F0gLa3WBf4AE3LZasW8xKAc3"}; guid=4d433752f944783be504718dd9375718392804f625bd03a4fa6cc8b973e42f80; pwdt_id=N04CaREvkvIouigH; sid=7fcdfcc076217da5f4e09cb51165c7fw'
    # ck = 'pin=8hIdWHSGZjAqMhJ; wskey=AAJiqz44AEDYdkVFAEEu-G6-2QFqkkEfrIypeRXjP2AdR3KEnbaaMy0ug-ACGq-78Liy_HGdkBdtB5Zn6pNpUNP7t9FWa8t4; pt_pin=8hIdWHSGZjAqMhJ; pt_key=app_openAAJiqz46ADBgzpX4v8U2q3tFI0CIV4yh8bEsayvpjTgkfRH6ZFbcue9LYdnLJLF5w47t6TUYFS0; unionwsws={"devicefinger":"eidAd96e8121eas6XzWuye4VTvC0RUyK08xv2181sEtbAF3EnytPeXK70rsSYUqIwCvsa09wWasG+LOEKJWQ2DFM6e9NXlvS4bDd+wgPwsZ2uA1yoad2","jmafinger":"oNZezb8HrGmzeuGCEpR4LdTFsm3UXWlzOkQnKoI_4ZJr2ip8yAM2SOtCQHjK5S9c6"}; DeviceSeq=dfd1825fadeb4a889e9f8a272d2b3191; TrackID=18T_2HMW2l5SqQiRbN5M0aZ2jYqCu0XKowQcpU3v78ChGoQEXLnhrQwx0MOcTU0OREiDh4dct0IFZ9oBnqd4VtjjZloVjBZBWylYnnnVfBHY; thor=04BAC086CD93D5FD47B392CB12574E16E9AD2959EDB47C64E1282479F61986D5C05B619EC73D40FB1627B0E649C27D696F50ADB69587E586BCD721A57A90B619C67A6D28A6B6AAE576145AA44C84F8357FC796C4684033D929EB1A84D3FA59D3E2012FF1E492FD81EBA72DF9636147D5D95BCD409AEBF051693CE490B0B3A251F8400B8D50CD38077C8129F2A8D9918791A7F6F25D400ED95A35A485BAB48EFD; pinId=1hI1uxT3jeOkBbbjZjDJRw; unick=8hIdWHSGZjAqMhJ; ceshi3.com=000; _tp=mFP36iYd%2BpcELZ2E02A32g%3D%3D; logining=1; _pst=8hIdWHSGZjAqMhJ; guid=1497d3eec1d6e2f4b3dfdd485b0abdbc5c9c30ef8401106ad366e67e1e6e5714; pwdt_id=8hIdWHSGZjAqMhJ; sid=38d97be301f9cf078954d79c973c1d9w'
    # ck = 'guid=ef8fe7819990bed74458c7d31d9f7a4eb2e061f8d9a41918160ca5b75dc71695; pt_key=app_openAAJiq1deADA-qv594L13L09jPZ-ODqXb2uVKys9-iB66eF2aFcPUjDfMoW7w1gZFW673MrEksKk; pt_pin=jd_yaifaHleFaeT; pwdt_id=jd_yaifaHleFaeT; sid=cb52a1da252e32175cb1afcdfcd2992w; pin=jd_yaifaHleFaeT; wskey=AAJggSsoAECpKA6gUhXFgio0Hg4fuc-Ha9ECfK3mxfve3m6vin_HehqygQJN-VJaHhHHs2j281DCd_Ij7IVGbtj7kd5DEMRO;'
    # ck = 'pin=jd_7d1c1d0d7c8c6; wskey=AAJiimL_AEApaqYXOWKhJbDvkWEDaP-kreV2Go6HF5dJX7Z1ag0WrxxFZ-kHVeSAuOnLuVyKD-yr4wmWtoj05HgFEwI8YL0e; '
    # ck = 'pin=%E7%AD%89%E9%97%AE%E7%A1%AE%E7%BA%A6; wskey=AAJiNgPCAEApoy2Db9gLgwu9oK7ffQGOEkdGT_dXAePIcJ89lzR1VCwTfMDEao6SGa2uv2aPZ_Ic3zdIVnrezzLT2_dvY6vL;'
    ck = 'pin=%E9%83%B4%E5%B7%9E%E5%B8%82%E6%83%A0%E9%A3%9E%E5%95%86%E8%B4%B8; wskey=AAJisJbhAFCfJKLDiUPNO-Uireh1UwkYWfCOzfG7iXtpiu3wZqS3Vq2eK_JTK1OBupE0YWB6uZ23lluxfxs6sTmfHIu9489dr8Wx75RiI0u2h2TXzD7j_g;'
    ip = getip_uncheck()
    # client = jd(ck, ip)
    # create_order_appstore(ck, '200', ip)

    get_real_url(ck, )
    

    # ip = None
    # jd_client = jd(ck, ip)
    # jd_client.get_appstore_detail('248300092259')
    # print(jd_client.delete_order('248300092259'))
    # url = 'https://m.jd.com'
    # url = 'https://st.jingxi.com/order/n_detail_v2.shtml?deal_id=248322658627&appCode=msc588d6d5&__navVer=1'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=e997760dabfe6ff502361ce4ea77666b9077749a65b2ce5e0057f934307e42a23fa5eea4af30c9bca6aab606e24ecc71c184d066df2d580afb5fa7da880e8e03c3f7ffc69162a5a830cdcd50f7b4f0dc'
# 
    # code, token = jd_client.gen_token(url)
    # token_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
    # print(token_url)
    # code, mck = jd_client.get_mck(token_url)
    # print(mck)
    # code, pay_id = jd_client.submit_appstore(mck, skuid, '100')
    # print('payid', pay_id)
    # code, order_id = jd_client.pay_index(pay_id)
    # print('order_id', order_id)
    # order_id = '248335926310'
    # query_order_appstore(ck, '', order_id, '100')


    # code = jd_client.cart_add(good_id)
    # code, address = jd_client.get_address()
    # code = jd_client.current_order(good_id, address)
    # code, order_id_s = jd_client.submit_order(id, address)
    # url = 'weixin://wxpay/bizpayurl?pr=W0VhsEuzz'
    # url = 'https://wqs.jd.com/order/n_detail_jdm.shtml?deal_id=244737756703&sceneval=2&appCode=ms0ca95114'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=35e63cd8e2759b7b61a352950e199a5be7fd9b33af78959511a3a9e1ba2af6c7fb9c748e5eb8642576f2bf821e57796849575b6380eeee0733a3b398749e879d7468d1105e2aae7f367203b13dcff177'
    # url = 'https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2Fb'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=85ba07a8357daaffe73450b9e5ca00bfebd5562e067c21e082b47a92e971cbeed62c171c87bc4aa79d3cee8cd6e542bc8eaccb975963e8f46aa057c4774c7ecdc1b0c4ab88b7e0928f8872365c7dde35'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=b40653a2a42cd78a492916bdb8ce459a48c563c58ceb58b85a2d1772e18858d526cef82354c2cf661474df9c82776427122f64c16e897369932856dd0260db749dad0fe81d042f848ab3f603f57cf109'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=91cdd3c81ca4eb0e567ae1aa974c0edc26ca3884223ba250dbcfa8810261853e2328b54465304f257d4cf742590d02052b86033b07b653b048611091e50a63b4c1b0c4ab88b7e0928f8872365c7dde35'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=77a008cf61301d9cbb9651771b952797f4245a8c9c698fabf6fc7b04857f5739bd950ccd2100377230016f15f941f7b10d18f8356738e997b2407dd18021474472285eb678746a57ab75c07ce71f6f46'
    # status, token = jd_client.gen_token(url)
    # pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
    # print(pay_url)
    # ck = 'guid=565a406d6271d4a4978f3c43e5efab123b307323f9a344b981164e268315b531; pt_key=app_openAAJipsscADDBi0pEYaB97guiLrL9sS4v1Un_hPTmgeJMVvb8e-JrqJqcRypjXt8BnnPukPzZfpE; pt_pin=jd_JAAsikWhNxem; pwdt_id=jd_JAAsikWhNxem; sid=24dd47f9d082bae65366f9162a08f25w; pin=jd_JAAsikWhNxem;wskey=AAJifdadAEDOi_tzRdBaoHUkiHDqm5lJpibdiz98f8DprVM33w816q7fYHgQRPVz4LGtGbMrrE2oD6shp6Blg01K13CA64Q0;'
    # create_order_appstore(ck, '100', getip_uncheck())
    # jd_client = jd(ck, ip)
    # amount = '105'
    # code, repeat_key = jd_client.xlmy_qb_load('200145365539')
    # print(repeat_key)
    # code, order_id = jd_client.xmly_qb_submit(skuid, repeat_key, amount, '780776614')
    # print(order_id)
    # code, pay_id = jd_client.xmly_gopay(order_id, amount)
    # print(pay_id)
    # code, order_id, pay_id = jd_client.yk_submit(user, phone, card_id, id)
    # order_id = ''
    # order_id = '248666777007'
    # code, pay_id = jd_client.gen_app_payid(order_id, '22', amount)
    # print(pay_id)
    # jd_client.pay_index(pay_id)
    # pay_url = jd_client.weixin_pay(pay_id)
    # print(pay_url)
    # jd_client.
    # code, pay_url = jd_client.df_pay(pay_id)
    # if code != SUCCESS:
    # print(pay_url)
    # skuid = '200147970416'
    # amount = '50'
    # code, repeat_key = jd_client.xlmy_load(skuid)
    # code, order_id = jd_client.knowledge_submit(repeat_key, skuid, amount, '42324542')
    # print(order_id)
    # code, newpay_url = jd_client.xmly_gopay(order_id, amount)
    # print(newpay_url)
    # pay_id = None
    # pay_id = '06ae74bdfeab293f356b3c3499adc08b'
    # for i in newpay_url.split('?')[1].split('&'):
        # if 'payId' in i:
            # pay_id = i.split('=')[1]
    # jd_client.pay_index(pay_id)
    # pay_url = jd_client.weixin_pay(pay_id)
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