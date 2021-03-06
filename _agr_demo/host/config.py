# Header
WORKERMAPBIT = 32
DEGREEBIT = 5
OVERFLOWBIT = 1
ISACKBIT = 1
ECNBIT = 1
RESENDBIT = 1
INDEXBIT = 5  # 2**10=1024
TIMEBIT = 5  # TODO: 现在是为了凑8
SWITCHIDBIT = 5
SEQUENCEBIT = 32

# Payload
DATANUM = 32
DATABYTE = 124 # 31 * 4 即 payload 中 DATANUM 个 4 字节整数
JOB_NUM = 32

# Number of packages
PKTNUM = 2000
ALLOW_LOSS_RATE = 1

# topo version
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

if(TOPO_VERSION == DEMOV4):
    # receiver set
    NGA_FLOW = 6
    SWITCHML_FLOW = 3
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO07):
    NGA_FLOW = 3
    SWITCHML_FLOW = 2
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO09):
    NGA_FLOW = 3
    SWITCHML_FLOW = 2
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO11):
    NGA_FLOW = 3
    SWITCHML_FLOW = 2
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO13):
    NGA_FLOW = 4
    SWITCHML_FLOW = 2
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO15):
    NGA_FLOW = 4
    SWITCHML_FLOW = 2
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO0307):
    NGA_FLOW = 3
    SWITCHML_FLOW = 3
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO0310):
    NGA_FLOW = 3 # TODO:
    SWITCHML_FLOW = 3
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO0313):
    NGA_FLOW = 5
    SWITCHML_FLOW = 3
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO0316):
    NGA_FLOW = 5+3 # TODO:
    SWITCHML_FLOW = 3
    ATP_FLOW = 1
elif(TOPO_VERSION == TOPO0319):
    NGA_FLOW = 5+1 # TODO:
    SWITCHML_FLOW = 3
    ATP_FLOW = 1

PS_RECEIVE_FLOW = NGA_FLOW

# if(SEND_MODE == TCPREPLAY), configure:
REPLAY_PCAP_LOG = 'logs/write_pcap.log' 
if(TOPO_VERSION == DEMOV4):
    REPLAY_PCAP_DIR = 'mypcap/demov4/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO07):
    REPLAY_PCAP_DIR = 'mypcap/topo_7/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO09):
    REPLAY_PCAP_DIR = 'mypcap/topo_9/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO11):
    REPLAY_PCAP_DIR = 'mypcap/topo_11/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO13):
    REPLAY_PCAP_DIR = 'mypcap/topo_13/' + str(PKTNUM) + '/'
elif(TOPO_VERSION == TOPO15):
    REPLAY_PCAP_DIR = 'mypcap/topo_15/' + str(PKTNUM) + '/'
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

REPLAY_PCAP_PREFIX_NGA = 'param_NGA-'
REPLAY_PCAP_PREFIX_SWITCHML = 'param_switchML-'
REPLAY_PCAP_PREFIX_ATP = 'param_switchML-' # 共用

# host monitor
AGGRE_MONITOR_LOG = 'logs/aggregation.log'

# PS as receiver
RECEIVER_LOG = 'logs/receiver.log'
LARK_HOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/ac8d355f-943f-44c6-bac5-248d80a10bf5'