# -*- coding: utf-8 -*-
import base64
import hashlib
import time
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import unquote
import uuid
import requests
import json
from hashlib import md5
from tools import random_phone
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

KLY_505 = '200153481018'

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
   KLY_505:{
       'face_price': '50000',
       'online_price': '50500'
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
        print(body)
        try:
            resp = requests.post(url=url + params, data=body, headers=headers, proxies=self.proxy)
            print(resp.text)
        except:
            return NETWOTK_ERROR
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
        except:
            print('===== submit error ======')
            return NETWOTK_ERROR, None, None
        print(resp.text)
        if resp.status_code == 200:
            ret_json = resp.text.split('(')[1]
            ret_json = ret_json.split(')')[0]
            ret_json = json.loads(ret_json)
            if ret_json['msg'] == 'SUCCESS':
                return SUCCESS, ret_json['data']['orderId'], ret_json['data']['payId']
            elif ret_json['msg'] == '不能下单' or '您的账户下单过于频繁' in ret_json['msg'] or 'no permissions' in ret_json['msg']:
                return CK_UNVALUE, None, None
        return RET_CODE_ERROR, None, None

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
    # ip = get_ip()
    # if(ip == None):
        # print(account + 'get proxy error')
        # return
    ip = getip_uncheck()
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

def create_order(account, ck, sku_id, card_id, amount, phone_type):
    if phone_type == ANDROID:
        return create_df_pay(account, ck, sku_id, card_id, amount)
    elif phone_type == IOS:
        return create_sdk_pay(account, ck, sku_id, card_id, amount)
     
        

if __name__ == '__main__':
    good_id = '10045398811484'
    amount = '103'
    good_id_206 = '10045398948206'
    good_id_309 = '10045399054885'


    phone = '13367849114'
    amount = '505'
    card_id = '1000113200034820713'
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
    # ck = 'pin=4d9b500034155; wskey=AAJioezoAECwBP5u00yWw4Wmm1VoGgB6DKaGtp_iF-nnh3LMty5vhN6xuU0oVyMTQ9ENxG8Wyb2utzOCDrs5gulgXGCajild;'
    ck = 'guid=45d763d66f8a1e21cea7f9b1aedbbebe58dd7e3bc040f15ca83e875fccfcb16e; pt_key=app_openAAJiqYuSAEDRuA__A6tK47tOg5LStzonkj33X_7R0aDB6xBCYZw2nrSYjTfSWa75VUuSfpRSOsrJk8eS4vZ7E7gcKhrBLWOH; pt_pin=jd_ZW8vrsHz0s57jZk; pwdt_id=jd_ZW8vrsHz0s57jZk; sid=392bc5983122f98dafdda9622dae98dw; pin=jd_ZW8vrsHz0s57jZk;wskey=AAJiHCtRAFDzK3DBRZbGte0raavmaLNSMUnyuzfjbO9j1Knl7wYzGSvz8Q3uNSVnjt6AOjP0pNmWxmFW-4U8xUscpW26vPmJlhHASTJjznsGquo5Y1Lg8w==;'
    ck = 'guid=c638ee7574571d55b9b272f9b578f98c40e68ec22c31f4ebbda832602e7717b3; pt_key=app_openAAJiqYuTAEDcSDrKEK1FstIFRpTJcMyrRc4sDbNcc8NgVlyJBp6KPkqifzjQ_WlcJmRQm12SpBbby_BEA8EXXxMNobxBxe_3; pt_pin=jd_DoUiY6tydHRrJxb; pwdt_id=jd_DoUiY6tydHRrJxb; sid=79aaefb3989577337b1ee1a899ca331w; pin=jd_DoUiY6tydHRrJxb;wskey=AAJiDI4YAFBNgPdxb1j_UEKipLFNPexZ0iQ-voK5aRMf4G5ZK5pSeCnH6LRkspKuUL0-X1B9TNEUSswMbDPK7Mu1A7df8KZKdX9afSjnRe6-lj2Xvh4WAg==;'
    for i in ck.split(';'):
        if 'pin=' in i:
            user = i.split('=')[1].strip()
    # jd_client = jd(ck, getip_uncheck())
    jd_client = jd(ck)
    # url = 'https://oilcard.m.jd.com/?skuId=200153481018'
    # url = 'https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html'
    # code, token = jd_client.gen_token(url)
    # print(token)
    # token_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
    # code, mck = jd_client.get_mck(token_url)
    # print(mck)
    # jd_client.ck = jd_client.ck + mck
    # print(jd_client.ck)
    # code, order_id, pay_id = jd_client.yk_submit(user, phone, card_id, KLY_505, amount)
    pay_id = '80069608df2840889746192ccc98f8eb'
    print(pay_id)
    jd_client.pay_index(pay_id)
    code, pay_info = jd_client.sdk_pay(pay_id)
    print(pay_info)