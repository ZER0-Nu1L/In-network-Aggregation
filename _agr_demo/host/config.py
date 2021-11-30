# Header
WORKERMAPBIT = 32
DEGREEBIT = 5
OVERFLOWBIT = 1
ISACKBIT = 1
ECNBIT = 1
RESENDBIT = 1
INDEXBIT = 5  # 2**5=32
TIMEBIT = 5  # TODO: 现在是为了凑8
SWITCHIDBIT = 5
SEQUENCEBIT = 32

# Payload
DATANUM = 32
DATABYTE = 124 # 31 * 4 即 payload 中 DATANUM 个 4 字节整数

# Data
DATADIR = "/home/p4/paras/"

# Number of packages
PKTNUM = 5000
ALLOW_LOSS_RATE = 0.95
PS_RECEIVE_FLOW = 6  # our route = 6, ATP = 1, SWITCH = 3

# host monitor
AGGRE_MONITOR_LOG = 'logs/aggregation.log'

# PS as receiver
RECEIVER_LOG = 'logs/receiver.log'
