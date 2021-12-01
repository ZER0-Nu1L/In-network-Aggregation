from scapy.all import *    
from scapy.all import Ether, IP
from atp_header import ATP, ATPData
from config import *
from utils import *
from send import DataManager

hostMac = {
    "h1":  "08:00:00:01:01:01", "h2":  "08:00:00:01:02:01", "h3":  "08:00:00:01:03:01", "h4":  "08:00:00:01:04:01", "h5":  "08:00:00:01:05:01", "h6":  "08:00:00:01:06:01", "h7":  "08:00:00:01:07:01", "h8":  "08:00:00:01:08:01",
    "h9":  "08:00:00:02:01:01", "h10": "08:00:00:02:02:01", "h11": "08:00:00:02:03:01", "h12": "08:00:00:02:04:01", "h13": "08:00:00:02:05:01", "h14": "08:00:00:02:06:01", "h15": "08:00:00:02:07:01", "h16": "08:00:00:02:08:01",
    "h17": "08:00:00:03:01:01", "h18": "08:00:00:03:02:01", "h19": "08:00:00:03:03:01", "h20": "08:00:00:03:04:01", "h21": "08:00:00:03:05:01", "h22": "08:00:00:03:06:01", "h23": "08:00:00:03:07:01", "h24": "08:00:00:03:08:01"
}
hostIP = {
    "h1":  "10.1.1.1", "h2":  "10.1.2.1", "h3":  "10.1.3.1", "h4":  "10.1.4.1", "h5":  "10.1.5.1", "h6":  "10.1.6.1", "h7":  "10.1.7.1", "h8":  "10.1.8.1",
    "h9":  "10.2.1.1", "h10": "10.2.2.1", "h11": "10.2.3.1", "h12": "10.2.4.1", "h13": "10.2.5.1", "h14": "10.2.6.1", "h15": "10.2.7.1", "h16": "10.2.8.1",
    "h17": "10.3.1.1", "h18": "10.3.2.1", "h19": "10.3.3.1", "h20": "10.3.4.1", "h21": "10.3.5.1", "h22": "10.3.6.1", "h23": "10.3.7.1", "h24": "10.3.8.1"
}


def packet_list(PSHost, degree, switchID, pktNum, srcIP, srcMac):
    test_data = [ float(i) / (DATANUM * pktNum) for i in range(0, DATANUM * pktNum) ]
    manager = DataManager(PSHost, test_data)
    packet_list = manager._partition_data(1, switchID, degree, srcIP, srcMac)
    return packet_list

def packet_genarate(packageNamePrefix, PSHost, pktNum, hostGroup, groupPackageConf):
    '''
    hostGroup： gourpID - hostname
    groupPackageConf: groupID - switchID - degree
    '''
    workdir = os.getcwd()
    pcapDir = os.path.join(workdir, REPLAY_PCAP_DIR)

    for groupID, group in enumerate(hostGroup):
        for host in group:
            pcapName = packageNamePrefix + host + '.pcap'
            pcapFiledir = os.path.join(pcapDir, pcapName)
            
            switchID, degree = groupPackageConf[groupID]
            srcIP, srcMac = hostIP[host], hostMac[host]
            pktLst = packet_list(PSHost, degree, switchID, pktNum, srcIP, srcMac)
            logger.info((PSHost, degree, switchID, pktNum, pcapName, srcIP, srcMac))

            wrpcap(pcapFiledir, pktLst)

def _packet_genarate_all():
    '''
    # 并不能用:sob:，因为获取
    '''
    # switchML/ATP，共用
    packageNamePrefix = REPLAY_PCAP_PREFIX_SWITCHML
    PSHost = "10.3.9.1"
    pktNum = PKTNUM
    hostGroup = [
        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'],
        ['h9', 'h10', 'h11', 'h12', 'h13', 'h14', 'h15', 'h16'],
        ['h17', 'h18', 'h19', 'h20', 'h21', 'h22', 'h23', 'h24']
    ]
    groupPackageConf = [(2, 8), (3, 8), (4, 8)]
    packet_genarate(packageNamePrefix, PSHost, pktNum, hostGroup, groupPackageConf)
    
    # NGA
    packageNamePrefix = REPLAY_PCAP_PREFIX_NGA
    PSHost = "10.3.9.1"
    pktNum = PKTNUM
    hostGroup = [
        ['h1', 'h5', 'h8', 'h13', 'h16', 'h19', 'h24'],
        ['h4', 'h7', 'h12', 'h15', 'h18', 'h23'],
        ['h2', 'h11', 'h14', 'h17', 'h20', 'h22'],
        ['h3', 'h6', 'h9'],
        ['h10', 'h21']
    ]
    groupPackageConf = [(1, 7), (2, 6), (3, 6), (4, 3), (0, 2)]
    packet_genarate(packageNamePrefix, PSHost, pktNum, hostGroup, groupPackageConf)
    

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    workdir = os.getcwd()
    logDir = os.path.join(workdir, REPLAY_PCAP_LOG)
    setHandler(logger, logDir)

    _packet_genarate_all()


