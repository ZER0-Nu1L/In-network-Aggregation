# Header
WORKERMAPBIT = 32
DEGREEBIT = 5
OVERFLOWBIT = 1
ISACKBIT = 1
ECNBIT = 1
RESENDBIT = 1
INDEXBIT = 10  # 2**10=1024
# TIMEBIT = 5  # TODO: 现在是为了凑8
SWITCHIDBIT = 5
SEQUENCEBIT = 32

# Payload
DATANUM = 32
DATABYTE = 124 # 31 * 4 即 payload 中 DATANUM 个 4 字节整数
JOB_NUM = 1024

# Data
DATADIR = "/home/p4/paras/"

# Number of packages
PKTNUM = 1000
ALLOW_LOSS_RATE = 1
REPLAY_PCAP_LOG = 'logs/write_pcap.log' 
REPLAY_PCAP_DIR = 'mypcap/1000/'
REPLAY_PCAP_PREFIX_NGA = 'param_NGA-'
REPLAY_PCAP_PREFIX_SWITCHML = 'param_switchML-'
REPLAY_PCAP_PREFIX_ATP = 'param_switchML-' # 共用

# receiver set
NGA_FLOW = 6
SWITCHML_FLOW = 3
ATP_FLOW = 1
PS_RECEIVE_FLOW = NGA_FLOW

# host monitor
AGGRE_MONITOR_LOG = 'logs/aggregation.log'

# PS as receiver
RECEIVER_LOG = 'logs/receiver.log'
