import base64
import json
import requests
from time import sleep, time
from urllib.parse import quote
import tools
from jingdong import LOG, jd
from ip_sqlite import ip_sql
from jingdong import get_ios_wx
from order_sqlite import order_sql
from tools import LOG_D
from jingdong import jd
from tools import xor

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
                        return SUCCESS, True, line.replace('<inputtype="hidden"id="hideKey"value="', '').replace("\"name='hideKey'>", '')
                return SUCCESS, None
            elif res.status_code == 302:
                if 'orderId' in res.headers['Location']:
                    return SUCCESS, False, res.headers['Location']
            return CK_UNVALUE, None, None
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None, None
        # ==========================
        # try:
            # res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            # print(res.text)
            # if res.status_code == 302:
                # if 'orderId' in res.headers['Location']:
                    # return SUCCESS, res.headers['Location']
            # return CK_UNVALUE, None
        # except Exception as e:
            # tools.LOG_D(e)
            # return NETWOTK_ERROR, None



    def create_order(self, hotkey, skuid, phone, amount):
        url = 'https://chongzhi.jd.com/order/order_createOrder.action?mobile=' + phone + \
            '&messageId=&skuId=' + skuid + '&hideKey=' + hotkey + '&payType=0&paymentPassword=' + \
            '&usedJingdouNum=0&couponIds=&checkMessage=true&messageCode=&entry=4&onlinePay=' + amount
        head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
            'Referer': 'https://chongzhi.jd.com/iframe_fast.action',
            'Cookie': self.ck
        }
        try:
            res = requests.get(url, headers=head, proxies=self.proxy, allow_redirects=False)
            if '销售火爆' in res.text:
                LOG_D('销售火爆')
                return CK_UNVALUE, None
            if res.status_code == 302:
                if 'orderId' in res.headers['Location']:
                    return SUCCESS, res.headers['Location']
            return CK_UNVALUE, None
        except Exception as e:
            tools.LOG_D(e)
            return NETWOTK_ERROR, None


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





def upload_order_result(order_me, order_no, img_url, amount, ck_status, phone):
    url = 'http://127.0.0.1:9393/api/preparenotify/notifyjdurl0069'
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
        'account': phone,
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
    print(res.text)



def create_order(ck, amount, phone, proxy):
    pc_client = pc_jd(ck)    
    code, area = pc_client.search_phone(phone)
    if code != SUCCESS:
        return code, None, None
    code, skuid = pc_client.search_skuid(area, amount)
    if code != SUCCESS:
        return code, None, None
    code, need_create, hitkey = pc_client.order_confirm(skuid, phone)
    if code != SUCCESS:
        return code, None, None
    if need_create:
        code, cashier_url = pc_client.create_order(hitkey, skuid, phone, amount)
    else:
        cashier_url = hitkey
    # ===================
    # code, cashier_url = pc_client.order_confirm(skuid, phone)

    if code != SUCCESS:
        return code, None, None
    for i in cashier_url.split('?')[1].split('&'):
        if 'orderId' in i:
            order_no = i.split('=')[1]
    if code != SUCCESS:
        return code, None, None
    code, cashier_url = pc_client.cashier_index(cashier_url)
    if code != SUCCESS:
        return code, None, None
    code, pay_sign, page_id, channel_sign = pc_client.get_pay_channel_qq(cashier_url)
    print(pay_sign, page_id, channel_sign)
    if code != SUCCESS:
        return code, None, None

    for i in range(2):
        # code, weixin_page_url = pc_client.weixin_confirm(order_no, pay_sign, amount, page_id, channel_sign)
        code, weixin_page_url = pc_client.weixin_new(order_no, pay_sign, amount, page_id, channel_sign)
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
    tools.LOG_D(img_url)
    if code != SUCCESS:
        return code, None, None
    return code, order_no, img_url



def order(ck, order_me, amount, phone):
    for i in ck.split(';'):
        if 'upn=' in i:
            area = i.split('=')[1].replace(' ', '')
    area = xor(area)
    area = str(base64.b64decode(bytes(area, encoding='utf-8')), encoding='utf-8')
    tools.LOG_D(area)
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('account: ' + account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(3):
        code, order_no, img_url = create_order(ck, amount, phone, proxy)
        if code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            ck_status = '0'
            break
        elif code == SUCCESS:
            break
        elif code == RET_CODE_ERROR:
            pass
        i += 1
    tools.LOG_D(img_url)
    # order_no = str(int(time()))
    # img_url = 'https://pcashier.jd.com/image/virtualH5Pay?sign=77a008cf61301d9cbb9651771b952797f4245a8c9c698fabf6fc7b04857f5739bd950ccd2100377230016f15f941f7b10d18f8356738e997b2407dd18021474472285eb678746a57ab75c07ce71f6f46'
    # ck_status = '1'
    upload_order_result(order_me, order_no, img_url, amount, ck_status, phone)


def get_real_url(ck, pay_info, proxy):
    jd_client = jd(ck, proxy)
    code, token = jd_client.gen_token(pay_info)
    if code != SUCCESS:
        return code, None
    token_url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + token
    return SUCCESS, token_url


def real_url(ck, pay_info):
    for i in ck.split(';'):
        if 'upn=' in i:
            area = i.split('=')[1].replace(' ', '')
    area = xor(area)
    area = str(base64.b64decode(bytes(area, encoding='utf-8')), encoding='utf-8')
    tools.LOG_D(area)
    result = {
        'code': '-1',
        'data': '',
        'msg': ''
    }
    account = tools.get_jd_account(ck)
    proxy = None
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        code, pay_url = get_real_url(ck, pay_info, proxy)
        if code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['msg'] = 'ck unvalue'
            break
        elif code == SUCCESS:
            result['code'] = '1'
            result['data'] = pay_url
            result['msg'] = 'success'
            return json.dumps(result)
        i += 1
    # pay_url = 'weixin://app/wxe75a2e68877315fb/pay/?nonceStr=7c250678f61f49092fa0d4040e5e54e9&package=Sign%253DWXPay&partnerId=1238342201&prepayId=wx1321152505977680ae181c2f694ddd0000&timeStamp=1655126125&sign=872D48225CD35C74783548967B23710D&signType=MD5'
    # result['code'] = '0'
    # result['data'] = pay_url
    # result['msg'] = 'success'
    return json.dumps(result)


def upload_callback_result(result):
    url = 'http://127.0.0.1:9393/api/ordernotify/notifyorderstatus0069'
    head = {
        'content-type': 'application/json'
    }
    tools.LOG_D(result)
    try:
        res = requests.post(url, headers=head, data=result).json()
    except Exception as e:
        LOG_D(e)
        return False
    tools.LOG_D(str(result) + '\nret:' + json.dumps(res))
    if res['code'] == 0:
        return True
    else:
        return False



def query_order(ck, order_me, order_no, amount):
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
        'amount': amount
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
        jd_client = jd(ck, proxy)
        code, order_status, status_name = jd_client.query_pczorder_detail(order_no)
        if code == SUCCESS:
            if order_status == True:
                result['pay_status'] = '1'
                result = json.dumps(result)
                upload_callback_result(result)
                return
            else:
                result['pay_status'] = '0'
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


def query_order_im(ck, order_me, order_no, amount):
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
        'amount': amount
    }
    account = tools.get_jd_account(ck)
    tools.LOG_D(account)
    proxy = ip_sql().search_ip(account)
    tools.LOG_D(proxy)
    if proxy == None:
        area, proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().delete_ip(account)
        ip_sql().insert_ip(account, proxy)
    for i in range(3):
        jd_client = jd(ck, proxy)
        code, order_status, status_name = jd_client.query_pczorder_detail(order_no)
        if code == SUCCESS:
            if order_status == True:
                result['pay_status'] = '1'
                result = json.dumps(result)
                return result
        elif code == NETWOTK_ERROR:
            area, proxy = tools.getip_uncheck(area)
            if proxy == None:
                return json.dumps(result)
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            result['ck_status'] = '0'
            result = json.dumps(result)
            return result
        i += 1
    result = json.dumps(result)
    return result




if __name__=='__main__':
    # ck = 'pin=jd_4762c256ebfb3; wskey=AAJirtIfAECnCMjp7CTiPQshmrP2UiC94vV5VyRtUwUpOL_UvcsqTndgxWOT6SPCBw7-4kQYO6afK1o-EaYZQjx0_UyWY--b; pt_pin=jd_4762c256ebfb3; pt_key=app_openAAJirtIhADBtQsn-DLBo4zGKN0wOybtlj3sTru_4TbadxTZ5-e4jm70kMHjy296dpcPCv8LYbuo; unionwsws={"devicefinger":"eidAfc8a81224fsdWDeGZL7MTPGy+HpabTvTJlg3h+Y5sRl5irLtPixQKHjrBx04byjzK3VVOKfHecRIRtNs+VnBefcCkgD+p5mm8TgnO6u6C1s1gJQ5","jmafinger":"ix1aQXJ9OVWAlDm4MK5fEaosw-0X9PaOVqFe7s5U9XmsNHcSq3x2km9xi5R5mWdQM"}; DeviceSeq=5b45a2110d66443ea72f21d7efd3bd6a; TrackID=1OeXiGRLINsXryWK0NN9p6m-mG4YPuqU_oVm8hrtTr4yMhR1nMSNzfoXg1VLi-wfJGaod-QKWjqgHCYRlKEYYrI9sBwINj4mfQQno15yBkvM; thor=19850E4E8343798D4937C5D34955475980B0E79041E3C29C63BE896841E522A37BFF31FCB6064839424BEFF2613039B4EE1769F95674D799FD8B325F95EDA495C91201C68DAEB8E7FC517EF03C136649BFD918E3AC903EAFF8801E94EEA282DC5ED0F3B9623B3BDE263621A07A994BF8B1D8F39BEDC57D01B361393067B009EFC7DF1D331CF9AEC61230E1F929C06952E01ADF22CD7CAD7310E55869BCDF483B; pinId=vnctP4qicjRFItTY9RAg07V9-x-f3wj7; unick=jd_159752iwz; ceshi3.com=000; _tp=zYlkriRADD1%2FCvkf%2BcaAjvvNrBL6EIlmxlgrxuaxKII%3D; logining=1; _pst=jd_4762c256ebfb3; guid=811be59c61e44ba6a89934c9c19db814c8067da9cb74a0e87d3d88638f9fa5d7; pwdt_id=jd_4762c256ebfb3; sid=532c32066fb5e8c63056a1aacd4da71w'
    # ck = 'mp=jd_4762c256ebfb3;  TrackID=1UuHHF3GXVCjjXY6BlYcZnNctLg1BSOiy8EEAl26SulGwR0K9uOj1mMRxffsXa8_hXMJ-jP-m_f7GkDWMjUF2nvfrhRx48OAvEO5mKMBhtcsfXmgr0qBLQFqY6D6PbmefN3r-YYSQHA9fx0tfqWz8RA;  thor=19850E4E8343798D4937C5D34955475980B0E79041E3C29C63BE896841E522A3916C042B0E057B13F055028B506A4EDAABD2DB34706B6644CFC81D97F76F27751E8A5D1ADED9034BBBE3E11B633C70336EC2F96A3BBD1EE0AD715491CFD556A58BC43369E80DD135F382E59B21D28142CF1E6824FEF51C00071F6363A71BB00139A949A33569A7C2BE154DD67155BF6577C22CE3E4602981EBB79E86DB23A524;  pinId=vnctP4qicjRFItTY9RAg07V9-x-f3wj7;  pin=jd_4762c256ebfb3;  unick=jd_159752iwz;  _tp=zYlkriRADD1%2FCvkf%2BcaAjvvNrBL6EIlmxlgrxuaxKII%3D;  _pst=jd_4762c256ebfb3;'
    # ck = '__jdv=76161171|direct|-|none|-|1655627848479; __jdu=16556278484711553437989; areaId=21; ipLoc-djd=21-1827-0-0; shshshfp=75eab5f243e0e0369fab1aa388e3811f; shshshfpa=a59ce402-8a14-a9c6-ac6c-0111f28bd2da-1655627855; TrackID=1NgSXK7lVG681iwDTjEFVJ43-E8HdRuPDMl3HQDw4P9B1bNgOnViePKcTFVNjs7krIF4C31EImN8mn8fwVo4lp21ZLNMO6RSaZ4kIeVgGi8l8aw650t0cOsUYBTQ9qM-jyx7HurF8PWkK6OlN4pXWbQ; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A74540BB9EC1C38C8C3974BA639A2B659EB52FB959BBBCDDA26375EB90F65D445A18C90E5B054C2730D64B078D49DB0F63487896C0217815BC0AC20895D273A1CC294AA94CAA143CFDFE363F0471B3C35F9CD41977274505A1D162D4A39736FE0405742E15C651339CD406ACA2A7941FA1DC89CCE4B14FA5F6EF3B96FC48FB597445; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d%2BSKBX0iW%2BQy5xFBy0C7MU1%2BoxmN9c%3D; _pst=jd_4d9b500034155; __jda=76161171.16556278484711553437989.1655627848.1655627848.1655627848.1; __jdb=76161171.4.16556278484711553437989|1.1655627848; __jdc=76161171; shshshsID=f57428a150a5f108156d4aeb469c3790_2_1655627875192; shshshfpb=p-wQtVi-LWL6GSAfesoLmrw; 3AB9D23F7A4B3C9B=QNCWC64QP4P2LVZKSMOYVQ5UVCXBVUAFAP3XXO4Q2JGY5MVLJ5CNJO5XE3NHQHT2XMBDWWZ24L3C6T75QSANI6DL6E'
    # ck = 'pin=jd_4762c256ebfb3; wskey=AAJiruKKAEBQCGistMVzX3Y32T_lWzDURSCFEDxjV-n21XY4TSgZlyeDDNzQQi3agepbi0yjnYFv9REJJ9EVlSiOxIrfBHTG; pt_pin=jd_4762c256ebfb3; pt_key=app_openAAJiruKNADDshSnkT-105J6ClurQXI3j8tV-5JrzMo-Eq2hlqurNV8-U043V-_ty9bfMqeH2kew; unionwsws={"devicefinger":"eidAe728812240sayNynC401T7Oc9xGXjfTj0sjcqI0IWkAExS27cCv2WlyXRiSGGHq/2Xht9TiklcNBqHHCoGewnD4ZLIenz0YWVG9kplqv/+TNgYV1","jmafinger":"e-2HqFR0kmiCP22UnESJ99dqD0udbXM4xjrRIv16VbzcrobdXqIeIoVRgipPMcV87"}; DeviceSeq=b9d82ffc828e4ebcb52799a3e531b39e; TrackID=1Qw5XwO__PAXY1rFrw95IuYdD6fxdTbuWUrxF-d_Zj7ShaWzBWGxSkKSZwzp-RMzC0MTy3Xl0IZCgxwxYOon02tcURYDygjnXq_EyAHNo4Y4; thor=19850E4E8343798D4937C5D34955475980B0E79041E3C29C63BE896841E522A3FE6F5528F8FC24E2902380115EBFD753713D6E70B879ADFE7C0C91D7584B515173BA1762353E5191CBC86272976933557C3334C942DE8FF3C5D576D1D89F155FDC5C12DD674D215DA50F835107F2C9C18A92A0A78EF2AEBE985E7AAC44C721BF77FB8656B42457442B3E7BBCB5102384B89293A8EC15BCF5E8847835A920567D; pinId=vnctP4qicjRFItTY9RAg07V9-x-f3wj7; unick=jd_159752iwz; ceshi3.com=000; _tp=zYlkriRADD1%2FCvkf%2BcaAjvvNrBL6EIlmxlgrxuaxKII%3D; logining=1; _pst=jd_4762c256ebfb3; guid=8e3be2586f13604e2069377dc396848f68b93834d05b52108a43c4bb75eddade; pwdt_id=jd_4762c256ebfb3; sid=5e57c84c006796ee8630d373e6ef146w'
    # ck = 'mp=jd_7c4f910ec9c4a;  TrackID=1OUw5SgXcdeLq8rTzepNeF-GCipCtKbQQQKFhUHiSRm9ieuWlTIwaySVgWI6PiQTWT3wFDbGmfIfzeMdVnCeSl9GNZxnqGXlDob8wnQx9sfTKx37K4mTo8Ewl_-DA_LloRP474sdwXcwYEayFheo0xw;  thor=9B879A28E74F96C62CC442143F652B5F1383D3CA6550639B63C601B0E6D4A8B82CA808F0B242B46E2B1DFB3286F05488A1D03C84FA8A76A0CA57CABEE36D22A22DCC98058B81A7C6FD7DF32306CC853C1E7E14E2DBD7B4F586A00B9871F909D249F66EE254B5E08235D9DFC0B2653271294D0B348E2C4A97E6DE30B8B73C12FFB34B32EC0D0C400B340D3725E249E54A0E64A4E488223B0DA4C99DFCB730AA27;  pinId=ligEvkIMBthcQmeAslFuHLV9-x-f3wj7;  pin=jd_7c4f910ec9c4a;  unick=jd_159192tjj;  _tp=8lor4nyHaToV6EjiOzKojBiKrSW6izgdRzhfcyUNymo%3D;  _pst=jd_7c4f910ec9c4a; pin=jd_7c4f910ec9c4a; wskey=AAJir13SAEAd_EhOUHKFth1RWZo-JB1IwyWxsOj0_3Pwlr8TCeAn-QVAjik7Xli12lVXq_EcMSIXtRPEhsnuAFAE1j9O4Lxt; pt_pin=jd_7c4f910ec9c4a; pt_key=AAJir13TADBQQB7AWI6ap6FHKEASGgeEIpHuYhqiekUvpjBNqn7AdBD3fp8wCKa5SJA19O9OpN0; unionwsws={"devicefinger":"eidAefe381224bsbuBrLWXj/TjqFNqzh3+5JOrgazNr2BdDoQlEdpug3ta04EZAk1v9pr2lFGAi/E+3T4E6X5aZiV/OfzVVZdkHicCg9mjRoaAnk5gIy","jmafinger":"twVWf9_3A2tCZBfDjchBjboAiOJ9KdiDcvi_GJfGJfiTg_UXmfs37M3E925WaNEoP"}'
    ck = 'pin=wdeQtrbjZGkGPg; wskey=AAJir2XlAEAZBXjYbajHQpOJUnOqs0n-J8q2RsLaMB-EIhpYs6iHD82nBHuO6nvO8yaoF9Bpd-tJJq4wQjU23dCmliBxNCBQ; pt_pin=wdeQtrbjZGkGPg; pt_key=AAJir2XmADBFFzaI51BczghnewT_k_5GFQ79BP14J2O0sfEzSWTm0QB2hzZ2OvH2g_JaHgQHs4U; unionwsws={"devicefinger":"eidA2a23812338s8sLuY8U9XQHSqqfKyvrtFprC7mnLMfUueboKfeSqduJp6BZiOZE0+82hT+VAZ0JhutZUgnUfSCK4R/9wflWpH0ezLuGcZepEc5udN","jmafinger":"j7lmEP-9WdiDjdbTPmo5FT300RULMpSa3S9NPOQjMr-LJa4Nbt7Z7hWd5YYteDF_m"}'
    ck = '__jdv=76161171|direct|-|none|-|1655661859509; __jdu=16556618595081329726906; areaId=14; ipLoc-djd=14-1159-0-0; TrackID=1TXiubVDF6F1jU4t2EaqdUo-AeMvhSp-9wYg-e7PDRyt3AormSC98FAccM14-Kq01wI8jOquK5S3R-XfG2_cucKQ3n0i_VID9JleJWs7ANWk; pinId=5cIh1s8V6vnw90f3U2HISA; pin=wdeQtrbjZGkGPg; unick=eQtrbjZGkGPg; ceshi3.com=000; _tp=uec71obJjBj0W24efbJcPg==; _pst=wdeQtrbjZGkGPg; shshshfp=d537d0cbe1a5c489943d585a85c0541e; shshshfpa=b0b2a1cf-b21d-ad0d-dae4-9a21372738bf-1655661882; shshshsID=d0220b1b1ed086f97aa72cfc2ddfafdc_1_1655661883081; shshshfpb=qRNA559s6J4jH3ozhNDUznw; _distM=248950866433; qd_ad=-|-|-|-|0; qd_uid=L4LMDHO5-H19XYKPLMGCOW18QHMNO; qd_fs=1655661946035; qd_ls=1655661946035; qd_ts=1655661946035; qd_sq=1; qd_sid=L4LMDHO5-H19XYKPLMGCOW18QHMNO-1; 3AB9D23F7A4B3C9B=VS4TQP7U2PRQABBKVMCDVQGNXRFTUL5BVL7LOLTXTOOO5XWTEOT2574AILKVNDHNKQZZY7IQFBYJ4XNTHIDE6IFDCU; thor=F16C42E3749CEC96AA34BA6265776EF9D710B48BD23DC0DA17DD091DA2DFA6823ECF0A641040C6D9D9D01EB62E2BC3436D30CDC630E1B58BB641782C9B854D4C4A0D74D5457F6C1C57D710289D403F2106A27C3ED5AD9152ED6FC7C84E8DC1BE38AE893913E4E9CC342E340FE65398D88446E4B30417F5FF53B98EE51414DD15FA17FB42F5E489DDC8EED05F5B3DC08B; __jda=24961467.16556618595081329726906.1655661859.1655661859.1655661859.1; __jdb=24961467.26.16556618595081329726906|1.1655661859; __jdc=24961467; pin=wdeQtrbjZGkGPg; wskey=AAJir2XlAEAZBXjYbajHQpOJUnOqs0n-J8q2RsLaMB-EIhpYs6iHD82nBHuO6nvO8yaoF9Bpd-tJJq4wQjU23dCmliBxNCBQ; pt_pin=wdeQtrbjZGkGPg; pt_key=AAJir2XmADBFFzaI51BczghnewT_k_5GFQ79BP14J2O0sfEzSWTm0QB2hzZ2OvH2g_JaHgQHs4U; unionwsws={"devicefinger":"eidA2a23812338s8sLuY8U9XQHSqqfKyvrtFprC7mnLMfUueboKfeSqduJp6BZiOZE0+82hT+VAZ0JhutZUgnUfSCK4R/9wflWpH0ezLuGcZepEc5udN","jmafinger":"j7lmEP-9WdiDjdbTPmo5FT300RULMpSa3S9NPOQjMr-LJa4Nbt7Z7hWd5YYteDF_m"}'
    # ck = 'mp=wdeQulHIJNTrzK;  TrackID=1XnarqFv11GOkAbZQ79Cj64a5oO99RBzkGuJZnFAnZ4rlzxUkRXNEQwb9XLy-KECvljng8iJhiz5bQ6MEtZb4x3dtNJkX9A6nOaYoLfarTHyqBIcIZHr1hxW-Okkp3p3f;  thor=6607FD97C06EF71C631766633E45DDE9A0BB4F25215510AD81BE5134246999E16C4599D3D7917D205AD4806E9595C29439F6EF1866DEEB92D7E63FC46D385C2DC44B826CE7E18713C7EA5783F3B5546C14E9257EC69B269CDDD7D91D299A79760A4251E453A7EBE7E624688DA99F5DD4851FBA245B29D555360F6DFF0E2AC999A464EA91C24C953C52B6A16CC9760D01;  pinId=1I31wMePdFQNmdIoST1rzw;  pin=wdeQulHIJNTrzK;  unick=eQulHIJNTrzK;  _tp=9zj2lR4AYA5sTUaZZpQxnQ%3D%3D;  _pst=wdeQulHIJNTrzK; pin=wdeQulHIJNTrzK; wskey=AAJir3XDAED7SDXXzSNNkuwOC7I7F75Onzg_yXGp3yGaGtE44rTfuOzX8grUb8jVfbZKntxRpS7NLRfSiGwXSXoOaelgG_wv; pt_pin=wdeQulHIJNTrzK; pt_key=AAJir3XEADBoSwS-tmf9wcbksDRUp9xK0_EE26Oy5L7j8gmx9_vup_4Pi3Xqu-KgR755_1bb928; unionwsws={"devicefinger":"eidAf7f0812253sdFYH3UlaSSRiqGyFhPUMrexWB+NPT9k4Q8ZpEbrbgi+KegIsNUfj/N1hzdE3imqt0Tsah/7AQA0A2xdeukEBHukdYS/rOx4Vcn89J","jmafinger":"rOmrQoBoqkZPrOQtsR3EaIZa6VSPCqP60IK-98Cg4A3iBrv11afaevC21_S-2x8lF"}'
    ck = 'mp=jd_6LawhBrw2Kjv;  TrackID=1fNzYpIaLM2b-3oWcs0eBq-m58IHrlQH_uJVGilQe1F-NqP5w4SS-Y3fqgJaT9L6MR3FkEwPdZsEKg3AYLZwwb5s5vJ-XMt409GW1wCALg1VZSDRBiERVLSztoy4GVjp-;  thor=58E97E257737DAE3FB8938F29CC9192B8B1E09206274CC6D7ABA6700F2688E98D10BB7461C3628A913BE5117552A3C177E9FEBCCE53A957893CA53FA0F4DFEDE18FB4EB7DE13BACE31256F5B1617459F9E4E44623F0CF68C5D6E337EA541FB97B5BD09DFFCE7BD1FB096F79F6BC9BABAEFF797B427D545CF1A3C5C5E3AEB3755389D00B33E4FFB8558F6848139FAAC646515EB7D1A17968C475E007A9CB57B60;  pinId=4TDTg2SmOpUbcryeplPBvg;  pin=jd_6LawhBrw2Kjv;  unick=jd_6LawhBrw2Kjv;  _tp=g%2BWdJH33L9RwEPq2DKYRXQ%3D%3D;  _pst=jd_6LawhBrw2Kjv; pin=jd_6LawhBrw2Kjv; wskey=AAJiCFTGAEB9mJ4AAIu6wX7_ykroTZLWWMo8x5P-tom1NDBBGLrXMRQQPU_Y_ME3AXeG4zGDkEHhINFrZKf2ZKsiTZp_L89A; &%E5%B9%BF%E4%B8%9C%E7%9C%81%E4%BD%9B%E5%B1%B1%E5%B8%82'
    ck = '__jdv=76161171|direct|-|none|-|1655969160798; __jdu=1655969160797563967703; areaId=5; ipLoc-djd=5-142-0-0; PCSYCityID=CN_130000_130100_0; shshshfp=75eab5f243e0e0369fab1aa388e3811f; shshshfpa=0a65a8d7-6984-a676-8f81-cc314dd3beb6-1655969165; TrackID=1oABTUQFhXjmUVyEV6kwoudToN4OPyEnIYFGE-htVX5u-ksINegUVfCpbEqm66ICOhbr_xGXsTnGS9WmWvHPjw5ezN5WiRl_FYMnB09keP_TwLILFiCFqmGbcM_B5f6S5DHcG14KdY3pT1nFyHwB1zw; thor=63C48F15AFBF3EEB9A7FD8F3F7A9BF05D0817F049E308CC94A6938FF9A69A745BD47EA20AFC79055282B406048EC2E8192306DFC9AC8BBF7C06A2977EBB537156D97E6C9C3E0F1A75DFDF627B7304D301546775AEE6B4F27EB2684B23FD1BA951704EA4A373CC81EE17E0C0C5585B4A98B30E9B08570713BC12F6E0F5CEA691BD2097FF16D32E0B4886C9804D292579B8FC2C50B1A826915D6D8519E3DF6CB47; pinId=tA352EW71edd9cU5JurDWrV9-x-f3wj7; pin=jd_4d9b500034155; unick=jd_4d9b500034155; ceshi3.com=201; _tp=VHnhiNi86OlY5d+SKBX0iW+Qy5xFBy0C7MU1+oxmN9c=; _pst=jd_4d9b500034155; shshshsID=17a4b998abd4cec4a52ce59bbf05dedc_2_1655969183899; shshshfpb=asho2E8g2vXZOZfB8NJ1twA; __jda=122270672.1655969160797563967703.1655969161.1655969161.1655969161.1; __jdc=122270672; __jdb=122270672.6.1655969160797563967703|1.1655969161; 3AB9D23F7A4B3C9B=L4VA3H3XRQXTHOSQML6VS3B7QYYN7GVIBS2KPYED4PB7WAMMO52MPHRJZLNNWXPSPTBNDJOKGTPD7SIYJTCJZFPFE4; wskey=AAJiqgJZAECd9g_DDWxJo3YPVOaYWwvDsU_BCxK7nZcTma51_nkgmKL3e4RfmW8vZ0r1bdc0B2FISHUA0CaxqLYzyy02KqUH;'
    ck = 'pin=jd_MJeXCVSpSPmF; wskey=AAJitBh6AEASeRc2oY7eppvWmhxctDlQSd_RlYCOwcPs7opn7B4ui6FtAh6rQZW575-q_P0BahwYNd8hZ_jSYsO_PDw8WHLa; pt_pin=jd_MJeXCVSpSPmF; pt_key=AAJitBh7ADDeKX-SSvh9VYS8eJ61M32C_R-unM3jqtew2toZaJtaUJCj1ZU_KtyrBsbw7BHvH6Q; unionwsws={"devicefinger":"eidA226181226es17hyfyAXdTtCPKdhGTgLX8e4coUmVXPGsnydS4aqLMsbpxVbEpI7Hi1pkNphfVla2Fr0ZO6OPMv+VCaS6kcQhBZq0U5i/rMP2F7JV","jmafinger":"l18B00Se11nCLM2-xy2wjGXMYxOx39op7xk8BKIV6IEUu776DT6vo9YN3lx1o6sbU"}; DeviceSeq=6dcbb0ef393c48fd8680a792b5287744; TrackID=1yYZh8F_fmKitga002yjus0-FNkMqROyPJ35xc5Iqp-BQnW8LObWkZPbutzFxcs7SRVkvrTWfj-UCMLoB9mGxbz76j4zOC3xfsJlKEPT0pu8; thor=6747CECC33807B9DB377AB93EF1BFE5715F809EE2FC887B2D0F4E8F3DD23BEEAF3F7B4E8C62907B87AF723DB86E5B5860B1A29744519B719C8E4164BDD85ED6FEEA0E1ABA851DC454DB568024D1B4DF40D99D1EDED485D6C3AAC0A7BFC123599E3AA80B85FC2ACD9B196452EBE651BD2D2EAB400856F013FA66ED30AF94A26463060FB9061606BD691A1E5D1F0E7C3723195A6F93E60F624A530E90077E884ED; pinId=F2Te-vh7VUE0M6xtTMKo5A; unick=jd_MJeXCVSpSPmF; ceshi3.com=000; _tp=C2B0B8wx7NdjjREbRXWqXQ%3D%3D; logining=1; _pst=jd_MJeXCVSpSPmF'
    ck = 'TrackID=1fwEq5HSXihwQ4z4ER-aWSEgSpFWSshz8k3D4beU8CUhvqNE9-KmpL2mX9vA_h0gVGkFNP7Fk1G0Av3VEjUyPuk7RbdFdiHIg0KjrK9hhyu0; thor=6747CECC33807B9DB377AB93EF1BFE5715F809EE2FC887B2D0F4E8F3DD23BEEAF3CC468519237B61FE6B745DAC6840A616FC418D3F8D15BF6ADB910650CBE841E2ACEA2D2941908F42325B6102712FE06A457B4341C9240246FFF1B1BF73413E285CB8D4EEC08E2D7345D28984218196494B643DCAB07D6BB22D418CB7EBB54F2895F2AE3C9A724C23C95DBA3856499E1D52FE9246816E57B557A333867F83EC; pinId=F2Te-vh7VUE0M6xtTMKo5A; pin=jd_MJeXCVSpSPmF; unick=jd_MJeXCVSpSPmF; _tp=C2B0B8wx7NdjjREbRXWqXQ%3D%3D; _pst=jd_MJeXCVSpSPmF; upn=4cl.4Mhb44xC4cl.4cdd4chB; pin=jd_MJeXCVSpSPmF; wskey=AAJitBh6AEASeRc2oY7eppvWmhxctDlQSd_RlYCOwcPs7opn7B4ui6FtAh6rQZW575-q_P0BahwYNd8hZ_jSYsO_PDw8WHLa;'
    # 'https://chongzhi.jd.com/order/order_confirm.action?&&entry=4&t=1655559214558 '
    ck = 'TrackID=1Ktw9ylhL-GYYcycohQwr0hDpQwhot66CSNYn7Wb7QZAXHFgWxy8MCvnPQGYNkoLBk9n4rxLXZBBvfWzoEOCpVEeJYBjtgGOmFkwVwhmhYIc; thor=357C782282E25E788042CA34F39B7F79EC5E1641533AD09E5AAE486741153722E420E3DAE1C23ED71C5E1AD612539D08C1F7F4494B6EBF8943CFF7B5F0298A4A1E58720052042E2E0538290DF511106A17C86DEDB791B41CCE2E4807D002BDFE3BB34E4DB66E5F94C2E25742EF8CC5294515FA8D85E5BA956C9F74FA918F2A6E7207C80C800D5EB9EEDF1A76143242E21D7A03D072747787EEF45F8926EA63F6; pinId=KklU2_ObtBggWoTyP1TrNdgbjeU3V8yF; pin=jd_lRtPvfOKKtcdt1j; unick=jd_lRtPvfOKKtcdt1j; _tp=RrPbRXfzdeB5pRjfVTqOHcCLYN7yTQlRcmwnOGaw4Eg%3D; _pst=jd_lRtPvfOKKtcdt1j; upn=4slV4X3Y44xC7[V.4sJ[4chB; pin=jd_lRtPvfOKKtcdt1j; wskey=AAJiOwnxAFBk46oa4B4lvZ0m9VKt4u59ACO5TLuT9BfuOenwRg5Y8xZh-K5KH9rMy3If4d-xkcSqqRMyKvDCD9B6MS99IlRFcCOHOqQaQszbH7gI1anO8Q;'
    ck = 'TrackID=1VSACxJpf-zs0Adpo9fUkIAbKAl_2_dBMHItS67Exi7pZj2tug5W-pDtwhWxNtSictwNamQXfSNTJKesA_vxnjCHio8WjkP-1sagT8RaDcEs; thor=B26EE72195F5C5CEB035D4B042A4772A543EFD7DB247B73C8AFDEFBD6A2A31F758A0951C2387D0AC2B4A9AEDC88487C12CF4005785497301A47FDCED5BE540658C4FF3818029C79AA950F2573655AAE4E3D811877560BDD5953BC3054F876825D1994D1315E54C7A880D3B9D8A7E939584DD3416862C3156EBE0338F93B87A71B4DFAC1B855E6A3B76BC83F9F46F9EE1D8B70168BB9F3F529D8E1E1D504BD4D5; pinId=l43DvKUHDM3PAr2WXAPl0AbLH2vz4BO0; pin=jd_NqnnvH1FWlciq7I; unick=jd_NqnnvH1FWlciq7I; _tp=auSfjpWBF5ssGqRpdPMKigp%2F2usEGmSwtmACykuRheY%3D; _pst=jd_NqnnvH1FWlciq7I; upn=4cFy4Mhb44xC4qdm45Vo4chB; pin=jd_NqnnvH1FWlciq7I; wskey=AAJiOwEBAFBD8oXhuwDdAVMfm66Dc8XE-oQxEmQ0MfsafF7JBvoOsP1zYDtwMZef3HW4zVwHowf8juugLhs44aZV2hPXdS5-ILr_Vcn1HgIbmDmWb3ZSuA;'
    ck = 'TrackID=12gRDoBuE3jaO9I_TsAhh9nU2TKLOycmL2lj_X8oKMW4l2s1L07_IbuG0snMRkQLKgwL-OMb9CK1-tKj9ZRa-3P4biPSQnpRWWTaM5gt0wVg; thor=72085FB7AB75A030DEFDDC97D57A4FA311A69F41454663B677FE4ED534CE51971C3B97A59AC5274960441EDD0CC3C2EADDEAEBFF782391492CF67120B217C5B436A2205C5C5C578C6128C1FD0038AD65AF41A5D0DC192D3CED593DA65DADC0F296A3257BF6F8313567E553BBA96D25E2EF3889E7FFDE6CD9812CB60035F3F76EC9C9C9F9E662BDE83F8080331841697B029D012B44D53BC11E8360CB605FEB69; pinId=Pu407A4gV6O7viNkMlNI292hRoc2Q1_2; pin=jd_KgHdl6uXsGmLKFQ; unick=jd_KgHdl6uXsGmLKFQ; _tp=qwSP69GXhjZB1t8IKlVBXVA6IlJBu2UeLYkoJKFY%2B5c%3D; _pst=jd_KgHdl6uXsGmLKFQ; upn=4sV[4sFg44xC7XdS4X3N4chB; pin=jd_KgHdl6uXsGmLKFQ; wskey=AAJiQnQZAFCMs0i8XT8mECnOKoHL_-pKWyJcYY-L3Gm_lIxPsbmw0EQE29IB2HpZ-DuHCBLGuKGdmwLtcysEfMsqXF2AA434R8IoAENQUSXGKTgd8PT4Fw;'
    ck = 'TrackID=13KMrvDI1i4L1dFc5HVx07Ygp9MTf5phYQyzhfUSO8DFqg6qVTjg8hUimyrOC-8ussc3eeK4auCeoxHuNDaEGVH7YjZm9YajFO5-8kdbkoc8; thor=495D3908D399E69A91BA8059153C23CF818023CF74FE803821AF30C79DCFD2037169FDBB4CEA92DD39667B2DDCE443B399F2E143A07CF5E90449A58540AE329CD8964EC1A9C9D5BA423BA43EB5EF6483ADD6049FE3E4379CD14E34BB43E340706EDBC6230FE3CA0FC2A4D51B497542F0E8E6B7E2CBBD0C88D794A7553451C214B17965910AEE5DD2836CBA9E4F6F277CD676834B364ABB40250A7C914F67A154; pinId=scXmZDe0y9KI4PtZaZUfQQ; pin=jd_lsTGiDjeDRuj; unick=jd_lsTGiDjeDRuj; _tp=SRXrR0%2FdN3b5hCtXw4Do6w%3D%3D; _pst=jd_lsTGiDjeDRuj; upn=4sFg7HtQ44xC7M*d4MpS4shw4chB; pin=jd_lsTGiDjeDRuj; wskey=AAJhf8eDAEA1TMIpNtuo_ydZ0y_q2yjLTeE9U0z9GOYU3LK2GjJbBc6wZhq2_bolOceTt2BYspd9fjhHPVG-I7N6BydUTp_e;'
    
    mobile='13784302433'
    amount = '200'
    print(order(ck, '', amount, mobile))
    # query_order_im(ck, '', '249266167651', '100')
    # u = 'https://pcashier.jd.com/image/virtualH5Pay?sign=4137e710e43594ce63978e1b18a7736493f63a1b82878ee5f9c140df36b6d5f4679b159cf57c1a112d9c16fb99c52e61d87bea5c65bd464ed37150286789927572285eb678746a57ab75c07ce71f6f46'
    # print(real_url(ck, u))
    # jd_client = jd(ck)