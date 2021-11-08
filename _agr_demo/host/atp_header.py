from scapy.all import *
import sys, os
from config import *

TYPE_ATP = 0x12

class ATP(Packet):
    name = "ATP"
    fields_desc = [
        BitField("workerMap", 0, WORKERMAPBIT),
        BitField("aggregationDegree", 0, DEGREEBIT),
        BitField("overflow", 0, OVERFLOWBIT),
        BitField("isAck", 0, ISACKBIT),
        BitField("ecn", 0, ECNBIT),
        BitField("resend", 0, RESENDBIT),
        BitField("aggIndex", 0, INDEXBIT),
        BitField("timestamp", 0, TIMEBIT),
        BitField("switchId", 0, SWITCHIDBIT),
        BitField("sequenceId", 0, SEQUENCEBIT),
    ]

class ATPData(Packet):
    name = "ATPData"
    fields_desc=[
        IntField("d00", 0),
        IntField("d01", 0),
        IntField("d02", 0),
        IntField("d03", 0),
        IntField("d04", 0),
        IntField("d05", 0),
        IntField("d06", 0),
        IntField("d07", 0),
        IntField("d08", 0),
        IntField("d09", 0),
        IntField("d10", 0),
        IntField("d11", 0),
        IntField("d12", 0),
        IntField("d13", 0),
        IntField("d14", 0),
        IntField("d15", 0),
        IntField("d16", 0),
        IntField("d17", 0),
        IntField("d18", 0),
        IntField("d19", 0),
        IntField("d20", 0),
        IntField("d21", 0),
        IntField("d22", 0),
        IntField("d23", 0),
        IntField("d24", 0),
        IntField("d25", 0),
        IntField("d26", 0),
        IntField("d27", 0),
        IntField("d28", 0),
        IntField("d29", 0),
        IntField("d30", 0),
        IntField("d31", 0),
    ]

bind_layers(IP, ATP, proto=TYPE_ATP)
bind_layers(ATP, ATPData)