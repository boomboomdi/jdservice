import sys
sys.path.append('..')
from pc_jd import *
from pebble import ProcessPool


def order_appstore(ck, order_me, amount):
    for i in ck.split(';'):
        if 'upn=' in i:
            area = i.split('=')[1].replace(' ', '')
    area = xor(area)
    area = str(base64.b64decode(bytes(area, encoding='utf-8')), encoding='utf-8')
    tools.LOG_D(area)
    code = NETWOTK_ERROR
    ck_status = '1'
    account = tools.get_jd_account(ck)
    tools.LOG_D('========================================== create order ======================================== account: ' + str(account))
    proxy = ip_sql().search_ip(account)
    # tools.LOG_D('searchip: ' + str(proxy))
    if proxy == None:
        proxy = tools.getip_uncheck(area)
        if proxy == None:
            return None
        ip_sql().insert_ip(account, proxy)

    for i in range(5):
        code, order_no, img_url = create_order_appstore(ck, order_me, amount, proxy)
        if code == NETWOTK_ERROR:
            proxy = tools.getip_uncheck(area)
            if proxy == None:
                return NETWOTK_ERROR
            ip_sql().update_ip(account, proxy)
        elif code == CK_UNVALUE:
            return False
        elif code == SUCCESS:
            order_sql().insert_order(order_no, amount)
            order_sql().update_order_time(order_no)
            return True
        elif code == RET_CODE_ERROR:
            continue
    return False



if __name__ == '__main__':
    appck_f = open('ck', encoding='utf-8')
    true_ck_f = open('true_ck', 'a', encoding='utf-8')
    # print(address_f.readlines())
    # with ProcessPool(max_workers=10, max_tasks=5) as pool:
    for line in appck_f.readlines():
        print(line)
        line = line.replace('\n', '')
        for i in line.split('----'):
            if 'pin=' in i:
                ck = i
        try:
            status = order_appstore(ck, '', '200')
            if status == True:
                print('================ true ==============')
                print(ck)
                true_ck_f.write(ck + '\n')
        except Exception as e:
            print(e)
            continue
# 
    sleep(3)
    print('finish')
    appck_f.close()