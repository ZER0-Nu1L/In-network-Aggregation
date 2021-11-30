#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import os
import argparse
import time
import logging

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP
from atp_header import ATP, ATPData
from utils import *
from config import *

class DataManager:
    def __init__(self, dst_ip, data):
        self.dst_ip = socket.gethostbyname(dst_ip)
        self.dst_ip = dst_ip
        self.data = float_to_int(data)
    
    def _partition_data(self, worker_id, switch_id, degree): # TODO: worker_id 尚未支持
        '''
        把data以一个payload的大小为单位进行划分
        '''
        packet_list = []
        for i, index in enumerate(range(0, len(self.data), DATANUM)):
            iface = get_if()
            left = index
            right = index+DATANUM if (index+DATANUM <= len(self.data)) else len(self.data)

            args = ["d00", "d01", "d02", "d03", "d04", "d05", "d06", "d07", "d08", "d09", "d10", "d11", "d12", "d13", "d14", "d15", "d16", "d17", "d18", "d19", "d20", "d21", "d22", "d23", "d24", "d25", "d26", "d27", "d28", "d29", "d30", "d31"]
            packet_list.append(
                Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff') /
                IP(dst=self.dst_ip, proto=0x12) /
                ATP(aggregationDegree = degree, aggIndex = i, switchId = switch_id) /  # NOTE: 这里的 aggIndex 暂时比较随意
                ATPData(**dict(zip(args, self.data[left:right])))
                )
        return packet_list

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    workdir = os.getcwd()
    logDir = os.path.join(workdir, AGGRE_MONITOR_LOG)
    setHandler(logger, logDir)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, help="The destination host to use")
    parser.add_argument('--degree', type=int)
    parser.add_argument('--switchId', type=int)
    parser.add_argument('--dataSeq', type=int)
    args = parser.parse_args()

    host = args.host
    degree = args.degree
    switchID = args.switchId
    dataSeq = args.dataSeq
    
    test_data = [ float(i) / (DATANUM * PKTNUM) for i in range(0, DATANUM * PKTNUM) ] # DEBUG:
    
    # directory = DATADIR + "para_of_" + str(dataSeq) + "_epoch_0"         # TODO: 后续根据新文件进行修改
    # with open(directory, 'r') as file:
    #     test_data = list(map(float, file.read().split("\n")[:-1])) # 最后有一个无效的 [:-1]
    
    manager = DataManager(host, test_data)
    packet_list = manager._partition_data(1, switchID, degree)
    
    iface = get_if()
    time_start = time.time()
    
    logger.info(host + " the number of packet is:" + str(len(packet_list)))
    for pkt in packet_list:
        # pkt.show()      # .show2() 不能展示新协议？
        # hexdump(pkt)    # 以经典的hexdump格式(十六进制)输出数据包.
        sendp(pkt, iface=iface, verbose=False)
    
    time_end = time.time()
    packageTotalBits =  len(packet_list) * len(packet_list[0]) * 8
    totalTime = time_end - time_start
    logger.info(host + ' time that send packages cost: ' + str(totalTime) + 's')
    logger.info(host + ' send package speed:' + str(packageTotalBits/totalTime) + 'bit/s')