# -*- coding: utf-8 -*-
import base64
import json
from re import I
from termios import OFDEL
import requests
from time import time, sleep
from urllib.parse import quote
import tools
from jingdong import LOG, jd
from ip_sqlite import ip_sql
from jingdong import get_ios_wx
from order_sqlite import order_sql
from urllib.parse import unquote
from tools import LOG_D, byte2str
from tools import xor, get_area

SUCCESS = 1
WEB_CK_UNVALUE = 2
CK_UNVALUE = 3
CK_PAY_FAIL = 4
NETWOTK_ERROR = 5
RET_CODE_ERROR = 6
CK_NO_ADDRESS = 7
UNLOGIN=8
UNKNOW = 9


class pc_jd():

    def __init__(self, ck, proxy_ip=None) -> None:
        self.ck = ck
        if proxy_ip == None:
            self.proxy = None
        else:
            self.proxy = {
                'http': proxy_ip,
                'https':proxy_ip 
            }

    def get_order_url(self, order_no):
        query_list = '[{"orderType":34,"erpOrderId":"' + order_no + '"}]'
        url = 'https://ordergw.jd.com/orderCenter/app/1.0/?callback=jQuery9550751&queryList=' + quote(query_list) + '&_=' + str(int(time())) + '575'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D('代理不可用:' + str(self.proxy))
            return NETWOTK_ERROR, None
        tools.LOG_D(res.text)
        if res.status_code == 200:
            ret = res.text.split('(')[1][0:-1]
            ret_json = json.loads(ret)
            operations = ret_json['appOrderInfoList'][0]['operations']
            for operation in operations:
                if operation['name'] == '付款':
                    return SUCCESS ,'https:' + operation['url']
            return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None


    def get_jmiurl(self, url):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

    def cashier_index(self, cashier_url):
        tools.LOG_D('enter')
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url=cashier_url, headers=head, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

    def get_pay_channel(self, jmi_url):
        params = jmi_url.split('?')[1]
        for param in params.split('&'):
            if 'orderId' in param[0:7]:
                order_id = param.replace('orderId=', '')
            if 'reqInfo' in param[0:7]:
                req_info = param.replace('reqInfo=', '')
            if 'sign' in param[0:4]:
                sign = param.replace('sign=', '')
        url = 'https://pay.jd.com/api-d-cashier/jdpay/getPayChannel?cashierId=1&appId=pcashier'
        data = '{"orderId":"' + order_id + '","reqInfo":"' + req_info + '","sign":"' + sign + '","aksType":"sm","riskReqVo":{"deviceId":"","fingerprint":""}}'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': jmi_url,
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None, None
        if res.status_code == 200:
            ret = res.text
            if '微信支付' not in ret:
                return CK_UNVALUE, None, None, None
            ret_json = json.loads(ret)
            channel_list = ret_json['platPayInfo']['platPayChannelList']
            for channel in channel_list:
                if channel['channelName'] == '微信支付':
                    channelSign = channel['channelSign']
            return SUCCESS, ret_json['paySign'], ret_json['pageId'], channelSign
        else:
            return RET_CODE_ERROR, None, None, None

    def get_pay_channel_qq(self, jmi_url):
        tools.LOG_D('enter')
        params = jmi_url.split('?')[1]
        for param in params.split('&'):
            if 'orderId' in param[0:7]:
                order_id = param.replace('orderId=', '')
            if 'reqInfo' in param[0:7]:
                req_info = param.replace('reqInfo=', '')
            if 'sign' in param[0:4]:
                sign = param.replace('sign=', '')
        url = 'https://pay.jd.com/api-d-cashier/jdpay/getPayChannel?cashierId=1&appId=pcashier'
        data = '{"orderId":"' + order_id + '","reqInfo":"' + req_info + '","sign":"' + sign + '","aksType":"sm","riskReqVo":{"deviceId":"","fingerprint":""}}'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None, None
        if res.status_code == 200:
            ret = res.text
            if '微信支付' not in ret:
                return CK_UNVALUE, None, None, None
            ret_json = json.loads(ret)
            channel_list = ret_json['platPayInfo']['platPayChannelList']
            for channel in channel_list:
                if channel['channelName'] == '微信支付':
                    channelSign = channel['channelSign']
            return SUCCESS, ret_json['paySign'], ret_json['pageId'], channelSign
        else:
            return RET_CODE_ERROR, None, None, None



    def weixin_confirm(self, order_id, pay_sign, amount, page_id, channel_sign):
        tools.LOG_D('enter')
        url = 'https://pcashier.jd.com/weixin/weixinConfirm?cashierId=1&appId=pcashier'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pay.jd.com',
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }
        data = '{"orderId":"' + order_id + '","pageId":"' + page_id + '","paySign":"' + pay_sign + '","riskReqVo":{"deviceId":"","fingerprint":""},' + \
            '"payingChannel":{"bankCode":"weixin","channelSign":"' + channel_sign + '","payAmount":"' + amount + '","agencyCode":"617"}}'
        data = 'bankPayRequestStr=' + quote(data)
        try:
            res = requests.post(url, headers=head, data=data, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']


    def get_weixin_img(self, weixin_page_url, order_id, pay_sign):
        tools.LOG_D('enter')
        url = 'https://pcashier.jd.com/weixin/getWeixinImageUrl?cashierId=1&appId=pcashier'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': weixin_page_url,
            'Origin': 'https://pcashier.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        data = '{"orderId":"' + order_id + '","paySign":"' + pay_sign + '","riskReqVo":{"deviceId":"","fingerprint":""}}'
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            if 'weixinImageUrl' in res.text:
                ret_json = json.loads(res.text)
                return SUCCESS, 'https:' + ret_json['weixinImageUrl'].replace('virtualH5CashierImage?qrCodeSign', 'virtualH5Pay?sign')
            else:
                return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None


    def get_payurl(self, weixin_img_url):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pcashier.jd.com/',
            'Origin': 'https://pcashier.jd.com',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        img = requests.get(weixin_img_url, headers=head, proxies=self.proxy).content
        pay_url = tools.parse_qrcode_local(img)
        print(pay_url)

    def order_place(self, skuid):
        url = 'https://card.jd.com/order/order_place.action?skuId=' + skuid
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Content-Type': 'application/json',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=5)
            # print(res.text)
        except Exception as e:
            tools.LOG_D('代理不可用:' + str(self.proxy))
            # tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            # print(res.text)
            for line in res.text.split('\n'):
                if 'orderParam.winId' in line:
                    line = line.replace(' ', '')
                    win_id = line.replace('<inputtype="hidden"id="winId_"name="orderParam.winId"value="', '')   \
                                .replace('"attr="exclu"sync="true"/>', '')
                    return SUCCESS, win_id
            return CK_UNVALUE, None
        return RET_CODE_ERROR, None

    def submit_order(self, skuid, amount, win_id):
        # url = 'https://card.jd.com/json/order_syncSubmitOrder.action'
        url = 'https://card.jd.com/json/order_syncSubmitOrder.action?now=0.7249590835586648'
        # print(url)
        data = 'webFeOrderInfo.buyNum=1&webFeOrderInfo.payRuleInfo=&webFeOrderInfo.cardNewVersion=1' + \
            '&webFeOrderInfo.payMode=0&webFeOrderInfo.moneyBasic=0&webFeOrderInfo.integralBasic=0&' + \
            'webFeOrderInfo.payPwd=&webFeOrderInfo.couponIds=&webFeOrderInfo.dongCouponIds=&webFeOrderInfo.amountPayable=' + amount + '.00' + \
            '&webFeOrderInfo.couponsAmount=&webFeOrderInfo.jbeanAmount=&orderParam.useBean=&orderParam.gameAreaSrv=2&webFeOrderInfo.skuId=' + \
            skuid + '&webFeOrderInfo.categoryId=13759&orderParam.winId=' + win_id + '&orderParam.secondSource=0&webFeOrderInfo.eid='
        head = {
            'Host': 'card.jd.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Origin': 'https://card.jd.com',
            'Referer': 'https://card.jd.com/order/order_place.action?skuId=' + skuid,
            'Cookie': self.ck,
            'Content-Length': str(len(data) + 2)
        }
        # print(head)

            # skuid + '&webFeOrderInfo.categoryId=13759&orderParam.winId=' + win_id + '&orderParam.secondSource=0'
        # data = 'webFeOrderInfo.buyNum=1&webFeOrderInfo.payRuleInfo=&webFeOrderInfo.cardNewVersion=1&webFeOrderInfo.payMode=0&webFeOrderInfo.moneyBasic=0&webFeOrderInfo.integralBasic=0&webFeOrderInfo.payPwd=&webFeOrderInfo.couponIds=&webFeOrderInfo.dongCouponIds=&webFeOrderInfo.amountPayable=200.00&webFeOrderInfo.couponsAmount=&webFeOrderInfo.jbeanAmount=&orderParam.useBean=&orderParam.gameAreaSrv=2&webFeOrderInfo.skuId=11183368356&webFeOrderInfo.categoryId=13759&orderParam.winId=card_7567142298329571078&orderParam.secondSource=0&webFeOrderInfo.eid='
        # print(data)
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D('代理不可用:' + str(self.proxy))
            # tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            ret_json = res.json()
            tools.LOG_D(res.text)
            if ret_json['code'] == 200:
                url = ret_json['url']
                items = url.split('?')[1].split('&')
                for i in items:
                    if 'orderId' in i:
                        order_no = i.split('=')[1]
                        return SUCCESS, order_no
            elif ret_json['code'] == 31 or '销售火爆' in ret_json['msg']:
                tools.LOG_D(ret_json)
                return CK_UNVALUE, None
            else:
                tools.LOG_D(ret_json)
                return UNKNOW, None
        else:
            return RET_CODE_ERROR, None

    
    def get_order_list(self):
        tools.LOG_D('get_order_list')
        url = 'https://order.jd.com/center/list.action'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None


    def get_order_status(self, order_no):
        query_list = '[{"orderType":34,"erpOrderId":"' + order_no + '"}]'
        url = 'https://ordergw.jd.com/orderCenter/app/1.0/?callback=jQuery7859047&queryList=' + quote(query_list) + '&_=' + str(int(time())) + '049'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy, timeout=5)
            print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None
        if res.status_code == 302:
            if 'https://passport.jd.com' in res.headers['Location']:
                return CK_UNVALUE, None, None
        if res.status_code == 200:
            ret = res.text.split('(')[1][0:-1]
            ret_json = json.loads(ret)
            print(ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name'])
            if ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name'] == '已完成':
                return SUCCESS, True, ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name']
            else:
                return SUCCESS, False, ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name']
        return RET_CODE_ERROR, None, None


    def get_order_status_qb(self, order_no):
        url = 'https://kami.jd.com/order/detail/' + order_no + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            html = res.text.replace(' ', '').replace('\n', '').replace('\t', '')
            if '充值成功' in html.split('state-txt')[1][0:20]:
                return SUCCESS, True, '充值成功'
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None
        return SUCCESS, False, '等待付款'

    def get_kami(self, order_no):
        url = 'https://card.jd.com/order/order_detail.action?orderId=' + order_no
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        res = requests.get(url, headers=head, proxies=self.proxy)
        card_id = None 
        card_key = None 
        pay_time = None 
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'onclick="copyToClipboard(' in line:
                    if '</div>' in line:
                        card_id = line.replace(' ', '').replace('onclick="copyToClipboard(\'', '').replace('\');"></div>', '').replace('\r', '')
                        # print('id', card_id)
                    else:
                        card_key = line.replace(' ', '').replace('onclick="copyToClipboard(\'', '').replace('\');">', '').replace('\r', '')
                        # print('key', card_key)
                if '卡密提取时间' in line:
                    pay_time = line.replace('\r', '').split('时间:')[1]
            if card_id != None and card_key != None:
                return SUCCESS, card_id, card_key, pay_time

    def get_passkey(self, order_no):
        url = 'https://order.jd.com/center/list.action?r=' + str(int(time())) + '784'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }          
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=8)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if '_orderid' in line:
                    if order_no in line:
                        passkey = line.split('_passkey="')[1].replace('"></a>', '')
                        tools.LOG_D(passkey)
                        return SUCCESS, passkey
            return SUCCESS, None
        if res.status_code == 302:
            return CK_UNVALUE, None
        

    def get_recycle_passkey(self, order_no):
        url = 'https://order.jd.com/center/recycle.action?d=1'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }          
        res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
        if res.status_code == 200:
            if '忘记密码' in res.text:
                return UNLOGIN, None
            for line in res.text.split('\n'):
                if '_orderid' in line:
                    if order_no in line:
                        passkey = line.split('_passkey="')[1].replace('"></a>', '')
                        tools.LOG_D(passkey)
                        return SUCCESS, passkey
        else:
            return RET_CODE_ERROR, None



    def recycle_order(self, order_no, passkey):
        url = 'https://order.jd.com/lazy/recycleOrder.action?orderId=' + order_no + '&PassKey=' + passkey + '&callback=jQuery1715934&_=' + str(int(time())) + '685'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None    
        if res.status_code == 200:
            tools.LOG_D(res.text)
            if 'success' in res.text:
                return SUCCESS, True
            else:
                return SUCCESS, False


    def delete_order(self, order_no, passkey):
        url = 'https://order.jd.com/lazy/deleteOrder.action?orderId=' + order_no + '&PassKey=' + passkey + '&callback=jQuery3342349&_=' + str(int(time())) + '149'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            tools.LOG_D(res.text)
            if 'success' in res.text:
                return SUCCESS, True
            else:
                return SUCCESS, False
               
    # ==================== qb =====================
    def qb_get_repeatkey(self, skuid):
        url = 'https://kami.jd.com/order/confirm?skuId=' + skuid + '&quantity=1&source=6&appId=22123-6-001&categoryId=22123'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=5)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if 'repeatKey' in line:
                    repeakey = line.replace(' ', '').replace('<inputtype="hidden"name="repeatKey"value="', '').replace('">', '').replace('\r', '')
                    return SUCCESS, repeakey
            return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None

    def qb_get_jmiurl(self, order_no):
        url = 'https://kami.jd.com/order/getJmiUrl/' + order_no + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
            print(res.headers)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

   
    def qb_submit_order(self, amount, repeatkey, qq):
        url = 'https://kami.jd.com/order/submitOrder?businessType=19&source=6&appCode=109&salePrice=' + amount + \
            '.00&skuPrice=' + amount + '.00&payType=0&orderAmount=' + amount + '.00&onlineAmount=' + amount + \
            '.00&balanceAmount=0&jingdouAmount=0&jingquanAmount=0&dongquanAmount=0&couponIds=&password=&repeatKey=' \
            + repeatkey + '&skuParam.brand=64&skuParam.quantity=1&skuParam.skuId=' + QB_SKUIDS[amount] + \
            '&skuParam.categoryId=22123&features=&rechargeNum=' + qq + '&isCouponBiz=false&stockAvailable=true&eid='
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://kami.jd.com/order/confirm?skuId=' + QB_SKUIDS[amount] + '&quantity=1&source=6&appId=22123-6-001&categoryId=22123',
            'Cookie': self.ck
        }              
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
            print(res.headers)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            return SUCCESS, res.headers['Location']
        else:
            return RET_CODE_ERROR, None

    def clear_order(self, order_no):
        tools.LOG_D(order_no)
        for i in range(3):
            tools.LOG_D('DELETE ORDER ' + str(i))
            code, passkey = self.get_passkey(order_no)
            tools.LOG_D('passKey: ' + str(passkey))
            if code != SUCCESS:
                return code, None
            if passkey == None:
                return code, False
            code, status = self.recycle_order(order_no, passkey)
            if code != SUCCESS:
                return code, None
            if status == True:
                code, passkey = self.get_recycle_passkey(order_no)
                if code != SUCCESS:
                    return code, None
                if passkey == None:
                    return SUCCESS, False
                code, status = self.delete_order(order_no, passkey)
                if code != SUCCESS:
                    return code, None
                if status == True:
                    return SUCCESS, True
            sleep(1)
        return SUCCESS, False

    def weixin_page(self, url):
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }       
        try:
            res = requests.get(url, headers=head, proxies=self.proxy)
            print(res.text)
            print(res.headers)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, False
        if res.status_code == 302:
            # if 'fail' in res.headers['Location']:
                # tools.LOG_D('wxpay can not use')
                # return CK_UNVALUE, False
                return SUCCESS, True
            # else:
                return SUCCESS, True

    def weixin_page_qb(self, url):
        tools.LOG_D('enter')
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pay.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 302:
                if '/success/fail' in res.headers['Location']:
                    tools.LOG_D(res.headers['Location'])
                    return SUCCESS, False
                else:
                    return SUCCESS, True
            return SUCCESS, True
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, False

    def get_unpay(self):
        url = 'https://order.jd.com/center/list.action?s=1'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action?s=1',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
            orders = []
            order = {}
            for line in res.text.split('\n'):
                if 'pay-button-order' in line:
                    print(line)
                    if len(line) < 64:
                        return SUCCESS, orders
                    tmps = line.replace("$ORDER_CONFIG['pay-button-order']='[", '').replace("]';", '').split('},{')
                    for tmp in tmps:
                        for s in tmp.split(','):
                            if 'orderId' in s:
                                order['order_id'] = s.split(':')[1]
                            if 'amount' in s:
                                order['amount'] = s.split(':')[1].replace('.00', '')
                        orders.append(json.dumps(order))
            return SUCCESS, orders
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None

    def get_unpay_appstore_passkey(self, order_id):
        querylist = '[{"orderType":34,"erpOrderId":"' + order_id + '"}]'
        url = 'https://ordergw.jd.com/orderCenter/app/1.0/?callback=jQuery4735171&queryList=' + quote(querylist) + '&_=' + str(int(time())) + '469'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
            # print(res.text)
        except Exception as e:
            tools.LOG_D('代理不可用:' + str(self.proxy))
            # tools.LOG_D(e)
            return NETWOTK_ERROR, None
        order_json = json.loads(res.text.split('(')[1][0:-1])
        for item in order_json['appOrderInfoList']:
            # print(item)
            # print(item['operations'])
            if str(item['orderInfo']['erpOrderId']) == order_id:
                for operation in item['operations']:
                    if operation['style'] == 'btn-pay':
                        return SUCCESS, operation['url'].split('PassKey=')[1]
        return SUCCESS, None





    def get_unpay_appstore(self):
        url = 'https://order.jd.com/center/list.action'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action?s=1',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, timeout=4)
            orders = []
            order = {}
            for line in res.text.split('\n'):
                if 'pay-button-order' in line:
                    print(line)
                    if len(line) < 64:
                        return SUCCESS, orders
                    tmps = line.replace("$ORDER_CONFIG['pay-button-order']='[", '').replace("]';", '').split('},{')
                    for tmp in tmps:
                        for s in tmp.split(','):
                            if 'orderId' in s:
                                order['order_id'] = s.split(':')[1]
                            if 'amount' in s:
                                order['amount'] = s.split(':')[1].replace('.00', '')
                        orders.append(json.dumps(order))
            return SUCCESS, orders
        except Exception as e:
            # tools.LOG_D(e)
            tools.LOG_D('代理不可用:' + str(self.proxy))
            return NETWOTK_ERROR, None


    # def order_center

    def locdetails_order(self, order_id):
        # order_id = '248615578437'
        url = 'https://locdetails.jd.com/pc/locdetail?orderId=' + order_id + '&modelId=2'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action?s=1',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy)
            for line in res.text.split('\n'):
                if 'https://pcashier.jd.com/cashier/index.action' in line:
                    return SUCCESS, line.split('"')[1]
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None

    def jump_url(self, order_id):
        url = 'https://kami.jd.com/order/getJmiUrl/' + order_id + '/39'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 302:
                return SUCCESS, res.headers['Location']
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None

    def jump_url_appstore(self, order_id, passkey):
        url = 'https://card.jd.com/order/order_pay.action?orderId=' + order_id + '&PassKey=' + passkey
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            print(res.text)
            if res.status_code == 302:
                return SUCCESS, res.headers['Location']
        except Exception as e:
            tools.LOG_D('代理不可用:' + str(self.proxy))
            # tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None


    def just_delete(self):
        url = 'https://order.jd.com/center/list.action?t=34-62&d=1&s=4096'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/center/list.action',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy, timeout=4)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:       
            for line in res.text.split('\n'):
                if '$ORDER_CONFIG[\'pop_sign\']=' in line:
                    i = line.replace('$ORDER_CONFIG[\'pop_sign\']=\'[{"orderType":34,"orderIds":["', '').replace('"]}]\';', '')
                    return SUCCESS, i.split('","')
        return SUCCESS, None


    # ============================== new ========================== #    
    def weixin_new(self, order_id, pay_sign, amount, page_id, channel_sign):
        url = 'https://pcashier.jd.com/weixin/weiXinNew?cashierId=1&appId=pc_ls_mall'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://pay.jd.com',
            'Origin': 'https://pay.jd.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }
        data = '{"orderId":"' + order_id + '","pageId":"' + page_id + '","paySign":"' + pay_sign + '","riskReqVo":{"deviceId":"","fingerprint":""},' + \
            '"payingChannel":{"bankCode":"weixin","channelSign":"' + channel_sign + '","payAmount":"' + amount + '","agencyCode":"617"}}'
        data = 'bankPayRequestStr=' + quote(data)
        try:
            res = requests.post(url, headers=head, data=data, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 302:
            if '/success/fail' in res.headers['Location']:
                tools.LOG_D(res.headers['Location'])
                return CK_UNVALUE, None
            return SUCCESS, res.headers['Location'].replace('appId=pcashier', 'appId=pc_ls_mall')




amount = '200.00'

APPSTORE_SKUIDS = {
    '10': '10022039398507',
    '50': '11170365589',
    '100': '11183343342',
    '200': '11183368356',
    '500': '11183445154',
    '1000': '13138170874'
}

QB_SKUIDS = {
    '11': '200145364712',
    '105': '200145365539',
    '210': '200145348880',
    '586': '10048511037815',
    '68': '200153870251',
    '305': '200153773388'
}

DNF_SKUIDS = {
    '50': '200153770492',
    '80': '200153769485',
    # '100': '200153773388'
    '100': '200145201414'
}


def create_order_appstore(ck, order_me, amount, proxy):
    tools.LOG_D('create_order_appstore')
    # ========test=========
    pc_client = pc_jd(ck, proxy)
    code, order_no, cashier_url = get_useful_unpay_appstore(ck, amount, proxy)
    if code != SUCCESS:
        return code, None, None
    if order_no == None:
        code, win_id = pc_client.order_place(APPSTORE_SKUIDS[amount])
        tools.LOG_D(win_id)
        if code != SUCCESS:
            return code, None, None
        sleep(3)

        code, order_no = pc_client.submit_order(APPSTORE_SKUIDS[amount], amount, win_id)
        tools.LOG_D(order_no)
        if code != SUCCESS:
            return code, None, None
        code, order_url = pc_client.get_order_url(order_no)
        if code != SUCCESS:
            return code, None, None
        code, cashier_url = pc_client.get_jmiurl(order_url)
        if code != SUCCESS:
            return code, None, None

    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel(cashier_url)
    if code != SUCCESS:
        return code, None, None

    for i in range(2):
        code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
        if code != SUCCESS:
            return code, None, None
        tools.LOG_D(weixin_page_url)
        code, status = pc_client.weixin_page_qb(weixin_page_url)
        if code != SUCCESS:
            return code, None, None
        if status == True:
            break
        code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
        if code != SUCCESS:
            return code, None, None
        sleep(1)
        i += 1

    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    LOG_D(img_url)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url


def test_create_order_appstore(ck, order_me, amount, proxy):
    tools.LOG_D('create_order_appstore')
    # ========test=========
    pc_client = pc_jd(ck, proxy)

    order_no = '249240135597'
    cashier_url = 'https://pcashier.jd.com/cashier/index.action?orderId=249240135597&reqInfo=eyJjYXRlZ29yeSI6IjEiLCJjb21wYW55SWQiOiI2Iiwib3JkZXJBbW91bnQiOiIyMDAuMDAiLCJvcmRlcklkIjoiMjQ5MjQwMTM1NTk3Iiwib3JkZXJUeXBlIjoiMzQiLCJwYXlBbW91bnQiOiIyMDAuMDAiLCJ0b1R5cGUiOiIxMCIsInZlcnNpb24iOiIzLjAifQ==&sign=5ad314d41181af1a2adc9765899b2e05'
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel(cashier_url)
    if code != SUCCESS:
        return code, None, None

    for i in range(2):
        code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
        if code != SUCCESS:
            return code, None, None
        tools.LOG_D(weixin_page_url)
        code, status = pc_client.weixin_page_qb(weixin_page_url)
        if code != SUCCESS:
            return code, None, None
        if status == True:
            break
        code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
        if code != SUCCESS:
            return code, None, None
        sleep(1)
        i += 1

    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    LOG_D(img_url)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url





def order_appstore(ck, order_me, amount):
    area = get_area(ck)
    if area == None:
        upload_order_result(order_me, '', '', amount, '0')
        return
    tools.LOG_D(area)
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('========================================== create order ======================================== account: ' + str(account))
    proxy = ip_sql().search_ip(account)
    # tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(5):
        code, order_no, img_url = create_order_appstore(ck, order_me, amount, proxy)
        if code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            if proxy == None:
                return NETWOTK_ERROR
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
        else:
            break
        i += 1
    tools.LOG_D(img_url)
    upload_order_result(order_me, order_no, img_url, amount, ck_status)


def get_useful_unpay(ck, amount, proxy):
    tools.LOG_D('enter')
    pc_client = pc_jd(ck, proxy)
    code, orders =  pc_client.get_unpay()
    if code != SUCCESS:
        return code, None, None
    if orders == None:
        return SUCCESS, None, None
    for order in orders:
        order = json.loads(order)
        if amount == str(order['amount']):
            order_id = str(order['order_id'])
            last_time = order_sql().search_order(order_id)
            now_time = str(int(time()))
            if last_time != None:
                # if int(now_time) - int(last_time) > 600:
                if int(now_time) - int(last_time) > 600:
                    code, cashier_url = pc_client.jump_url(order_id)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None

def get_useful_unpay_appstore(ck, amount, proxy):
    tools.LOG_D('enter')
    pc_client = pc_jd(ck, proxy)
    code, orders =  pc_client.get_unpay_appstore()
    if code != SUCCESS:
        return code, None, None
    if orders == None:
        return SUCCESS, None, None
    for order in orders:
        order = json.loads(order)
        if amount == str(order['amount']):
            order_id = str(order['order_id'])
            last_time = order_sql().search_order(order_id)
            now_time = str(int(time()))
            if last_time != None:
                # if int(now_time) - int(last_time) > 600:
                if int(now_time) - int(last_time) > 780:
                    code, passkey = pc_client.get_unpay_appstore_passkey(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    code, cashier_url = pc_client.jump_url_appstore(order_id, passkey)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None


def test_order_appstore(ck, order_me, amount):
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    proxy = tools.getip_uncheck()
    for i in range(3):
        code, order_no, img_url = create_order_appstore(ck, order_me, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            break
        elif code == RET_CODE_ERROR:
            return None
        i += 1
    tools.LOG_D(img_url)
    upload_order_result(order_me, order_no, img_url, amount, ck_status)



def get_real_url(ck, img_url, os):
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    area = get_area(ck)
    tools.LOG_D(area)
    account = tools.get_jd_account(ck)
    proxy = None
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)
    for i in range(6):
        app_client = jd(ck, proxy)
        tools.LOG_D(img_url)
        code, token = app_client.gen_token(img_url)
        tools.LOG_D(token)
        if code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            if proxy == None:
                return None
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

def upload_callback_result(result):
    # return True
    url = 'http://127.0.0.1:9191/api/ordernotify/notifyorderstatus0069'
    head = {
        'content-type': 'application/json'
    }
    tools.LOG_D(result)
    res = requests.post(url, headers=head, data=result).json()
    tools.LOG_D(str(result) + '\nret:' + json.dumps(res))
    if res['code'] == 0 or res['code'] == '0':
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
        tools.LOG_D(e)
        return
    print(res.text)


def query_order_appstore(ck, order_me, order_no, amount):
    area = get_area(ck)
    tools.LOG_D(area)
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
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        pc_client = pc_jd(ck, proxy)
        code, order_status, status_name = pc_client.get_order_status(order_no)
        if code == SUCCESS:
            if order_status == True and status_name == '已完成':
                code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
                result['card_name'] = card_id
                result['card_password'] = card_key
                result['pay_status'] = '1'
                # tools.LOG_D(card_id + ' = ' + card_key + ' = ' + pay_time)
                result = json.dumps(result)
                if upload_callback_result(result):
                    if order_status == True and status_name == '已完成':
                        # pc_client.clear_order(order_no)
                        tools.LOG_D('wait delete ' + order_no)
                        sleep(30)
                        for i in range(8):
                            if just_del(ck, order_no) == False:
                                continue
                            else:
                                return
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            if proxy == None:
                result = json.dumps(result)
                upload_callback_result(result)
                return 
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1



def query_order_appstore_immediate(ck, order_me, order_no, amount):
    for i in ck.split(';'):
        if 'upn=' in i:
            area = i.split('=')[1].replace(' ', '')
    area = xor(area)
    area = str(base64.b64decode(bytes(area, encoding='utf-8')), encoding='utf-8')
    tools.LOG_D(area)
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
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        proxy = tools.getip_uncheck(area)
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        pc_client = pc_jd(ck, proxy)
        code, order_status, status_name = pc_client.get_order_status(order_no)
        if code == SUCCESS:
            if order_status == True and status_name == '已完成':
                code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
                result['card_name'] = card_id
                result['card_password'] = card_key
                result['pay_status'] = '1'
                # tools.LOG_D(card_id + ' = ' + card_key + ' = ' + pay_time)
                result = json.dumps(result)
                if upload_callback_result(result):
                    if order_status == True and status_name == '已完成':
                        # pc_client.clear_order(order_no)
                        tools.LOG_D('wait delete ' + order_no)
                        sleep(30)
                        for i in range(8):
                            if just_del(ck, order_no) == False:
                                continue
                            else:
                                return
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck(area)
            if proxy == None:
                result = json.dumps(result)
                upload_callback_result(result)
                return 
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1


def just_del(ck, order_id):
    if '&' not in ck:
        area = '上海市'
    else:
        area = ck.split('&')[1]
        area = unquote(area)
    tools.LOG_D(area)
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(8):
        pc_client = pc_jd(ck, proxy)
        # code, orders = pc_client.just_delete()
        # for order in orders:
            # pc_client.clear_order(order)
        sleep(10)
        code, status = pc_client.clear_order(order_id)
        if code == SUCCESS:
            if status == True:
                return True
            else:
                continue
        elif code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            if proxy == None:
                return False
            ip_sql().update_ip(account, proxy)
            continue
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            return False
        i += 1
    return False


def callback(ck, order_no, order_me, amount):
    result = {
        'check_status': '',
        'pay_status': '',
        'ck_status': '',
        'time': '',
        'order_me': order_me,
        'order_pay': order_no,
        'amount': amount,
        'card_name': '',
        'card_password': ''
    }
    proxy = None
    pc_client = pc_jd(ck)
    code, order_status, status_name = pc_client.get_order_status(order_no)
    if code != SUCCESS:
        pass
    if order_status == True and status_name == '已完成':
        code, card_id, card_key, pay_time = pc_client.get_kami(order_no)
        tools.LOG_D(card_id, card_key, pay_time)
        result['check_status'] = '1'
        result['pay_status'] = '1'
        result['ck_status'] = '1'
        result['order_me'] = order_me
        result['order_pay'] = order_no
        result['card_name'] = card_id
        result['card_password'] = card_key
    else:
        result['check_status'] = '1'
        result['pay_status'] = '0'
        result['ck_status'] = '1'
        result['order_me'] = order_me
        result['order_pay'] = order_no
        pass
    result = json.dumps(result)
    if upload_callback_result(result):
        if order_status == True and status_name == '已完成':
            pc_client.clear_order(order_no)



if __name__=='__main__':
    # print(order_qb(ck, '', '305', '13562365463'))
    # dnf80 = '200153769485'
    # amount = '80'
    # ck = ck.encode('utf-8').decode('latin-1')
    # pc_client = pc_jd(ck, None)
    # just_del(ck, '249031984259')
    # print(create_order_knowkedge(ck, amount, DNF_SKUIDS[amount], '52313461', getip_uncheck()))
    # print(create_order_knowkedge(ck, amount, DNF_SKUIDS[amount], '52353462', None))
    # print(order_knowkedge(ck, '', '100', '2325463432'))
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=1c268751b4d3f5ec8ab255c01537372beaba8a259a056385a9bd95fcd26aa269940ec59282a6f63c01bd8878f9ecb403cb6b510cd1fa1d15aeca8ceb7551ed069dad0fe81d042f848ab3f603f57cf109'
    # url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=a8992807ee08692fed8c70bab00cf1bbb09d4f2da4444431ac45a211c20a4b5826cef82354c2cf661474df9c82776427122f64c16e897369932856dd0260db749dad0fe81d042f848ab3f603f57cf109'
    # url = 'https://m.jd.com'
    # print(get_real_url(ck, url, ''))
    # print(get_real_qb(ck, '248592464389=105'))
    # ck = 'TrackID=111KcnzbgCLOX0dBwPVaPjJ7p0xP_NXeXirMUzvceY2_TntDiEgAXN-1lBX_J5bs5bHkQJKa1rhpCbRrU4iynq5JS__DuYcru8ee3-g_PFXg; thor=FC9B022D341ECFD774F842E36094AEF123AD852701730188F7590831FDDAE9DD11E213C40AF53B10C520DCC6A6ACAC344744B19968F9DA58D5ACEFF88C1E1C29DCCE4A8FF196FB1C365801049299C79B148C6EB4DEED547FCE9A5164CC6B33DF0D08DA5DBBC117DCF0435B1C16807662532169F459D55D484A2093B19A03865C937B1376E9EFFB14249EF4DD59F99020FBEDFA51DF90EEC854D27D2CA2932F94; pinId=0_w1fANft98aiSkPILLWKrGag-k0Ux-h; pin=jd_NNkr7iYWTG4Brs7; unick=jd_NNkr7iYWTG4Brs7; _tp=8T6K424Lny7kMLh2lzjyyFFfYXzHwuNDp0n2GazI7mk%3D; _pst=jd_NNkr7iYWTG4Brs7; upn=4cFy4Mhb44xC4sVN4X3Y4chB; pin=jd_NNkr7iYWTG4Brs7; wskey=AAJivJ1RAFDdWiM-xVMJL1oJ8RHxuArapR6Ey7_kVcpfd0lTJwWcH5CmHbo6ooWTtUshPFz2fivg2fOKOPtoEuvzUygSLoICTaPneUTMJcHy6zelNpxQrA;'
    # order_appstore(ck, '', '200')
    ck = '__jdu=16509706855941893098380; shshshfpa=24b6bb36-e2eb-935b-8da5-4244c2284385-1654941526; shshshfpb=zgH442FN956xyfHqjr4f9ag; user-key=b713e0dc-ea97-4f4b-8edb-4e1a16076df9; areaId=5; __jdv=122270672|direct|-|none|-|1656239716924; PCSYCityID=CN_130000_130100_0; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; _tp=VHnhiNi86OlY5d%2BSKBX0iW%2BQy5xFBy0C7MU1%2BoxmN9c%3D; _pst=jd_4d9b500034155; ipLoc-djd=5-142-157-42800.8254666397; ipLocation=%u6cb3%u5317; ceshi3.com=201; TrackID=1R_A8rHgeI7vzoyuuV8OpyQxypRf0Gmmvm2q-CnDieNN3-LrcoyM2jz3YqTGn_LniqeeftGOAAqJ812uCPkXdyys1eU7H2n9ruyVkrM2CcS9kZPYDNj8K71TclM9_QvevolOmyzOxPZCdjMn-vaRLfQ; unick=%E6%98%AF%E7%9A%84%E6%98%AF%E7%9A%84%E6%98%AF%E7%9A%84456; qd_uid=L50PLJ0S-087W47I0YU1AGM018Z6Q; qd_fs=1656574352523; qd_ls=1656574352523; shshshfp=b4abc46426debf37b8d70e31836b233e; ip_cityCode=142; cn=3; qd_sq=2; qd_ts=1656592096033; 3AB9D23F7A4B3C9B=L4VA3H3XRQXTHOSQML6VS3B7QYYN7GVIBS2KPYED4PB7WAMMO52MPHRJZLNNWXPSPTBNDJOKGTPD7SIYJTCJZFPFE4; qd_ad=-%7C-%7Cdirect%7C-%7C0; __jda=187205033.16509706855941893098380.1650970686.1656587795.1656590969.71; __jdc=187205033; _distM=249281234915; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A74540A1267F67F4089906566E57F89A8447016F745C7CF4A4DE60036EBE85F2B05C29922B8DA9C44E7D2218CA90317BF82F2D7EA0285D4A92BAA2DB832BE14DD1BEF6A84FB9D8339C005EE04BD096724CC506A53D5D899FA8036BDB6ABDFC60B1DCEA5963E786794CEED84A90AA18A1ECE7AE6ABCB44861AE88AD4CB5347DA08D0B; __jdb=187205033.23.16509706855941893098380|71.1656590969'
    test_create_order_appstore(ck, '', '204', None)
 
    # print(query_order_qb(ck, '', DNF_SKUIDS['50'], '50'))
    # test(ck)
    # callback(ck, '247486125452', '123', '100')
    # clear_order(ck, '247761070918')
    # 06:50
    # 07:18
    # weixin_page_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=699d3620bdddb2cd1d9471b07eca4efedef02545e1061f0cc3119c5588f40c8c5893c0c857e10c555aecefb46ea62f518caa1476b7d3513d6242fad999a962a0c1b0c4ab88b7e0928f8872365c7dde35'
    # weixin_page_url = 'https://m.jd.com'
    # print(get_real_url(ck, weixin_page_url, 'ios'))
    # order_no = '247574887620'
    # callback(ck, order_no)
    # upload_order_result('124', '123','http://www.baidu.com', '100')