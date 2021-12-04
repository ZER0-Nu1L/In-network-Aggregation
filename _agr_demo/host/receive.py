#!/usr/bin/env python3
import sys
import os
import time
import logging

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import Ether, IP, Raw, ICMP
from scapy.layers.inet import _IPOption_HDR
from atp_header import ATP, ATPData
from utils import *
from config import *

logger = logging.getLogger(__name__)
workdir = os.getcwd()
logDir = os.path.join(workdir, RECEIVER_LOG)
setHandler(logger, logDir)


def handle_pkt(pkt):
    if (ICMP not in pkt) and ((ATP in pkt) or (IP in pkt)) : #  (ICMP not in pkt) and 
        # print("got a packet:")
        # pkt.show()
        # hexdump(pkt)
        logger.info('[rec]aggIndex: ' + str(pkt[ATP].aggIndex))  # DEBUG:
        # print("len(pkt) = ", len(pkt))
        sys.stdout.flush()

def main():
    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print(("sniffing on %s" % iface))
    sys.stdout.flush()

    count = PKTNUM * PS_RECEIVE_FLOW * ALLOW_LOSS_RATE # DEBUG:
    pkt_len = len(Ether()/IP()/ATP()/ATPData()) * 8
    logger.info('[rec]Expect receiver ' + str(count) + 'pkt')

    time_start = time.time()
    packets = sniff(iface = iface, prn = lambda x: handle_pkt(x), count = count) # 
    time_end = time.time()
    totalTime = time_end - time_start

    logger.info('[rec]Time cost: ' + str(totalTime) + 's')  
    logger.info("[rec]Receive %d packets" % len(packets))
    logger.info('[rec]Throughout: ' + str(pkt_len*len(packets)/totalTime) + 'bps')
    

if __name__ == '__main__':
    main()
