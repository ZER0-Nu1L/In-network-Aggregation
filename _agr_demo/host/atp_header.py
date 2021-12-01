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
        # BitField("timestamp", 0, TIMEBIT),
        BitField("switchId", 0, SWITCHIDBIT),
        BitField("sequenceId", 0, SEQUENCEBIT),
    ]

class ATPData(Packet):
    name = "ATPData"
    fields_desc=[
        SignedIntField("d00", 0), # 有符号整数, 4bytes
        SignedIntField("d01", 0),
        SignedIntField("d02", 0),
        SignedIntField("d03", 0),
        SignedIntField("d04", 0),
        SignedIntField("d05", 0),
        SignedIntField("d06", 0),
        SignedIntField("d07", 0),
        SignedIntField("d08", 0),
        SignedIntField("d09", 0),
        SignedIntField("d10", 0),
        SignedIntField("d11", 0),
        SignedIntField("d12", 0),
        SignedIntField("d13", 0),
        SignedIntField("d14", 0),
        SignedIntField("d15", 0),
        SignedIntField("d16", 0),
        SignedIntField("d17", 0),
        SignedIntField("d18", 0),
        SignedIntField("d19", 0),
        SignedIntField("d20", 0),
        SignedIntField("d21", 0),
        SignedIntField("d22", 0),
        SignedIntField("d23", 0),
        SignedIntField("d24", 0),
        SignedIntField("d25", 0),
        SignedIntField("d26", 0),
        SignedIntField("d27", 0),
        SignedIntField("d28", 0),
        SignedIntField("d29", 0),
        SignedIntField("d30", 0),
        SignedIntField("d31", 0),
    ]

bind_layers(IP, ATP, proto=TYPE_ATP)
bind_layers(ATP, ATPData)