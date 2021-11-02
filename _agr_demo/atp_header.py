from scapy.all import *
import sys, os
from config import *

TYPE_ATP = 0x12

'''
class ATP(Packet):
    name = "ATP"
    fields_desc = [
        ShortField("value", 0),
    ]
    def mysummary(self):
        return self.sprintf("value=%value%")
'''

class ATP(Packet):
    name = "ATP"
    fields_desc = [
        BitField("workerMap", 0, WORKERMAPBIT),
        BitField("aggregationDegree", 0, DEGREEBIT),
        BitField("overflow", 0, OVERFLOWBIT),
        BitField("isAck", 0, ISACKBIT),
        BitField("ecn", 0, ECNBIT),
        # BitField("switchId", 0, SWITCHIDBIT),
        # BitField("sequenceId", 0, SEQUENCEBIT),
        ShortField("value", 0),
        # BitFieldLenField("data", 0, DATABYTE * 8),
    ]

bind_layers(IP, ATP, type=TYPE_ATP) # TODO: 不知道有没有生效？？ 原来如果有这个，`pkt / Mytunnel`好像会自己加
