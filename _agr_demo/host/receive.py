#!/usr/bin/env python3
import sys
import struct
import os

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw, ICMP
from scapy.layers.inet import _IPOption_HDR
from atp_header import ATP
from utils import *

def handle_pkt(pkt):
    if ((ATP in pkt) or (IP in pkt)) : # (ICMP not in ATP) and 
        print("got a packet:")
        pkt.show()
        # hexdump(pkt)
        print("len(pkt) = ", len(pkt))
        sys.stdout.flush()

def main():
    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print(("sniffing on %s" % iface))
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
