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
from atp_header import ATP

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

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
    print(("sending on interface {} to value {}".format(iface, str(value))))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt / IP(dst=addr, proto=0x12) / ATP(value=value, aggregationDegree=degree) # NOTE: 

    pkt.show() # NOTE: .show2() 不能展示新协议？
#    hexdump(pkt)
#    print "len(pkt) = ", len(pkt)
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
