import base64
import json
import requests
from time import time
from urllib.parse import quote
from jd_yk import getip_uncheck
import tools
from jingdong import LOG, jd
from ip_sqlite import ip_sql
from jingdong import get_ios_wx
from order_sqlite import order_sql

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
        res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
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
            res = requests.get(url, headers=head, proxies=self.proxy)
            # print(res.text)
        except Exception as e:
            tools.LOG_D(e)
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

    def submit_order(self, skuid, win_id):
        url = 'https://card.jd.com/json/order_syncSubmitOrder.action'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': self.ck
        }
        data = 'webFeOrderInfo.buyNum=1&webFeOrderInfo.payRuleInfo=&webFeOrderInfo.cardNewVersion=1' + \
            '&webFeOrderInfo.payMode=0&webFeOrderInfo.moneyBasic=0&webFeOrderInfo.integralBasic=0&' + \
            'webFeOrderInfo.payPwd=&webFeOrderInfo.couponIds=&webFeOrderInfo.dongCouponIds=&webFeOrderInfo.amountPayable=' + amount + '.00' + \
            '&webFeOrderInfo.couponsAmount=&webFeOrderInfo.jbeanAmount=&orderParam.useBean=&orderParam.gameAreaSrv=2&webFeOrderInfo.skuId=' + \
            skuid + '&webFeOrderInfo.categoryId=13759&orderParam.winId=' + win_id + '&orderParam.secondSource=0&webFeOrderInfo.eid='
        print(data)
        try:
            res = requests.post(url, headers=head, data=data, proxies=self.proxy)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        if res.status_code == 200:
            ret_json = res.json()
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
            res = requests.get(url, headers=head, allow_redirects=False, proxies=self.proxy)
            print(res.text)
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None
        ret = res.text.split('(')[1][0:-1]
        ret_json = json.loads(ret)
        print(ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name'])
        if ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name'] == '已完成':
            return SUCCESS, True, ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name']
        else:
            return SUCCESS, False, ret_json['appOrderInfoList'][0]['orderStatus']['statusList'][0]['name']


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
        res = requests.get(url, headers=head, proxies=self.proxy)
        print(res.text)
        if res.status_code == 200:
            for line in res.text.split('\n'):
                if '_orderid' in line:
                    if order_no in line:
                        passkey = line.split('_passkey="')[1].replace('"></a>', '')
                        return passkey

    def get_recycle_passkey(self, order_no):
        url = 'https://order.jd.com/center/recycle.action?d=1'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://order.jd.com/',
            'Cookie': self.ck
        }          
        res = requests.get(url, headers=head, proxies=self.proxy)
        if res.status_code == 200:
            if '忘记密码' in res.text:
                return UNLOGIN, None
            for line in res.text.split('\n'):
                if '_orderid' in line:
                    if order_no in line:
                        passkey = line.split('_passkey="')[1].replace('"></a>', '')
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
        res = requests.get(url, headers=head, proxies=self.proxy)
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
        res = requests.get(url, headers=head, proxies=self.proxy)
        if res.status_code == 200:
            tools.LOG_D(res.text)
            if 'success' in res.text:
                return SUCCESS, True
               
    def clear_order(self, order_no):
        tools.LOG_D(order_no)
        passkey = self.get_passkey(order_no)
        code, status = self.recycle_order(order_no, passkey)
        if code != SUCCESS:
            pass
        if status == True:
            code, passkey = self.get_recycle_passkey(order_no)
            if code != SUCCESS:
                pass
            self.delete_order(order_no, passkey)

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
                    return CK_UNVALUE, False
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
            # print(res.text)
            orders = []
            order = {}
            # for line in res.text.replace(' ', '').replace('\n', '').replace('\t', '').split('等待付款'):
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
                # print(line + '\n\n')
            # for line in res.text.replace(' ', '').replace('\n', '').replace('\t', '').split('<strong>&yen;'):
                # print(line)
                # if 'order-status' not in line:
                    # continue
                # amount = line.split('</strong>')[0][:-3]
                # order['amount'] = amount
                # for line1 in line.split('order-status'):
                    # if line1.startswith('">等待付款'):
                        # for i in line1[0:158].split('?')[1].split('&'):
                            # if 'orderId' in i:
                                # order['order_id'] = i.split('=')[1]
                # orders.append(json.dumps(order))
            # return
            return SUCCESS, orders
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None

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

    def search_phone(self, phone):
        url = 'https://chongzhi.jd.com/json/order/search_searchPhone.action?mobile=' + phone
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://chongzhi.jd.com/iframe_fast.action',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 200:
                if 'area' in res.text:
                    return SUCCESS, res.json()['area']
            return CK_UNVALUE, None
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None

    def search_skuid(self, area, amount):
        url = 'https://chongzhi.jd.com/json/order/search_searchSkuId.action?ISP=1&area=' + area + '&filltype=0&faceValue=' + amount
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://chongzhi.jd.com/iframe_fast.action',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 200:
                if 'skuId' in res.text:
                    return SUCCESS, str(res.json()['skuId'])
            return CK_UNVALUE, None
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None



    def order_confirm(self, skuid, phone):
        url = 'https://chongzhi.jd.com/order/order_confirm.action?skuId=' + skuid + '&mobile=' + phone + '&entry=4&t=' + str(int(time())) + '558'
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://chongzhi.jd.com/iframe_fast.action',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if res.status_code == 200:
                for line in res.text.split('\n'):
                    if 'hideKey' in line:
                        line = line.replace(' ', '')
                        return SUCCESS, line.replace('<inputtype="hidden"id="hideKey"value="', '').replace("\"name='hideKey'>", '')
                return SUCCESS
            return CK_UNVALUE, None
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None
        return SUCCESS, None

    def create_order(self, hotkey, skuid, phone, amount):
        url = 'https://chongzhi.jd.com/order/order_createOrder.action?mobile=' + phone + '&messageId=&skuId=' + skuid + '&hideKey=' + hotkey + '&payType=0&paymentPassword=d41d8cd98f00b204e9800998ecf8427e&usedJingdouNum=0&couponIds=&checkMessage=true&messageCode=&entry=4&onlinePay=100'



if __name__=='__main__':
    ck = '__jdu=16509706855941893098380; __jdv=76161171|direct|-|none|-|1654941522932; areaId=21; shshshfpa=24b6bb36-e2eb-935b-8da5-4244c2284385-1654941526; shshshfpb=zgH442FN956xyfHqjr4f9ag; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d%2BSKBX0iW%2BQy5xFBy0C7MU1%2BoxmN9c%3D; _pst=jd_4d9b500034155; user-key=b713e0dc-ea97-4f4b-8edb-4e1a16076df9; ipLoc-djd=5-142-157-42800.8254666397; ipLocation=%u6cb3%u5317; cn=3; shshshfp=eb4ec6b3c1c9a309c081c326c6532dba; _distM=248887308482; joyya=0.1655561616.21.1nw0995; __jda=122270672.16509706855941893098380.1650970686.1655559185.1655565669.29; __jdc=122270672; __jdb=122270672.8.16509706855941893098380|29.1655565669; wlfstk_smdl=okxzc491ao3txai3gxkt8zgh46pmczd0; TrackID=1bfJwd1LEtgtTvTEKkqk4werPMh9otl9sSx5OuGfNwEMRbyppP5AdmQ3D7lZk3I-Qn5gOKMXgjyTkyhZ2CBVBv7BXnjBzOPsecht6C8fyHNNjkMnVRA13siFn7kyDV6RrzmjFy2I_GZi2diimK-4dZQ; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A74571325B4957AFB5FC95A3B9D7B2AB72BB1E6754F2C9876C5C3E673F399DB60BF609CD3A8DBA8AC3D2CF81C1A6837040C152FB70308403C2CFB7025DF218DBB6E603E0D09A5A84080F6CEC60C707D551FF5D48269E52B958DCBEAE42AFDED48A9CB73269D3E308CE36482AF77C877CD7D965D9004387448886DC434AD0B377B8EB; 3AB9D23F7A4B3C9B=L4VA3H3XRQXTHOSQML6VS3B7QYYN7GVIBS2KPYED4PB7WAMMO52MPHRJZLNNWXPSPTBNDJOKGTPD7SIYJTCJZFPFE4'

    pc_client = pc_jd(ck)    
    'https://chongzhi.jd.com/order/order_confirm.action?&&entry=4&t=1655559214558 '
    mobile='13784302409'
    amount = '100'
    code, area = pc_client.search_phone(mobile)
    code, skuid = pc_client.search_skuid(area, amount)
    code, hitkey = pc_client.order_confirm(skuid, mobile)
    print(hitkey)