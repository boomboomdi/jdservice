import time
import sys
sys.path.append("..") 
from jd_yk import check_ck


if __name__ == '__main__':
    oldck_f = open('newck', encoding='utf-8')
    newck_f = open('useck', 'w', encoding='utf-8')
    # print(address_f.readlines())
    for line in oldck_f.readlines():

        phone = '133' + str(int(time.time()))[0:8]
        card_id = '100011320003' + str(int(time.time()))[0:7]
        ck = line.replace('\n', '')
        if check_ck(ck, '', '105', card_id, phone):
            newck_f.write(ck + '\n')
    print('finish')
    time.sleep(1)