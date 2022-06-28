
from urllib.parse import unquote

total = open('/home/police/project/pay_data/jdck/2')
f = open('true_ck', encoding='utf-8')
true_list = f.readlines()
# print(len(true_list))
total_list = total.readlines()
# print(len(total_list))
# index = 0
# for n in total_list:
    # flag = False
    # for i in true_list:
        # pin = unquote(i.split(';')[0].split('=')[1])
        # print(pin)
        # if pin in n:
            # flag = True
    # if flag == False:
        # index += 1
        # print(n.replace('\n', ''))
# print(index)
# 
for i in true_list:
    pin = unquote(i.split(';')[0].split('=')[1])
    print(pin)