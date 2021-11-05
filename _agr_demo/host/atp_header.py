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
        # BitField("switchId", 0, SWITCHIDBIT),
        # BitField("sequenceId", 0, SEQUENCEBIT),
        # ShortField("value", 0),
        # BitFieldLenField("data", 0, DATABYTE * 8),
    ]

class ATPData(Packet):
    name = "ATPData"
    fields_desc=[
        IntField("d00", 0),
        IntField("d01", 1),
        IntField("d02", 2),
        IntField("d03", 3),
        IntField("d04", 4),
        IntField("d05", 5),
        IntField("d06", 6),
        IntField("d07", 7),
        IntField("d08", 8),
        IntField("d09", 9),
        IntField("d10", 10),
        IntField("d11", 11),
        IntField("d12", 12),
        IntField("d13", 13),
        IntField("d14", 14),
        IntField("d15", 15),
        IntField("d16", 16),
        IntField("d17", 17),
        IntField("d18", 18),
        IntField("d19", 19),
        IntField("d20", 20),
        IntField("d21", 21),
        IntField("d22", 22),
        IntField("d23", 23),
        IntField("d24", 24),
        IntField("d25", 25),
        IntField("d26", 26),
        IntField("d27", 27),
        IntField("d28", 28),
        IntField("d29", 29),
        IntField("d30", 30),
        # IntField("d31", 31),
    ]

bind_layers(IP, ATP, proto=TYPE_ATP)
bind_layers(ATP, ATPData)