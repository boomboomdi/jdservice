# -*- coding: utf-8 -*-
import base64
import hashlib
from random import randint
import time
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
import uuid
import requests
import json
from hashlib import md5
from tools import LOG_D, random_phone
import re
import tools
from ip_sqlite import ip_sql
from order_sqlite import order_sql

client_version = '10.4.0'
client = 'android'

SUCCESS = 1
WEB_CK_UNVALUE = 2
CK_UNVALUE = 3
CK_PAY_FAIL = 4
NETWOTK_ERROR = 5
RET_CODE_ERROR = 6
CK_NO_ADDRESS = 7

ANDROID = 'android'
IOS = 'ios'

SH_105 = '200152809708'
SH_205 = '200153024922'
SH_305 = '200153016681'
SH_505 = '200153015085'
SH_1010 = '200153023635'
SH_2020 = '200153016897'

YS_505 = '200152222503'
YS_1010 = '200152225502'
YS_2020 = '200152228602'

KLY_105 = '200153436520'
KLY_205 = '200153481321'
KLY_305 = '200153567756'
KLY_505 = '200153481018'
KLY_1010 = '200153472622'
KLY_2020 = '200153453401'

KLY = {
    '105': '200153436520',
    '205': '200153481321',
    '305': '200153567756',
    '505': '200153481018',
    '1010': '200153472622',
    '2020': '200153453401',
}

SKU_INFO = {
   SH_105:{
       'face_price': '10000',
       'online_price': '10500'
   }, 
   SH_205:{
       'face_price': '20000',
       'online_price': '20500'
   },
   SH_305:{
       'face_price': '30000',
       'online_price': '30500'
   },
   SH_505:{
       'face_price': '50000',
       'online_price': '50500'
   },
   SH_1010:{
       'face_price': '100000',
       'online_price': '101000'
   },
   SH_2020:{
       'face_price': '200000',
       'online_price': '202000'
   },
   YS_505:{
       'face_price': '50000',
       'online_price': '50500'
   },
   YS_1010:{
       'face_price': '100000',
       'online_price': '101000'
   },
   YS_2020:{
       'face_price': '200000',
       'online_price': '202000'
   },
   KLY_105:{
       'face_price': '10000',
       'online_price': '10500'
   },
   KLY_205:{
       'face_price': '20000',
       'online_price': '20500'
   },
   KLY_305:{
       'face_price': '30000',
       'online_price': '30500'
   },
   KLY_505:{
       'face_price': '50000',
       'online_price': '50500'
   },
   KLY_1010:{
       'face_price': '100000',
       'online_price': '101000'
   },
   KLY_2020:{
       'face_price': '200000',
       'online_price': '202000'
   },
}

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
            if '请添加白名单' in response.text:
                return None
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
        self.proxy = {
            'http': proxy_ip,
            'https':proxy_ip 
        }


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
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            # print(resp.text)
        except:
            return NETWOTK_ERROR
        if 'payId' in resp.text:
            return SUCCESS
        return CK_UNVALUE

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
    
    def sdk_pay(self, pay_id):
        print('sdk_pay')
        sv = '120'
        function_id = 'weixinPay'
        ts = str(int(time.time() * 1000))
        body= '{"appId":"jd_android_app4","payId":"' + pay_id + '","sdkToken":""}'
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
        except:
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            print(resp.text)
            ret_json = json.loads(resp.text)
            if 'errorCode' not in resp.text:
                return SUCCESS, ret_json['payInfo']
            else:
                print(resp.text)
                return RET_CODE_ERROR, None
        return RET_CODE_ERROR, None

    def yk_submit(self, user_id, phone, card_id, sku_id, amount):
        print(user_id + '   ========= yk_submit =========')
        online_price = SKU_INFO[sku_id]['online_price']
        face_price = SKU_INFO[sku_id]['face_price']
        ts = str(int(time.time() * 1000))
        url = 'https://api.m.jd.com/client.action?functionId=oilcardSubmitOrder&body=%7B%22userPin%22%3A%22' + user_id + \
            '%22%2C%22source%22%3A8%2C%22callId%22%3A%223c' + str(uuid.uuid4())[2:] + '%22%2C%22voiceCode%22%3Anull%2C%22promotionDiscount%22%3A0' + \
            '%2C%22dongCouponPay%22%3A0%2C%22balancePay%22%3A0%2C%22phone%22%3A%22' + phone + '%22%2C%22salePrice%22%3A' + online_price + '%2C%22promoRfId%22%3Anull' + \
            '%2C%22onlinePay%22%3A' + online_price + '%2C%22jingdouPay%22%3A0%2C%22skuId%22%3A%22' + sku_id + '%22%2C%22payType%22%3A1%2C%22couponIds%22%3A%5B%5D%2C%22' + \
            'cardNum%22%3A%22' + card_id + '%22%2C%22brand%22%3A%222%22%2C%22jingCouponPay%22%3A0%2C%22facePrice%22%3A' + face_price + '%7D&appid=youka_H5&client=youka_H5' + \
            '&clientVersion=1.0.0&jsonp=jsonp_' + ts + '_98652'
        print(url)
        headers = {
            'charset': "UTF-8",
            # 'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'user-agent': "okhttp/3.12.1;jdmall;android;version/10.3.5;build/92610;",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'referer': 'https://oilcard.m.jd.com/',
            'cookie': self.ck
        }
        try:
            resp = requests.post(url=url, headers=headers, proxies=self.proxy)
        except Exception as e:
            print('===== submit error ======')
            LOG_D(e)
            return NETWOTK_ERROR, None, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = resp.text.split('(')[1]
            ret_json = ret_json.split(')')[0]
            ret_json = json.loads(ret_json)
            if ret_json['msg'] == 'SUCCESS':
                return SUCCESS, ret_json['data']['orderId'], ret_json['data']['payId']
            # elif ret_json['msg'] == '不能下单' or '您的账户下单过于频繁' in ret_json['msg'] or 'no permissions' in ret_json['msg']:
            else:
                return CK_UNVALUE, None, None
        return RET_CODE_ERROR, None, None


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
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy, timeout=3)
        except:
            return NETWOTK_ERROR, None
        # print(resp.text)
        if resp.status_code == 200:
            ret_json = json.loads(resp.text)
            if ret_json['code'] == '0':
                return SUCCESS, ret_json['payId']
            else:
                return CK_UNVALUE, None
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
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy, timeout=3)
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
        head = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
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

    def order_detail(self, order_id):
        # url = 'https://oilcard.m.jd.com/order/orderDetail?orderId=' + order_id
        url = 'https://oilcard.m.jd.com/order/orderDetail?orderId=' + order_id
        print(url)
        headers = {
            # 'user-agent': "okhttp/3.12.1;jdmall;iphone;version/10.3.5;build/92610;",
            'user-agent': "jdapp;iphone;10.4.0;",
            # 'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            # 'referer': 'https://oilcard.m.jd.com/order/orderList',
            'cookie': self.ck
        }
        try:
            resp = requests.get(url=url, headers=headers, proxies=self.proxy)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if resp.status_code == 200:
            # print(resp.text)
            for line in resp.text.split('\n'):
                if 'fr red f-s-26' in line:
                    print(line)
                    if '充值成功' in line or '完成' in line or '正在充值' in line:
                        return SUCCESS, True
        return SUCCESS, False


    def update_ck(self):
        code, token = self.gen_token('https://oilcard.m.jd.com')
        if code != SUCCESS:
            return code
        token_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
        code, mck = self.get_mck(token_url)
        if code != SUCCESS:
            return code
        self.ck += mck
        return code

    def wait_pay(self, amount):
        sv = '120'
        function_id = 'wait4Payment'
        ts = str(int(time.time() * 1000))
        body= '{"deis":"dy","phcre":"v","newMyOrder":"1","newUiSwitch":"1","page":"1","pagesize":"10","plugin_version":104000}'
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
        # print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
        except Exception as e:
            print(e)
            return NETWOTK_ERROR, None
        if 'orderId' in resp.text:
            for order in resp.json()['orderList']:
                if amount in order['detailPrice']:
                    last_time = order_sql().search_order(order['orderId'])
                    now_time = str(int(time.time()))
                    if last_time != None:
                        if int(now_time) - int(last_time) > 600:
                            return SUCCESS, order['orderId']
        return SUCCESS, None

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


def upload_callback_result(result):
    url = 'http://127.0.0.1:9191/api/ordernotify/notifyorderstatus0069'
    head = {
        'content-type': 'application/json'
    }
    tools.LOG_D(result)
    try:
        res = requests.post(url, headers=head, data=result).json()
    except Exception as e:
        tools.LOG_D(e)
        return
    tools.LOG_D(str(result) + '\nret:' + json.dumps(res))
    if res['code'] == 0:
        return True
    else:
        return False

def upload_order_result(order_me, order_no, img_url, amount, ck_status):
    url = 'http://127.0.0.1:9191/api/preparenotify/notifyjdurl0069'
    head = {
        'content-type': 'application/json'
    }
    data = '{"prepare_status": "1", "ck_status": "1", "order_me": "' + order_me + '", "order_pay": "247775877802", "amount": "' + amount + '", "qr_url": "https://pcashier.jd.com/image/virtualH5Pay?sign=d6e2869be73c243c560393c09a7182ca89a1ed515bb088cc3ca08658daa14a0a6d4f8399eb23e3c53f93c113731f840e7fbd03300ab7e2ace58ab06ead2a3128ca6ce6e5705410517c18220000f4be1334af41273e8fe32548929db9a7001d32"}'
    data = {
        'prepare_status': '1',
        'ck_status': ck_status,
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'qr_url': img_url
    }
    if img_url == None:
        data['prepare_status'] = '0'
    data = json.dumps(data)
    tools.LOG_D(data)
    try:
        res = requests.post(url, headers=head, data=data)
    except Exception as e:
        LOG_D(e)
        return
    print(res.text)


def create_df_pay(account, ck, sku_id, card_id, amount):
    phone = random_phone()
    # ip = get_ip()
    ip = getip_uncheck()
    print('use ip:', ip)
    jd_client = jd(ck, ip)
    code, order_id, pay_id = jd_client.yk_submit(account, phone, card_id, sku_id, amount)
    if code != SUCCESS:
        return code, None, None
    jd_client.pay_index(pay_id)
    code, pay_url = jd_client.df_pay(pay_id)
    if code != SUCCESS:
        return code, None, None
    return code, pay_url, order_id


def create_sdk_pay(account, ck, sku_id, card_id, amount):
    phone = random_phone()
    ip = getip_uncheck()
    if ip == None:
        return None
    print('use ip:', ip)
    jd_client = jd(ck, ip)
    code, order_id, pay_id = jd_client.yk_submit(account, phone, card_id, sku_id, amount)
    if code != SUCCESS:
        return code, None, None
    jd_client.pay_index(pay_id)
    code, pay_info = jd_client.sdk_pay(pay_id)
    if code != SUCCESS:
        return code, None, None
    pay_url = 'weixin://app/wxe75a2e68877315fb/pay/?nonceStr=' + pay_info['nonceStr'] + \
        '&package=Sign%3DWXPay&partnerId=' + pay_info['partnerId'] + '&prepayId=' + pay_info['prepayId'] + \
        '&sign=' + pay_info['sign'] + '&timeStamp=' + pay_info['timeStamp'] + '&signType=SHA1'
    return SUCCESS, pay_url, order_id

def get_unpay(ck, proxy):
    jd_client = jd(ck, proxy)
    jd.wait_pay()

def create_ios_order(ck, sku_id, card_id, phone, amount, proxy):
    for i in ck.split(';'):
        if 'pin=' in i:
            user = i.split('=')[1].strip()
    jd_client = jd(ck, proxy)
    code = jd_client.update_ck()
    if code != SUCCESS:
        return code, None, None

    code, order_no = jd_client.wait_pay(amount)
    if code != SUCCESS:
        return code, None, None
    # unpay
    if order_no != None:
        code, pay_id = jd_client.gen_app_payid(order_no, '99', amount)
        if code != SUCCESS:
            return code, None, None
    # create new
    else:
        code, order_no, pay_id = jd_client.yk_submit(user, phone, card_id, sku_id, amount)
        if code != SUCCESS:
            return code, None, None
    code = jd_client.pay_index(pay_id)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, pay_id

def order_ios(ck, order_me, amount, card_id, phone):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_no, pay_id = create_ios_order(ck, KLY[amount], card_id, phone, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            order_sql().insert_order(order_no, amount)
            order_sql().update_order_time(order_no)
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    tools.LOG_D(pay_id)
    upload_order_result(order_me, order_no, pay_id, amount, ck_status)

def check_ck(ck, order_me, amount, card_id, phone):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_no, pay_id = create_ios_order(ck, KLY[amount], card_id, phone, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            return False
        elif code == SUCCESS:
            return True
        elif code == RET_CODE_ERROR:
            return False
        i += 1
    tools.LOG_D(pay_id)
    return False




def query_order_status(ck, order_id, proxy_ip):
    jd_client = jd(ck, proxy_ip)
    code = jd_client.update_ck()
    if code != SUCCESS:
        return code, None
    code, status = jd_client.order_detail(order_id)
    if code != SUCCESS:
        return code, None
    return SUCCESS, status


def query_order(ck, order_me, order_no, amount):
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
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        proxy = tools.getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        code, status = query_order_status(ck, order_no, proxy)
        if code == SUCCESS:
            if status == True:
                result['pay_status'] = '1'
                result['card_name'] = 'QB' + str(time.time()).replace('.', '')
                result['card_password'] = 'QB' + str(time.time()).replace('.', '')
                result = json.dumps(result)
                if upload_callback_result(result):
                    order_sql.delete_order(order_no)
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1



def query_order_im(ck, order_me, order_no, amount):
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
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        proxy = tools.getip_uncheck()
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        code, status = query_order_status(ck, order_no, proxy)
        if code == SUCCESS:
            if status == True:
                result['pay_status'] = '1'
                result['card_name'] = 'QB' + str(time.time()).replace('.', '')
                result['card_password'] = 'QB' + str(time.time()).replace('.', '')
                result = json.dumps(result)
                return result
            else:
                result = json.dumps(result)
                return result
        elif code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            return result
        i += 1




def get_real_url(ck, pay_id, proxy):
    jd_client = jd(ck, proxy)
    code, pay_info = jd_client.sdk_pay(pay_id)
    if code != SUCCESS:
        return code, None
    pay_url = 'weixin://app/wxe75a2e68877315fb/pay/?nonceStr=' + pay_info['nonceStr'] + \
        '&package=Sign%3DWXPay&partnerId=' + pay_info['partnerId'] + '&prepayId=' + pay_info['prepayId'] + \
        '&sign=' + pay_info['sign'] + '&timeStamp=' + pay_info['timeStamp'] + '&signType=SHA1'
    return SUCCESS, pay_url



def real_url(ck, pay_id):
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    account = tools.get_jd_account(ck)
    proxy = None
    if proxy == None:
        proxy = tools.getip_uncheck()
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        code, pay_url = get_real_url(ck, pay_id, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['msg'] = 'ck unvalue'
            break
        elif code == SUCCESS:
        # pay_url = 'weixin://app/wxe75a2e68877315fb/pay/?nonceStr=7c250678f61f49092fa0d4040e5e54e9&package=Sign%253DWXPay&partnerId=1238342201&prepayId=wx1321152505977680ae181c2f694ddd0000&timeStamp=1655126125&sign=872D48225CD35C74783548967B23710D&signType=MD5'
            result['code'] = '0'
            result['data'] = pay_url
            result['msg'] = 'success'
            return json.dumps(result)
        i += 1
    return json.dumps(result)



        

if __name__ == '__main__':
    good_id = '10045398811484'
    amount = '103'
    good_id_206 = '10045398948206'
    good_id_309 = '10045399054885'


    phone = '135' + str(randint(10000000, 99999999))
    amount = '1010'
    card_id = '100011320003' + str(randint(1000000, 9999999))
    sku_id = '200153481018'

    # code, order_id, pay_id = jd_client.yk_submit(user, phone, card_id, id)
    # jd_client.pay_index(pay_id)
    # code, pay_url = jd_client.df_pay(pay_id)
    # print(pay_url)

    # code, pay_url, order_id = create_ykdf(user, ck, id, card_id, amount)
    # code, pay_url, order_id = create_sdk_pay(user, ck, SH_505, card_id, '505')
    # code, pay_url, order_id = create_order(user, ck, id, card_id, amount, IOS)
    # print(code, pay_url, order_id)
    # ip = get_ip()
    # jd_client = jd(ck, ip)
    # ck = 'pin=jd_7b3b6c0bfbbbf; wskey=AAJiik8NAEDle7sy1ILxFTBQezCHqbTaSnxCubDeI6R2JkKxzs3UxmCRKF3drtQLB5bwya1CWmqypqGYEwVD_03mK303Klxz; pt_pin=jd_7b3b6c0bfbbbf; '
    # ck = 'guid=565a406d6271d4a4978f3c43e5efab123b307323f9a344b981164e268315b531; pt_key=app_openAAJipsscADDBi0pEYaB97guiLrL9sS4v1Un_hPTmgeJMVvb8e-JrqJqcRypjXt8BnnPukPzZfpE; pt_pin=jd_JAAsikWhNxem; pwdt_id=jd_JAAsikWhNxem; sid=24dd47f9d082bae65366f9162a08f25w; pin=jd_JAAsikWhNxem;wskey=AAJifdadAEDOi_tzRdBaoHUkiHDqm5lJpibdiz98f8DprVM33w816q7fYHgQRPVz4LGtGbMrrE2oD6shp6Blg01K13CA64Q0;'
    # ck = 'pt_pin=jd_JAAsikWhNxem; pwdt_id=jd_JAAsikWhNxem; sid=24dd47f9d082bae65366f9162a08f25w; pin=jd_JAAsikWhNxem;wskey=AAJifdadAEDOi_tzRdBaoHUkiHDqm5lJpibdiz98f8DprVM33w816q7fYHgQRPVz4LGtGbMrrE2oD6shp6Blg01K13CA64Q0;'
    # ck = 'pin=jd_CVUppfBIfbul; wskey=AAJiofzwAECscBxdv0Lj5qz3jreRLN_IAvgH7Uq70RWkOwBatTNQVkFnwWo51l7JBaT4YFA-lcnNG3e7bP9V-C5Hq5K0qqOz; guid=c3c44943dd764c55cae73b7fa2837c2f8d7af4dede429f16c1fa85e08996d02c; pt_key=app_openAAJiofzxADC9wqrMYQchf9syROsYZ9fBiVq_ojPiPQQlZZAXbFyGSH6sm6zvY69rXzG8WTP7vG4; pt_pin=jd_CVUppfBIfbul; pwdt_id=jd_CVUppfBIfbul; sid=3add1ca1f79d10e2a65a2f80e75d8cdw'
    # ck = 'pin=jd_kOpnrNnTYpKZ; wskey=AAJiogLUAEDOkeSL-5TrLxv8lh7IIhBSsvBP-z_GokebSrSvCqeqvCoJ9WfZhOnJkvNybXADQ22nesXXOLoi1m0_96dcbRV0; TARGET_UNIT=bjcenter; guid=4bf828b6c116dc2980893c40e64e51b1ed616531510f151f8a24c6922b0067a3; '
    # ck = 'pin=jd_4d9b500034155; wskey=AAJiqgJZAECd9g_DDWxJo3YPVOaYWwvDsU_BCxK7nZcTma51_nkgmKL3e4RfmW8vZ0r1bdc0B2FISHUA0CaxqLYzyy02KqUH;'
    # ck = 'guid=45d763d66f8a1e21cea7f9b1aedbbebe58dd7e3bc040f15ca83e875fccfcb16e; pt_key=app_openAAJiqYuSAEDRuA__A6tK47tOg5LStzonkj33X_7R0aDB6xBCYZw2nrSYjTfSWa75VUuSfpRSOsrJk8eS4vZ7E7gcKhrBLWOH; pt_pin=jd_ZW8vrsHz0s57jZk; pwdt_id=jd_ZW8vrsHz0s57jZk; sid=392bc5983122f98dafdda9622dae98dw; pin=jd_ZW8vrsHz0s57jZk;wskey=AAJiHCtRAFDzK3DBRZbGte0raavmaLNSMUnyuzfjbO9j1Knl7wYzGSvz8Q3uNSVnjt6AOjP0pNmWxmFW-4U8xUscpW26vPmJlhHASTJjznsGquo5Y1Lg8w==;'
    # ck = 'guid=c638ee7574571d55b9b272f9b578f98c40e68ec22c31f4ebbda832602e7717b3; pt_key=app_openAAJiqYuTAEDcSDrKEK1FstIFRpTJcMyrRc4sDbNcc8NgVlyJBp6KPkqifzjQ_WlcJmRQm12SpBbby_BEA8EXXxMNobxBxe_3; pt_pin=jd_DoUiY6tydHRrJxb; pwdt_id=jd_DoUiY6tydHRrJxb; sid=79aaefb3989577337b1ee1a899ca331w; pin=jd_DoUiY6tydHRrJxb;wskey=AAJiDI4YAFBNgPdxb1j_UEKipLFNPexZ0iQ-voK5aRMf4G5ZK5pSeCnH6LRkspKuUL0-X1B9TNEUSswMbDPK7Mu1A7df8KZKdX9afSjnRe6-lj2Xvh4WAg==;'
    # ck = 'guid=f9789125b29c90bffcf2835a1fcddfaeb275be368a4b5fe4a7bce46e2002092d; pt_key=app_openAAJirDmIADBNi_iF9sBoyVaZaAapr7J8VVWBHhdnDgVOeOcbBH2H6Kgos4TAAKLa_lISk4b0wgg; pt_pin=wdufNQNtnIfvpX; pwdt_id=wdufNQNtnIfvpX; sid=68649bddc754e1590c8dc7cbb8a26dew; pin=wdufNQNtnIfvpX; wskey=AAJiqupYAEDygbozK_biokrVTDuutv5SPDYbbFfy9tEfRvGnuF2ostRkdAYDi6ni9RvqxqullGqZyKZxuMYV5Z-dde8ZEEWE'
    # ck = 'guid=9a6c2d13412fa1340724134bbfa6cc454a1276a90d21ce2f6bd196e122f89086; pt_key=app_openAAJirDmIADCLDVI6V6N-Um5RmzU3AHNFQSOqiTP_8nMMRZvOWjGbxCFeYpxanAH3tq3ff_1Jkrc; pt_pin=wdsrfkrUhheDmU; pwdt_id=wdsrfkrUhheDmU; sid=931376a3d922d1e9d6f00a8b9ee7ca5w; pin=wdsrfkrUhheDmU; wskey=AAJiquv4AEDNNT5Iwf17Wv7WZV3Ot0evqclQ82PsU8cr1q9JqhlRn0OFU8Ly7yRn-fD8L6fjyA41BVz45kl0Y9kNA6669TBW;'
    # ck = 'guid=f9789125b29c90bffcf2835a1fcddfaeb275be368a4b5fe4a7bce46e2002092d; pt_key=app_openAAJirDmIADBNi_iF9sBoyVaZaAapr7J8VVWBHhdnDgVOeOcbBH2H6Kgos4TAAKLa_lISk4b0wgg; pt_pin=wdufNQNtnIfvpX; pwdt_id=wdufNQNtnIfvpX; sid=68649bddc754e1590c8dc7cbb8a26dew; pin=wdufNQNtnIfvpX; wskey=AAJiqupYAEDygbozK_biokrVTDuutv5SPDYbbFfy9tEfRvGnuF2ostRkdAYDi6ni9RvqxqullGqZyKZxuMYV5Z-dde8ZEEWE'
    # ck = 'guid=9a6c2d13412fa1340724134bbfa6cc454a1276a90d21ce2f6bd196e122f89086; pt_key=app_openAAJirDmIADCLDVI6V6N-Um5RmzU3AHNFQSOqiTP_8nMMRZvOWjGbxCFeYpxanAH3tq3ff_1Jkrc; pt_pin=wdsrfkrUhheDmU; pwdt_id=wdsrfkrUhheDmU; sid=931376a3d922d1e9d6f00a8b9ee7ca5w; pin=wdsrfkrUhheDmU; wskey=AAJiquv4AEDNNT5Iwf17Wv7WZV3Ot0evqclQ82PsU8cr1q9JqhlRn0OFU8Ly7yRn-fD8L6fjyA41BVz45kl0Y9kNA6669TBW;'
    # ck = 'guid=1b9f8c0966da45e5dec16b11d9b655a9846872e81ff861b174e2bd597be7e810; pt_key=app_openAAJirD_iADA8ovLLhGRUVcJAWZsHYcsRna5Cls-tETyj1LUgXyAuBuhhux9G52J4lB-hPKqJx74; pt_pin=HZHJY1251W; pwdt_id=HZHJY1251W; sid=6a2ad441bcd40e40ea87f117a43a227w; pin=HZHJY1251W; wskey=AAJikx0iAECDdpoEimGNZfFvBRNmCBdOrtXbMYaYYyLT3UMXulW3DDfulYkgoZN3AkVbzLFed-P9vgXL6vdXa3FHr40kodrm;'
    # ck = 'guid=7263d0ee9eef68231daf879547e25928bb6df81f6599076877d62e40fc159b61; guid=7263d0ee9eef68231daf879547e25928bb6df81f6599076877d62e40fc159b61; pt_key=app_openAAJirEOLADBN3whClzEUSwjY5unE4oFNAwXlj0Jn__zAHJC0B4fl48WIDIkt1HpU75ZzKsb-wj0; pt_pin=jd_LlUNXputbCwI; pwdt_id=jd_LlUNXputbCwI; sid=e79e17a9352bebdb2ce5e374c7aaf6ew; thor1=; wq_skey=; pin=jd_LlUNXputbCwI;wskey=AAJifHIYAEBHvX6dW-19h6iC0mI3QmuN4gz5XwtGaFDzfKFKZ_gVLeed_2IpXfzftt7eVR8IBzRt496xmz1QtRuFLuWbCEAq;'
    # ck = 'pt_pin=jd_YsAGvcvRuZAf;pt_key=app_openAAJiqye4ADAzJj3vFmtckk5wwWWKG2WIrMNDbAgqQorU5VgX8949DJloJK03Hf8Os7UlfwVnQPE; pin=jd_YsAGvcvRuZAf;wskey=AAJhzTiyAEAJJ7wQ_XPkj10HdD02RuW0xE4IufvRgGMYiP1JQoN-U7IMBKAxlCAvDkmwd-YXfX6o1vsXv2GwtOyWdexrojRD;'
    # ck = 'pt_pin=jd_iHWqyKfaXrIi;pt_key=app_openAAJiqye4ADD4G_WvJqvkGAIz-ttg3DVnN83NjXTL8H4_l10ftqs_Jg1_RhZCWHEvfatKVsLEDAw; pin=jd_iHWqyKfaXrIi;wskey=AAJhzUL8AECBrD6NVm02resg17FYPx6F6FLLhKws-YKwwJEw-khhIDYpwO0OcoN36wecvXxvrSLNEhRyt4k2bOWuneYlUSg_;'
    # ck = 'pin=jd_iHWqyKfaXrIi;wskey=AAJhzUL8AECBrD6NVm02resg17FYPx6F6FLLhKws-YKwwJEw-khhIDYpwO0OcoN36wecvXxvrSLNEhRyt4k2bOWuneYlUSg_;'
    # ck = 'pt_pin=jd_YXQEOLfwxRrG;pt_key=app_openAAJiqye4ADD3UDjSyVD3bFoAtqHK6u-8j16R9_7AhgqhCUTG2KeLoEqlEMqIUUBwDxlY61I1G5s; pin=jd_YXQEOLfwxRrG;wskey=AAJhzTvYAEB6jviIAFpw1M5WP2uc7JGYDsMcsaY02X-_5ITay_CAFogUrHPrJWRhF_PG9YkoQDMVbnT97fGNIScbVn3z678o;'
    # ck = 'pt_pin=jd_YXQEOLfwxRrG;pt_key=app_openAAJiqye4ADD3UDjSyVD3bFoAtqHK6u-8j16R9_7AhgqhCUTG2KeLoEqlEMqIUUBwDxlY61I1G5s; pin=jd_YXQEOLfwxRrG;wskey=AAJhzTvYAEB6jviIAFpw1M5WP2uc7JGYDsMcsaY02X-_5ITay_CAFogUrHPrJWRhF_PG9YkoQDMVbnT97fGNIScbVn3z678o;'
    # ck = 'pt_pin=jd_rdZhciuEBFCm;pt_key=app_openAAJiqye4ADD108w1WY4qlfl7tOCQlfvE3EcfXLDNaP8q0gUwQxxrPeJGbZjK37q0dAv4JeawK08; pin=jd_rdZhciuEBFCm;wskey=AAJhzUHDAEBm1wi9nCGChnD_IsdBl_EBLluHKOrB4uI3OidtXNNxZ202jIFm7RMYYW0D_AUBJMd7oWP-Ce55XzIH3n-_D3eN; '
    ck = 'pin=jd_FECiipTFOVRW;wskey=AAJhzXljAEDbmGUv-czFhjgBvjGHOXOhkvp7F90QCMmqx3Iq6tDKFJDQVoiIXYN1ZRZuJg4bUFDVCQU-CgE1BQlFZxZCiV6o; '
    ck = 'pt_pin=jd_FECiipTFOVRW;pt_key=app_openAAJiqye7ADABQYX1cugaKnAeSdA3W5kTiaCRJFKu_Wem22vwnxNBCq3SxDP_a1QsX3aA8ND5y5M; pin=jd_FECiipTFOVRW;wskey=AAJhzXljAEDbmGUv-czFhjgBvjGHOXOhkvp7F90QCMmqx3Iq6tDKFJDQVoiIXYN1ZRZuJg4bUFDVCQU-CgE1BQlFZxZCiV6o; '
    ck = 'pin=jd_rpdTfsPqucvg;wskey=AAJhzVWFAEDWQLvWw4Oo5W6HST489VpwlAWC8ujAlL7cxhwk50mJk45gAF-1yB--tTbJn_CVYIkgbbPhfvvCgIs-B0dC0U0p; '
    ck = 'pin=jd_mzroKfnSaOxy;wskey=AAJhzYLBAED9zjk0gz3ePjao5K37Lw6BYl0SIlVnY2E68o-KJ4_0sSjy_hfCpHjxl7MOX2_WQPRZ4TATujvQBRTouyTeCeCW; '
    ck = 'pin=jd_cISIbAfWRw7zt85;wskey=AAJiY8QYAFD9mEGCLDkqdvpv-6NkkzYwwhwqghay7mqKDHbuApCcdCfYcgObbS9xxPQdBtWdzCl0OSsbkSZXAmjVuv53mxL3YexWvl8McQ4C1eQD_dc1FA=='
    ck = 'pin=jd_PDIfGWaSDKyz;wskey=AAJhx-tQAEBPRt7rvzK3lWIMp1DOnxLXTGT7anfU29rr435cQ5uFgCnGv-xjHKieRbmsNOWI_HvOJViiu4lk6PFRoo0jUw6h;'
    ck = 'pin=jd_NBntffacpJxn;wskey=AAJhx9o5AED-XbJwodwvxZTy_ZZx0njZ6aHP4mcvY7f49EkgZ-bzs-rhIw-6xZAHzTy_VkwI6HCmJ-ypJupZ4XGCJFb8W3qn;'
    ck = 'pin=jd_pMKBhifWUvZc;wskey=AAJhx_I8AEDA-FeelvcD2bZ9MScI12X75PPnW6vcxQ3E8cBCXWTENSUX9QMJZqiBY-g-kN8wWfVwcVcMnVQ1jqqjp4KpfPzY;'
    ck = 'pin=jd_WHJPNPycfslV;wskey=AAJhx_vlAECwBeAOgKIBgQyqFzHa7zgfiC4p4zA2QRlxn3H8T6jRN4BEancR8sv-yaShzEL3UVQUeONejSyCBC8vs6oOHkFC;'
    ck = 'pin=jd_CsKjbZvArPnS;wskey=AAJhx-eUAEDpilqpO9SPAMLS1eMILyFYM9ia_wBvT8p-q4t2yexF8N_8l0es6g6T6ErTZLPoiC375tk2IejSzkH3luzPnlye;'
    ck = 'pin=jd_JJUQJyhuXQvV;wskey=AAJh3m9jAEBPOaUw6REmhmJrTBxSH6vgWg8CQ0WsT-y6haj_EhpGSUVkXskSFoIbJLObQF25GK0oikL3-uI8f9x3b3hlEIyk;'
    # ck = 'pin=jd_wfNdFSUhdltk;wskey=AAJh3l6hAEAODa-doZSckGIVNKGD0SOxejrlEeslfms_wnC9TOwwywgBe4kD1NQzhtm0XBAVWs83Z-VuCZzUYu1qdFQ9LApV; '
    # ck = 'pin=jd_EDyFZMGcbHRb;wskey=AAJh3l0UAEAFvaH8HQqSSDv5b-iWmV_l7Cv0fXcVB9vyga3-evLgrKbepfwx-G0rkcFIAhMj4zWEtVhCOYlBXi88_g5renRj;'
    ck = 'pin=jd_yGyNCNVqgDiW; wskey=AAJh3lBPAEDD22Sc7xaZ-ksuhz9HU2lBu4lbgxBpzCqdleLnK4e8SP15hEXk2xhXTALb7qN8AK4LvKa3UvNMghhkL27O8evz;'
    ck = 'pin=jd_fSLLMmbmzzfJ; wskey=AAJh3lGDAEBTfj4bRDiikbrehybIOS7y-OZ99zTpb3ZFaB8TJHeQVfeVUexL2uj2U0Sh7RhXcEeTcswnS1Jn8DUT3ORJv7Xt; '
    ck = 'pin=jd_kPBVOWEypCCr;wskey=AAJhxnZNAEDfW1Aq_-IJgLA5V-Y_splmupBCNbZ5gVR-ICaZayT9oyIyfzB3-YrjyfWU9gbcMBJ-jvD575Su_Ln8UGSAPa6V;'
    ck = 'pin=jd_vAdOaEdzVFdp; wskey=AAJghPQQAECZ95_rmo_6RpOu-lVJEB8wWeFrxTBFmo2bOWYqXt0N3EbKijwkRZHAdTaLwe9vDnKW5bGvzhjjmw5YpbUbqUgD; '
    ck = 'pin=jd_AdxjztAlWBiK; wskey=AAJggPxwAED45Vc7FG7sA1oX-h-x3vbeasgt8OREDXfCu8_Hy276YU-w4whW-iOHUgFipHDXbt7OEEDERzDuVqxdK3vnlIWz; '
    ck = 'pin=jd_uhxsgNHizwij; wskey=AAJgruWxAEBJkkFuuyWTIHLIDK4w08oDJXuURqSQh0ohqQMuVuF9ngWMCUaIVo_OKwNrt-12W8AnwOL4PoTS_ukQRzb30uUG; '
    ck = 'guid=66935036fe54f7ffa8696fa4ca99b8fb9ae361e147ea15a7fc1b1dc1b68b9660; pt_key=app_openAAJirdXIADDlPAGY1ruV9qOWcTv5-NFrxiVDYP2Zk89dvC9N8fMAY09e_nFQ0cP6WowlQ24p3bc; pt_pin=jd_uhxsgNHizwij; pwdt_id=jd_uhxsgNHizwij; sid=09c85b3453ce1986e6006c53e2b025dw; pin=jd_uhxsgNHizwij; wskey=AAJgruWxAEBJkkFuuyWTIHLIDK4w08oDJXuURqSQh0ohqQMuVuF9ngWMCUaIVo_OKwNrt-12W8AnwOL4PoTS_ukQRzb30uUG'
    ck = 'pin=jd_KHhDrLYdVpae;wskey=AAJhxngvAEDtn1Cc1-UHSI07s3YcIcmDqrntC49bCEnENHKioocxad0dyJPYUDqzB6De_IRu9VpUPASrIW1VbaJ-Fep1lS2i;'
    ck = 'guid=66935036fe54f7ffa8696fa4ca99b8fb9ae361e147ea15a7fc1b1dc1b68b9660; pt_key=app_openAAJirdXIADDlPAGY1ruV9qOWcTv5-NFrxiVDYP2Zk89dvC9N8fMAY09e_nFQ0cP6WowlQ24p3bc; pt_pin=jd_uhxsgNHizwij; pwdt_id=jd_uhxsgNHizwij; sid=09c85b3453ce1986e6006c53e2b025dw; pin=jd_uhxsgNHizwij; wskey=AAJgruWxAEBJkkFuuyWTIHLIDK4w08oDJXuURqSQh0ohqQMuVuF9ngWMCUaIVo_OKwNrt-12W8AnwOL4PoTS_ukQRzb30uUG;'
    ck = 'pin=jd_qRbyYLMFypuh;wskey=AAJhxqPrAEA21VR1OrpjsE9BxEL5d6-LngjXHN6f6cFVr4LY98t_jaXIluw4ni0Zbvc1ECj51CEGXb792ReU6b37vFgyW1_J;'
    ck = 'pin=jd_pWXGDEMeiZLg;wskey=AAJhxnmrAED8UbqJx-aoP9oNEDuN7M6flU21ujd0TqR1FKV_EgqUMdUPR7_k0egI3-xN5HutEbuz553ZzP7ssDn-ocjD5gsS;'
    # ck = 'guid=4147664d2d6900ff55c7a82810cf07172ed04c2c6d6a64f91dfdbf6d0aa44c34; pt_key=app_openAAJirdXkADCR9VzgCJ0OJj8-gUsr5CNAir64bG6NprH7MY50Jf0g-WpORUiy0borupQhh0W5sXo; pt_pin=jd_RTHfJGApbDPj; pwdt_id=jd_RTHfJGApbDPj; sid=9ae11f4b9ddcaf03b08805da425a804w; thor1=; wq_skey=; pin=jd_RTHfJGApbDPj;wskey=AAJhxmK3AEAhdaT8TWoIKtg1hCOVPMgJMRLRCOEcwYxORKFlbw4pLTTT_W4s-A8BCH3EDeOak5qqw62x6RM69It0z64zwE7G;'
    for i in ck.split(';'):
        if 'pin=' in i:
            user = i.split('=')[1].strip()
    jd_client = jd(ck, getip_uncheck())
    # jd_client.delete_order('245016422034')
    # jd_client.wait_pay('1010')

    # print(card_id)
    # print(phone)
    # code, order_id, pay_id = jd_client.yk_submit(user, phone, card_id, KLY_505, amount)
    # print(order_id)
    # pay_id = '1ed2bff7519b4a0c97e176a640a22342'
    # jd_client.pay_index(pay_id)
    # code, pay_info = jd_client.sdk_pay(pay_id)
    # print(pay_info)


    # print(create_sdk_pay(user, ck, KLY_505, card_id, amount))
    # pay_id = '78d5ba906c604e4a805d77bdb45fd315'
    # print(real_url(ck, pay_id))
    # ck = 'pin=jd_lzFrcmurRwaM;wskey=AAJhxn6pAECXSZ1eqbF_Odv-JDVIUJVuKpm57sRT6ZO7wFRztU0y0bR3wS0Op64SkYeGxOE3qaxcF7K4Q9UrC7VCfeLMtVpR;'
    ck = 'pin=jd_WvIBKXNckmRW;wskey=AAJhxnxtAECdwgdPGP9J1AuNUzvIxGZO4s5q3ENTp48gl2qTtcD_KCDUfN0FhUhIkkUed-HNKsjtseuI9DRwgXhI6Y1-jYq5;'
    ck = 'pin=jd_DeVbYnTNAZyK;wskey=AAJhxomgAEDyaw0-nF8UbJ3FuJUq--_6oj4phD4aUHBdWbsr6IkgA6rBsVQmO7uILvpngwM7nkL0rk01-LZ0mG7_D73w0S9O; '
    ck = 'pin=jd_jUAIgWbMwdOf;wskey=AAJhxo-iAEB8UAFEsDFiY6YZazbe7Qo-SvRKWU2eyc36xt8rLvzhEle7sbOiJnUMFst3HQYYBed-bxWuIC8V_7u0LleR_IgB;'
    ck = 'pin=jd_bMfNvswgRZFO;wskey=AAJhxoRkAEDMTtTyBFlCHhtB7F6XqJmloNePUca2nzWL0QaODLb2sytkdDjxx8mucwuhUL_B6IQoTjIdt4YrNvq6Yt2NI2TV'
    query_order(ck, '', '248925665512', '205')
    print(order_ios(ck, '', '505', card_id, phone))
