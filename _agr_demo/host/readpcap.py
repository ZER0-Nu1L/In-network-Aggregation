from scapy.all import *
from scapy.all import Ether, IP, Raw, ICMP
from scapy.layers.inet import _IPOption_HDR
from atp_header import ATP, ATPData
from config import *



packets = rdpcap(REPLAY_PCAP_DIR+'/param_switchML-h1.pcap')

for packet in packets:
   if packet.haslayer(ATP):
       print(packet.show()) 