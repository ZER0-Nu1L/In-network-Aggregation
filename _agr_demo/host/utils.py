from scapy.all import get_if_list
import logging

def setHandler(logger, logDir):
    logger.setLevel(level = logging.INFO)
    handler = logging.FileHandler(logDir)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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
    scale_factor = 100000000
    res = []
    for num in num_list:
        res.append(int(num * scale_factor))
    return res


def int_to_float(num_list):
    scale_factor = 100000000.0
    res = []
    for num in num_list:
        res.append(float(num / scale_factor))
    return res