# Topo version
DEMOV4 = 0
TOPO07 = 1
TOPO09 = 2
TOPO11 = 3
TOPO13 = 4
TOPO15 = 5
TOPO0307 = 6
TOPO0310 = 7
TOPO0313 = 8
TOPO0316 = 9
TOPO0319 = 10
TOPO_VERSION = TOPO0319

# PS as receiver
if(TOPO_VERSION == DEMOV4):
    PS_INDEX = 24 # 25-1
elif(TOPO_VERSION == TOPO07 or TOPO_VERSION == TOPO0307):
    PS_INDEX = 6 # 7-1
elif(TOPO_VERSION == TOPO09):
    PS_INDEX = 8 # 9-1
elif(TOPO_VERSION == TOPO11):
    PS_INDEX = 10 # 11-1
elif(TOPO_VERSION == TOPO13):
    PS_INDEX = 12 # 13-1
elif(TOPO_VERSION == TOPO15):
    PS_INDEX = 14 # 15-1
elif(TOPO_VERSION == TOPO0310):
    PS_INDEX = 9 # 10-1
elif(TOPO_VERSION == TOPO0313):
    PS_INDEX = 12 # 13-1
elif(TOPO_VERSION == TOPO0316):
    PS_INDEX = 15 # 16-1
elif(TOPO_VERSION == TOPO0319):
    PS_INDEX = 18 # 19-1

RECEIVER_LOG = 'logs/receiver.log'

# Control plane
READTABLE_TIME = 2
READ_TIME = 60 * 150

# host monitor
AGGRE_MONITOR_TIME = 60 * 150

# test mod
GENERATOR_AND_SEND = 0
TCPREPLAY = 1
MININET_CLI = 2
SEND_MODE = TCPREPLAY

# if(SEND_MODE == GENERATOR_AND_SEND), configure:
NGA = 1
SWTICHML = 2
ATP = 3
TEST_MODE = NGA

# if(SEND_MODE == TCPREPLAY), configure:
REPLAY_PCAP_PREFIX_NGA = 'param_NGA-'
REPLAY_PCAP_PREFIX_SWITCHML = 'param_switchML-'
REPLAY_PCAP_PREFIX_ATP = 'param_switchML-' # 共用
REPLAY_PCAP_PREFIX = REPLAY_PCAP_PREFIX_NGA
REPLAY_SPEED = 0.07 # M

PKTNUM = 2000
if(TOPO_VERSION == DEMOV4):
    REPLAY_PCAP_DIR = 'mypcap/demov4/' + str(PKTNUM)  + '/'
elif(TOPO_VERSION == TOPO07):
    REPLAY_PCAP_DIR = 'mypcap/topo_7/' + str(PKTNUM)  + '/'
elif(TOPO_VERSION == TOPO09):
    REPLAY_PCAP_DIR = 'mypcap/topo_9/' + str(PKTNUM)  + '/'
elif(TOPO_VERSION == TOPO11):
    REPLAY_PCAP_DIR = 'mypcap/topo_11/' + str(PKTNUM)  + '/'
elif(TOPO_VERSION == TOPO13):
    REPLAY_PCAP_DIR = 'mypcap/topo_13/' + str(PKTNUM)  + '/'
elif(TOPO_VERSION == TOPO15):
    REPLAY_PCAP_DIR = 'mypcap/topo_15/' + str(PKTNUM)  + '/'
elif(TOPO_VERSION == TOPO0307):
    REPLAY_PCAP_DIR = 'mypcap/topo-3_7/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO0310):
    REPLAY_PCAP_DIR = 'mypcap/topo-3_10/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO0313):
    REPLAY_PCAP_DIR = 'mypcap/topo-3_13/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO0316):
    REPLAY_PCAP_DIR = 'mypcap/topo-3_16/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO0319):
    REPLAY_PCAP_DIR = 'mypcap/topo-3_19/' + str(PKTNUM) + '/'