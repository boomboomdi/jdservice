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
from jingdong import get_ios_wx, check
from order_sqlite import order_sql
from urllib.parse import unquote
from tools import LOG_D, byte2str, getip_fensheng
from tools import xor, get_area, get_ip_info

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


    def jump_url_knowledge(self, order_id):
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

    def test(self):
        tools.LOG_D('enter')

    
    def knowledge_get_repetkey(self, skuid):
        tools.LOG_D('enter')
        url = 'https://v-knowledge.jd.com/order/confirm?skuId=' + skuid + '&quantity=1&source=6'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://cartv.jd.com/',
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
                    repeakey = line.replace(' ', '').replace('<inputtype="hidden"id="repeatKey"name="repeatKey"value="', '').replace('">', '').replace('\r', '')
                    repeakey = repeakey.encode("utf-8").decode("latin1")
                    # repeakey = repeakey.encode("UTF-8").decode("UTF-8")
                    print(repeakey)
                    return SUCCESS, repeakey
            return CK_UNVALUE, None
        else:
            return RET_CODE_ERROR, None



    def knowledge_submit(self, skuid, repeatKey, price, qq):
        tools.LOG_D('enter')
        url = 'https://v-knowledge.jd.com/order/submitOrder'
        data = 'skuParam.quantity=1&skuParam.skuId=' + skuid + '&businessType=6&source=6&repeatKey=' + repeatKey + \
            '&salePrice=' + price + '.00&payType=0&orderAmount=' + price + '.00&onlineAmount=' + price + '.00&balanceAmount=0' + \
            '&jingdouAmount=0&jingquanAmount=0&dongquanAmount=0&couponIds=&rechargeNum=' + qq + '&password=d41d8cd98f00b204e9800998ecf8427e' + \
            '&features=&skuParam.activityId='
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://v-knowledge.jd.com/order/confirm?skuId=' + skuid + '&quantity=1&source=6',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }              
        try:
            res = requests.post(url, headers=head, data=data, allow_redirects=False, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            if 'redirectUrl' in res.text:
                if '销售火爆' in res.text:
                    return CK_UNVALUE, None
                return SUCCESS, res.json()['redirectUrl']
        if res.status_code == 302:
            if 'orderId' in res.headers['Location']:
                return SUCCESS, res.headers['Location']
        return CK_UNVALUE, None


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
    '100': '200153999145',
    '200': '200153966433',
    '300': ''
}

DNF_SKUIDS = {
    '50': '200153770492',
    '80': '200153769485',
    # '100': '200153773388'
    '100': '200145201414'
}


def create_order_appstore_back(ck, order_me, amount, proxy):
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
        # code, weixin_page_url = pc_client.weixin_new(order_no, pay_sign, amount, page_id, channel_sign)
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

    # code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    # if code != SUCCESS:
        # return code, None, None
    # tools.LOG_D(weixin_page_url)
    # code, status = pc_client.weixin_page(weixin_page_url)
    # if code != SUCCESS:
        # return code, None, None
    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    LOG_D(img_url)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url


def create_order_appstore(ck, order_me, amount, proxy):
    tools.LOG_D('create_order_appstore')
    # ========test=========
    pc_client = pc_jd(ck, proxy)
    code, order_no, cashier_url = get_useful_unpay_appstore(ck, amount, proxy)
    if code != SUCCESS:
        return code, None
    if order_no == None:
        code, win_id = pc_client.order_place(APPSTORE_SKUIDS[amount])
        tools.LOG_D(win_id)
        if code != SUCCESS:
            return code, None
        sleep(3)
        code, order_no = pc_client.submit_order(APPSTORE_SKUIDS[amount], amount, win_id)
        tools.LOG_D(order_no)
        if code != SUCCESS:
            return code, None
    return code, order_no


def order_appstore_back(ck, order_me, amount):
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
    pay_info = ''
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(5):
        code, order_no = create_order_appstore(ck, order_me, amount, proxy)
        if code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            if proxy == None:
                return NETWOTK_ERROR
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            # pay_info = order_no + '#' + amount
            pay_info = order_no
            order_sql().insert_order(order_no, amount)
            order_sql().update_order_time(order_no)
            break
        elif code == RET_CODE_ERROR:
            return None
        else:
            break
        i += 1
    tools.LOG_D('========== create result: ' + str(order_no) + ' ===========')
    upload_order_result(order_me, order_no, pay_info, amount, ck_status)




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
                if int(now_time) - int(last_time) > 610:
                    code, passkey = pc_client.get_unpay_appstore_passkey(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    code, cashier_url = pc_client.jump_url_appstore(order_id, passkey)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None



def get_useful_unpay_knowledge(ck, amount, proxy):
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
                if int(now_time) - int(last_time) > 100:
                    code, cashier_url = pc_client.jump_url(order_id)
                    # code, cashier_url = pc_client.locdetails_order(order_id)
                    if code != SUCCESS:
                        return code, None, None
                    return SUCCESS, order_id, cashier_url
    return SUCCESS, None, None




def order_qb(ck, order_me, amount, qq):
    code = NETWOTK_ERROR
    area = get_area(ck)
    if area == None:
        upload_order_result(order_me, '', '', amount, '0')
        return
    tools.LOG_D(area)
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('========================================== create order qb ======================================== account: ' + str(account))
    proxy = ip_sql().search_ip(account)
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(5):
        code, order_no, img_url = create_order_qb(ck, order_me, amount, qq, proxy)
        if code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
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
    tools.LOG_D(img_url)
    # order_no = '1234567891'
    # img_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=91cdd3c81ca4eb0e567ae1aa974c0edc26ca3884223ba250dbcfa8810261853e2328b54465304f257d4cf742590d02052b86033b07b653b048611091e50a63b4c1b0c4ab88b7e0928f8872365c7dde35'
    upload_order_result(order_me, order_no, img_url, amount, ck_status)


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
    # upload_order_result(order_me, '', '', amount, ck_status)



def create_order_qb(ck, order_me, amount, qq, proxy):
    pc_client = pc_jd(ck, proxy)
    code, order_no, cashier_url = get_useful_unpay(ck, amount, proxy)
    if code != SUCCESS:
        return code, None, None
    if cashier_url == None:
        code, repeatkey = pc_client.qb_get_repeatkey(QB_SKUIDS[amount])
        print(repeatkey)
        if code != SUCCESS:
            return code, None, None
        code, cashier_url = pc_client.qb_submit_order(amount, repeatkey, qq)
        print(cashier_url)
        for i in cashier_url.split('?')[1].split('&'):
            if 'orderId' in i:
                order_no = i.split('=')[1]
    # return SUCCESS, order_no, order_no
    # print(order_no)
    code, cashier_url = pc_client.cashier_index(cashier_url)
    print(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    # code, weixin_page_url = pc_client.weixin_new(order_no, pay_sign, amount, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    tools.LOG_D(weixin_page_url)
    code, status = pc_client.weixin_page_qb(weixin_page_url)
    if code != SUCCESS:
        return code, None, None
    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url


def create_order_knowkedge(ck, amount, skuid, qq, proxy):
    pc_client = pc_jd(ck, proxy)
    code, order_no, cashier_url = get_useful_unpay(ck, amount, proxy)
    if code != SUCCESS:
        return code, None, None
    if cashier_url == None:
        code, repeatkey = pc_client.knowledge_get_repetkey(skuid)
        print(repeatkey)
        pc_client.test()
        if code != SUCCESS:
            return code, None, None
    # return None
        code, cashier_url = pc_client.knowledge_submit(skuid, repeatkey, amount, qq)
        if code != SUCCESS:
            return code, None, None
        for i in cashier_url.split('?')[1].split('&'):
            if 'orderId' in i:
                order_no = i.split('=')[1]
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None

    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None

    for i in range(5):
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
        sleep(1)
        i += 1

    if status == False:
        return CK_UNVALUE, None, None


    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    print('success', img_url)
    return code, order_no, img_url


def order_knowkedge(ck, order_me, amount, qq):
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
        code, order_no, img_url = create_order_knowkedge(ck, amount, DNF_SKUIDS[amount], qq, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck()
            if proxy == None:
                return None
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
    tools.LOG_D(img_url)
    upload_order_result(order_me, order_no, img_url, amount, ck_status)



def create_order_qb_unpay(ck, order_me, amount, qq, proxy):
    pc_client = pc_jd(ck, proxy)
    code, repeatkey = pc_client.qb_get_repeatkey(QB_SKUIDS[amount])
    print(repeatkey)
    if code != SUCCESS:
        return code, None, None
    code, cashier_url = pc_client.qb_submit_order(amount, repeatkey, qq)
    for i in cashier_url.split('?')[1].split('&'):
        if 'orderId' in i:
            order_no = i.split('=')[1]
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None
    tools.LOG_D(weixin_page_url)
    # weixin_page_url = 'https://pcashier.jd.com/weixin/weixinPage?cashierId=1&orderId=248572526985&sign=a2dbea7cfcbc9d5ba448d6b0ade9bb6b&appId=pcashier'
    code, status = pc_client.weixin_page_qb(weixin_page_url)
    if code != SUCCESS:
        return code, None, None
    if status == False:
        return CK_UNVALUE, None, None
    code, img_url = pc_client.get_weixin_img(weixin_page_url, order_no, pay_sign)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url



    # app_client.gen_token()
    # img_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=a78134e5944ce6619b7a54d2649898586b4776d24acc654320214577da92c7cbcd92cf045f5eab8bd50492fd2bf6035d45eb0db7d81e99916b6e43eeab562ba13b9487beaf0dcae568f49411ab2e64b3'
    # code, token  = app_client.gen_token(img_url)
    # pay_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token 
    # print(pay_url)

def get_real_qb(ck, order_info):
    order_no = order_info.split('=')[0]
    amount = order_info.split('=')[1]
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
        code, pay_url = get_ios_wx(ck, order_no, amount, proxy)
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



def get_real_url_back(ck, img_url, os, ip):
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    pro, city = get_ip_info(ip)
    if pro == None:
        pass
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

def get_real_url(ck, pay_info, amount, os, ip):
    area = get_area(ck)
    result = {
        'code': '1',
        'data': '',
        'msg': ''
    }
    proxy = None
    pro, city = get_ip_info(ip)
    if pro == None:
        area, proxy = tools.getip_uncheck(area)
    else:
        proxy = getip_fensheng(pro, city)
        if proxy == None:
            area, proxy = tools.getip_uncheck(area)
    account = tools.get_jd_account(ck)
    for i in range(6):
        if os == 'android':
            r = {}
            r['ck'] = ck
            r['order_id'] = pay_info
            result['code'] = '0'
            result['data'] = json.dumps(r)
            result['msg'] = 'success'
            return json.dumps(result)
        elif os == 'ios':
            order_id = pay_info.split('#')[0]
            # amount =  pay_info.split('#')[1]
            code, pay_url = get_ios_wx(ck, order_id, amount, proxy)
        if code == NETWOTK_ERROR:
            if pro == None:
                area, proxy = tools.getip_uncheck(area)
            else:
                proxy = getip_fensheng(pro, city)
                if proxy == None:
                    area, proxy = tools.getip_uncheck(area)
        elif code == CK_UNVALUE:
            result['msg'] = 'ck unvalue'
            break
        elif code == SUCCESS:
            result['code'] = '0'
            result['data'] = pay_url
            result['msg'] = 'success'
            return json.dumps(result)
        i += 1
    print(json.dumps(result))
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
    if img_url == None or img_url == '':
        data['prepare_status'] = '0'
    data = json.dumps(data)
    tools.LOG_D(data)
    try:
        res = requests.post(url, headers=head, data=data)
    except Exception as e:
        tools.LOG_D(e)
        return
    print(res.text)

    
def handle_fail(code):
    pass


def test(ck):
    pc_client = pc_jd(ck)
    pc_client.get_order_url('247682795586')


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



def query_order_appstore_im(ck, order_me, order_no, amount):
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
                # if upload_callback_result(result):
                if order_status == True and status_name == '已完成':
                    # pc_client.clear_order(order_no)
                    tools.LOG_D('wait delete ' + order_no)
                    sleep(30)
                    for i in range(8):
                        if just_del(ck, order_no) == False:
                            return result
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



def query_order_qb(ck, order_me, order_no, amount):
    code = NETWOTK_ERROR
    area = get_area(ck)
    if area == None:
        upload_order_result(order_me, '', '', amount, '0')
        return
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
    for i in range(5):
        jd_client = jd(ck, proxy)
        code, order_status = jd_client.search_order_detail(order_no)
        if code == SUCCESS:
            if order_status == True:
                result['pay_status'] = '1'
                result['card_name'] = 'QB_' + str(time()).replace('.', '')
                result['card_password'] = 'QB_' + str(time()).replace('.', '')
                result = json.dumps(result)
                upload_callback_result(result)
                order_sql().delete_order(order_no)
            else:
                result = json.dumps(result)
                upload_callback_result(result)
            return
        elif code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            upload_callback_result(result)
            return
        i += 1

    result = json.dumps(result)
    upload_callback_result(result)


def query_order_qb_im(ck, order_me, order_no, amount):
    code = NETWOTK_ERROR
    area = get_area(ck)
    if area == None:
        return None
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
    for i in range(5):
        jd_client = jd(ck, proxy)
        code, order_status = jd_client.search_order_detail(order_no)
        if code == SUCCESS:
            if order_status == True:
                result['pay_status'] = '1'
                result['card_name'] = 'QB_' + str(time()).replace('.', '')
                result['card_password'] = 'QB_' + str(time()).replace('.', '')
                result = json.dumps(result)
                upload_callback_result(result)
                order_sql().delete_order(order_no)
            else:
                result = json.dumps(result)
                return result
            return
        elif code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            return result
            return
        i += 1

    result = json.dumps(result)
    return result




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
        sleep(15)
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


    #AP2022070513074870898896  249369700077 
    # ck = 'pin=jd_Fa9XQOpktFRLESz; wskey=AAJiicA8AFCrrXT0uvmQaWf4LdHpWvKoq8nszucBbZf6QFsUqFLc6iRD2nXH0IJo9H4ZQvhpymzAE4MCFX3RWYm_09EZrudO7jej5avhbkGtfraqdUMimQ;'
    # ck = 'TrackID=1Lw5YMBRIiavicT70bqa8-bXF6luAuo10HryM2iTKLwDwQ1u293JY2fF7HeP_K2C99buFl3Hhg5anAcdcpyptFuitBInABiAA2mlH7ZSh7co; thor=05C536CD5C31394B06BD50C67200B44DC133A4AF080FE8D4CEBDE42EBC08513BB4B389C3C43703E09060A75CACE0BCC871BA2CF7D67C3320EAD3375865DB957CA6154D4985751074137FD711BEF833279FFECFA5DC45D9BE1C0B2D2E272EFBD0A0BC61C96F24011D7A734437C77604ECBE548D5634E678157186CA6BAD0653741F903DC185BE84472101CEF9F7D6AEABFC8BC862E28C8E7360A344ADF9137C62; pinId=jT8qCij4PBQ7hxldgnonIP5jU0RSLnkU; pin=jd_Fa9XQOpktFRLESz; unick=jd_Fa9XQOpktFRLESz; _tp=NI4dRTlZQN6VJk6dGTjvIdyJObrKHmkpAPPJQD5qyIw%3D; _pst=jd_Fa9XQOpktFRLESz; upn=4cFy4Mhb44xC4sVN4X3Y4chB; pin=jd_Fa9XQOpktFRLESz; wskey=AAJiicA8AFCrrXT0uvmQaWf4LdHpWvKoq8nszucBbZf6QFsUqFLc6iRD2nXH0IJo9H4ZQvhpymzAE4MCFX3RWYm_09EZrudO7jej5avhbkGtfraqdUMimQ;'
    # order_id = '249369700077'

    # AP2022070513154880285910
    # ck = 'TrackID=1F1llOGwgghGeigfWTasJxDSVmYfU9tvri4dNtViCDK9BB2fs22onepmVAhiSG2RluS26-rY_vmkgFUOeiM3ylPVdEgB21BgRsWM3nyxSLpQ; thor=35B82BBB4F52E1E361047E87695AAE1928B442A72B2CE2CC31BA3AB9261441FAB60EDBCA18C707C05D2A3069B63F22BA9BC19818BDDA16D0164946CBC7A7C4B6905493B852C0DDC44FAC57774A9A7FFE5E12A6DDB4FD6B735C89D919615863EE251E6B249E4FDC6EA2B303C37267E599B29B2C2370EAFDBD3246AF6F1121D07C1EFE2C89A0918B3B6D6077595B78154F3A7EA325D3303530AB5E758112BDDFE7; pinId=AM_t6EQkCX8PMA9I1cCvwg; pin=jd_IzxYOqjAcOuc; unick=jd_IzxYOqjAcOuc; _tp=uonfPGieTG4WuIpA0R5mNA%3D%3D; _pst=jd_IzxYOqjAcOuc; upn=7XdO4cpF4chB; pin=jd_IzxYOqjAcOuc; wskey=AAJihh4rAEDqQ8pPogiDNV6o5OoTJuM2mJKQh-l5492YlzeH0mFF_I0NrXsEN_PBCazdEOhm4wQ_DJRMFXf_456gNqlFjzGx;'
    # order_id = '249370412269'

    # AP2022070513072259156910
    # ck = 'TrackID=13h_pWSwDKcrD9yttfQInV0ejxza6_88bzAvSqFxnrxajF6jxrXweJjVHIogX1TFjVN-WgqXcestfrgYS7hSLJJyN-PMBLO1eN6rphmckmlE; thor=915E2EF7AF97088A8D4456A8508416E4128A43309700968326B73646B8694EA1954D15122E70518FBBF86943BF93D5DB7F497F2C9706FCF3C836373515B22D8FF2E7072525D14AAC61DFB3B1A757979646D53C240F054E072021ACE9B8223208011278D46D978D8539A867C75BC2839B2CFE186D260D37A7CF5265D56A1770B2E0621A5AF16DCC8EE144AC3804E4004C625FADF3986984727BF4919DDE0B4101; pinId=tMJ0q90LZ5LHQAQSI6m8guRhm7Bpus9V; pin=jd_K1TPyd9DHrJrv5K; unick=jd_K1TPyd9DHrJrv5K; _tp=%2FfqDKK%2BlZl3zGcr9WvpT42JFBmEthNAnUoFCsuDKHSQ%3D; _pst=jd_K1TPyd9DHrJrv5K; upn=4cFy4Mhb44xC4sVN4X3Y4chB; pin=jd_K1TPyd9DHrJrv5K; wskey=AAJiaiPnAFAgVNmLQVSyaCXBaPouIkUXgo_zctsM5X7tTvww540A0W65AdB_z260hvA-RJcpawbhEt1Dz1zlL5MyS-fJ1210-k35U7X1QlpCiO0Dv_ZZFQ;'
    # order_id = '249426379392'

    # AP2022070513085678188910
    # ck = 'TrackID=1D2XQPTVWZUOb1CaBu8ef3bQLAKFxk2jGZzSsPylhidSlKqQHqHlo0M8_cCmdaLMBVTSP-wZH4bq3LfXHv8W9y10C9NmbhAYHh_VtWKkQ4pU; thor=EB8415D9D58A308B4FBD813F36C97470D81158D9C980A30637584EB0048C1DE03EC1177BEBEDB0826C44BE05977895CD947B66E52D5F7EE5EFF4B9117D5E91DA01CDC133384D3D4F2969A095A81A9EA5F9477F7190313C47E741E284E4E12AF0CAD18FD69EF77D55629B92C3F11E2360C485A5FD4587DD49EF7D2CCB055ACDF6BDA50FCE2EF33C51D088AFDCDBBC5244AD8C88708BFAEB005CC44E1DA209264D; pinId=TgXnvTayNHjLfusoQfiymQlspRFb5_cn; pin=jd_ew6rJDoCsPy0Vol; unick=jd_ew6rJDoCsPy0Vol; _tp=7BT5L7lmNwxJzECcfUILnKnV8kurpNke6vaOzUm8%2Bcs%3D; _pst=jd_ew6rJDoCsPy0Vol; upn=4sJ{4X3Y44xC4MhK7[dn4cNi4chB; pin=jd_ew6rJDoCsPy0Vol; wskey=AAJie0EBAFBxtlQyw95_pliahvSUl3vsBKpF5zW8KFbibxMGKsortB1uyf12yrm82kNSAI-BwP4d0wH7QoxDggtQIN3h4Yo70l0rU5TsNmD8lfAzxCM8tg;'
    # order_id = '249439832584'

    # AP2022070513100869889910
    # ck = 'TrackID=1nqNsaBaHp5EPawuMnOxwDYM5-PumHl3dJY1D_8Lvqx_SHzbfXh-5FchqD2o3jbx2uDE-Erg9DLWsrnVuwgofVqUILpCLiYvnXMgxYO4hD6A; thor=84DA246B343BF74CEF9C271586346A1765B2106DC6E5CDCBD772620953B036933A90EC169F2C1AC5268AAF6204AD5A678BB2B618EB345BF4A10F02532927944549EEFBD4925112A92CBB48D16DF7FBBB42EEA48DF1EB7DA08F0BA10C9A7AC952E5FFFE44FE9120D1929A373A8B0C9F61A9145B11410F438111C08A71BB9020C627C84502C05FC7470F328C3D163F808DCD22F0950D7BC4F45115D6BC119DCF0F; pinId=qEy61nd8J-RDKlLOPGIadXwT7rYiIR98; pin=jd_Slgv05BcSgHaRzX; unick=jd_Slgv05BcSgHaRzX; _tp=%2BJj%2ByhNfSGppuhyM1AQ47TkvQgk8eR%2Bmm%2BbrPfb%2FEH4%3D; _pst=jd_Slgv05BcSgHaRzX; upn=4[tc4cde44xC4nhP7XN84chB; pin=jd_Slgv05BcSgHaRzX; wskey=AAJiivZoAFDDdLreu3XVc0Hl4RLTWx3KTj8kp3vuzvBa6hJEQhu0w6nwbM1kEXENx2vPPTajz3i7MvfxIW7iDI95qMWDAjyXX_m9oiMCQgDAaOwzalekiA;'
    # order_id = '249438532901'

    # query_order_appstore(ck, '', order_id, '200')

    ck = 'TrackID=1Ch_o_eufm6-bZTFDZ4khNEA9ApRXKlXcST2TgyELeokJydjhqGRL9ehGASaV9nMBQRZ7rbA-0TbntTq7bac8cd9KUjE2qQIooadsECstsb8; thor=9E1A6B5B6B6CA1199FBBF462F08309C108AF0F96C74BB176C449248654AB6BC8633B9ABD4BFD8FD4520E037F7A6D7D5125808AA353FFC957564EB0D0018330D98B668A0D89AF3C6A2899952FAD7F0BF4B2AE83C6B4AB1F8E3B6A8C0CF90D0BA2A2D583DFECED97D56EA8E388F58E5A1CC9814253FBC47C7E2318020C41F930183BD84D9CDD95019E403BAF819E9C9C8A9392EFBA0A2FD78B98C9CF79BB8F7437; pinId=J01ORfU3pBtko7LQ3AFxXw; pin=jd_vJhWaUvUzDis; unick=jd_vJhWaUvUzDis; _tp=1qkT7wBJsXSken1vSZ1qBg%3D%3D; _pst=jd_vJhWaUvUzDis; upn=4[tc4cde44xC4nhP7XN84chB; pin=jd_vJhWaUvUzDis; wskey=AAJi1q7jAEAeZQYwnry859vA0FT-GcEce7csDvlu4-DBZW_hJd8OjQ8LcURTJK_BPVrc7Q4B7sUxV_Yb3To2XiMtYzSEK2jJ;'
    print(get_real_url(ck, '249876538278#200', 'ios', ''))
    # order_appstore(ck, '', '200')
    # order_qb(ck, '', '100', '')
    # order_no = '249418749004'
    # print(query_order_qb(ck, '', order_no, '100'))
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