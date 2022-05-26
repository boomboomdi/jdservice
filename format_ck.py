
ck_f = open('ck')
cks = ck_f.read()
for ck in cks.split('\n'):
    for item in ck.split(';'):
        if 'pt_pin' in item:
            format_ck = item.strip().split('=')[1] + '====' + ck
            print(format_ck)
            continue
