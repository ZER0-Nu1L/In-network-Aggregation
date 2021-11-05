#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import argparse

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from atp_header import ATP, ATPData
from utils import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    parser.add_argument('--degree', type=int)
    parser.add_argument('--value', type=int)
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    value = args.value
    degree = args.degree
    
    iface = get_if()
    
    print(args)
    print(("sending on interface {} with value: {} degree: {}".format(iface, str(value), str(degree))))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff') # TODO: 
    pkt = pkt / IP(dst=addr, proto=0x12) / ATP(aggregationDegree=degree)
    pkt = pkt / ATPData(
        d00 = 1, d01 = 1, d02 = 1, d03 = 1, d04 = 1, d05 = 1, d06 = 1, d07 = 1, d08 = 1, d09 =1,
        d10 = 1, d11 = 1, d12 = 1, d13 = 1, d14 = 1, d15 = 1, d16 = 1, d17 = 1, d18 = 1, d19 =1,
        d20 = 1, d21 = 1, d22 = 1, d23 = 1, d24 = 1, d25 = 1, d26 = 1, d27 = 1, d28 = 1, d29 =1,
        d30 = 1,
    )

    pkt.show()      # .show2() 不能展示新协议？
    hexdump(pkt)    # 以经典的hexdump格式(十六进制)输出数据包.
    print("len(pkt) = ", len(pkt))
    
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
