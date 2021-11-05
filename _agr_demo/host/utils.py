from scapy.all import get_if_list


def get_if():
    '''
    get ethernet interface
    '''
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

def float_to_int(num_list):
    scale_factor = 1000000
    res = []
    for num in num_list:
        res.append(int(num * scale_factor))
    return res


def int_to_float(num_list):
    scale_factor = 1000000.0 # FIXME: 和 data 大小有关 16位整数(2**16)/浮点数，5+1位？
    res = []
    for num in num_list:
        res.append(float(num / scale_factor))
    return res