from scapy.all import *
import sys, os

TYPE_ATP = 0x12

class ATP(Packet):
    name = "ATP"
    fields_desc = [
        BitField("aggregationDegree", 0, 8),
        ShortField("value", 0),
    ]

bind_layers(IP, ATP, proto=TYPE_ATP)
