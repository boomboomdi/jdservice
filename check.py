
all_file = open('/home/police/project/pay_data/appstore_ck/ck50')
all_cks = all_file.readlines()

for ck in all_cks:
    ck = ck.replace('\n', '')