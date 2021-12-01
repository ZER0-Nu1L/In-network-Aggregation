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
PKTNUM = 10
ALLOW_LOSS_RATE = 0.97
WRITE_PCAP_LOG = 'logs/write_pcap.log'
WRITE_PCAP_DIR = 'mypcap/'

OUR_SOLUTION_FLOW = 6
SWITCHML_FLOW = 3
ATP_FLOW = 1
PS_RECEIVE_FLOW = SWITCHML_FLOW

# host monitor
AGGRE_MONITOR_LOG = 'logs/aggregation.log'

# PS as receiver
RECEIVER_LOG = 'logs/receiver.log'
