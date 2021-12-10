from scapy.all import *    
from config import *
from utils import *
from send import DataManager
from pathlib import Path

class WritePcap:
    def __init__(self, PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA):
        self.PSHost = PSHost
        self.hostMacMap = hostMacMap
        self.hostIPMap = hostIPMap
        self.hostGroup_SA = hostGroup_SA
        self.groupPackageConf_SA = groupPackageConf_SA
        self.hostGroup_NGA = hostGroup_NGA
        self.groupPackageConf_NGA = groupPackageConf_NGA

    def packet_list(self, PSHost, degree, switchID, pktNum, srcIP, srcMac):
        test_data = [ float(i) / (DATANUM * pktNum) for i in range(0, DATANUM * pktNum) ]
        manager = DataManager(PSHost, test_data)
        packet_list = manager._partition_data(1, switchID, degree, srcIP, srcMac)
        return packet_list

    def packet_genarate(self, packageNamePrefix, PSHost, pktNum, hostGroup, groupPackageConf):
        '''
        hostGroup： gourpID - hostname
        groupPackageConf: groupID - switchID - degree
        '''
        workdir = os.getcwd()
        pcapDir = os.path.join(workdir, REPLAY_PCAP_DIR)
        Path(pcapDir).mkdir(parents=True, exist_ok=True)

        for groupID, group in enumerate(hostGroup):
            for host in group:
                pcapName = packageNamePrefix + host + '.pcap'
                pcapFiledir = os.path.join(pcapDir, pcapName)

                switchID, degree = groupPackageConf[groupID]
                srcIP, srcMac = self.hostIPMap[host], self.hostMacMap[host]
                pktLst = self.packet_list(PSHost, degree, switchID, pktNum, srcIP, srcMac)
                logger.info((PSHost, degree, switchID, pktNum, pcapName, srcIP, srcMac))

                wrpcap(pcapFiledir, pktLst)

    def _packet_genarate_all(self, pktNum):
        # switchML/ATP，共用
        packageNamePrefix = REPLAY_PCAP_PREFIX_SWITCHML
        self.packet_genarate(packageNamePrefix, self.PSHost, pktNum, self.hostGroup_SA, self.groupPackageConf_SA)
        
        # NGA
        packageNamePrefix = REPLAY_PCAP_PREFIX_NGA
        self.packet_genarate(packageNamePrefix, self.PSHost, pktNum, self.hostGroup_NGA, self.groupPackageConf_NGA)
    

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    workdir = os.getcwd()
    logDir = os.path.join(workdir, REPLAY_PCAP_LOG)
    setHandler(logger, logDir)
    if(TOPO_VERSION == DEMOV4):
        PSHost = "10.3.9.1"
        hostMacMap = {
            "h1":  "08:00:00:01:01:01", "h2":  "08:00:00:01:02:01", "h3":  "08:00:00:01:03:01", "h4":  "08:00:00:01:04:01", "h5":  "08:00:00:01:05:01", "h6":  "08:00:00:01:06:01", "h7":  "08:00:00:01:07:01", "h8":  "08:00:00:01:08:01",
            "h9":  "08:00:00:02:01:01", "h10": "08:00:00:02:02:01", "h11": "08:00:00:02:03:01", "h12": "08:00:00:02:04:01", "h13": "08:00:00:02:05:01", "h14": "08:00:00:02:06:01", "h15": "08:00:00:02:07:01", "h16": "08:00:00:02:08:01",
            "h17": "08:00:00:03:01:01", "h18": "08:00:00:03:02:01", "h19": "08:00:00:03:03:01", "h20": "08:00:00:03:04:01", "h21": "08:00:00:03:05:01", "h22": "08:00:00:03:06:01", "h23": "08:00:00:03:07:01", "h24": "08:00:00:03:08:01"
        }
        hostIPMap = {
            "h1":  "10.1.1.1", "h2":  "10.1.2.1", "h3":  "10.1.3.1", "h4":  "10.1.4.1", "h5":  "10.1.5.1", "h6":  "10.1.6.1", "h7":  "10.1.7.1", "h8":  "10.1.8.1",
            "h9":  "10.2.1.1", "h10": "10.2.2.1", "h11": "10.2.3.1", "h12": "10.2.4.1", "h13": "10.2.5.1", "h14": "10.2.6.1", "h15": "10.2.7.1", "h16": "10.2.8.1",
            "h17": "10.3.1.1", "h18": "10.3.2.1", "h19": "10.3.3.1", "h20": "10.3.4.1", "h21": "10.3.5.1", "h22": "10.3.6.1", "h23": "10.3.7.1", "h24": "10.3.8.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'],
            ['h9', 'h10', 'h11', 'h12', 'h13', 'h14', 'h15', 'h16'],
            ['h17', 'h18', 'h19', 'h20', 'h21', 'h22', 'h23', 'h24']
        ]
        groupPackageConf_SA = [(2, 8), (3, 8), (4, 8)]
        # switchID, degree = groupPackageConf[groupID]
        hostGroup_NGA = [
            ['h1', 'h5', 'h8', 'h13', 'h16', 'h19', 'h24'],
            ['h4', 'h7', 'h12', 'h15', 'h18', 'h23'],
            ['h2', 'h11', 'h14', 'h17', 'h20', 'h22'],
            ['h3', 'h6', 'h9'],
            ['h10', 'h21']
        ]
        groupPackageConf_NGA = [(1, 7), (2, 6), (3, 6), (4, 3), (0, 2)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO07):
        PSHost = "10.2.4.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01", "h2": "08:00:00:01:02:01", "h3": "08:00:00:01:03:01",
            "h4": "08:00:00:02:01:01", "h5": "08:00:00:02:02:01", "h6": "08:00:00:02:03:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1", "h2": "10.1.2.1", "h3": "10.1.3.1",
            "h4": "10.2.1.1", "h5": "10.2.2.1", "h6": "10.2.3.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3'],
            ['h4', 'h5', 'h6']
        ]
        groupPackageConf_SA = [(2, 3), (3, 3)]

        hostGroup_NGA = [
            ['h3', 'h5', 'h6'],
            ['h1'],
            ['h2', 'h4']
        ]
        groupPackageConf_NGA = [(2, 3), (3, 1), (4, 2)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO09):
        PSHost = "10.2.5.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01", "h2": "08:00:00:01:02:01", "h3": "08:00:00:01:03:01", "h4": "08:00:00:01:04:01",
            "h5": "08:00:00:02:01:01", "h6": "08:00:00:02:02:01", "h7": "08:00:00:02:03:01", "h8": "08:00:00:02:04:01",
        }
        hostIPMap = {
            "h1": "10.1.1.1", "h2": "10.1.2.1", "h3": "10.1.3.1", "h4": "10.1.4.1",
            "h5": "10.2.1.1", "h6": "10.2.2.1", "h7": "10.2.3.1", "h8": "10.2.4.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4'],
            ['h5', 'h6', 'h7', 'h8']
        ]
        groupPackageConf_SA = [(2, 4), (3, 4)]

        hostGroup_NGA = [
            ['h3', 'h4', 'h5', 'h7'],
            ['h1'],
            ['h2', 'h6', 'h8']
        ]
        groupPackageConf_NGA = [(2, 4), (3, 1), (4, 3)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO11):
        PSHost = "10.2.6.1"
        hostMacMap = {
            "h1":	"08:00:00:01:01:01",    "h2":	"08:00:00:01:02:01",    "h3":	"08:00:00:01:03:01",    "h4":	"08:00:00:01:04:01",    "h5":	"08:00:00:01:05:01",
            "h6":	"08:00:00:02:01:01",    "h7":	"08:00:00:02:02:01",    "h8":	"08:00:00:02:03:01",    "h9":	"08:00:00:02:04:01",    "h10":	"08:00:00:02:05:01"
        }
        hostIPMap = {
            "h1":	"10.1.1.1",     "h2":	"10.1.2.1",     "h3":	"10.1.3.1",     "h4":	"10.1.4.1",     "h5":	"10.1.5.1",
            "h6":	"10.2.1.1",     "h7":	"10.2.2.1",     "h8":	"10.2.3.1",     "h9":	"10.2.4.1",     "h10":	"10.2.5.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4', 'h5'],
            ['h6', 'h7', 'h8', 'h9', 'h10']
        ]
        groupPackageConf_SA = [(2, 5), (3, 5)]

        hostGroup_NGA = [
            ['h1', 'h2', 'h4', 'h6', 'h10'],
            ['h3'],
            ['h5', 'h7', 'h8', 'h9']
        ]
        groupPackageConf_NGA = [(2, 5), (1, 1), (4, 4)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO13):
        PSHost = "10.2.7.1"
        hostMacMap = {
            "h1": 	"08:00:00:01:01:01",    "h2": 	"08:00:00:01:02:01",    "h3": 	"08:00:00:01:03:01",    "h4": 	"08:00:00:01:04:01",    "h5": 	"08:00:00:01:05:01",    "h6": 	"08:00:00:01:06:01",
            "h7": 	"08:00:00:02:01:01",    "h8": 	"08:00:00:02:02:01",    "h9": 	"08:00:00:02:03:01",    "h10": 	"08:00:00:02:04:01",    "h11": 	"08:00:00:02:05:01",    "h12": 	"08:00:00:02:06:01"
        }
        hostIPMap = {
            "h1": 	"10.1.1.1",     "h2": 	"10.1.2.1",     "h3": 	"10.1.3.1",     "h4": 	"10.1.4.1",     "h5": 	"10.1.5.1",     "h6": 	"10.1.6.1",
            "h7": 	"10.2.1.1",     "h8": 	"10.2.2.1",     "h9": 	"10.2.3.1",     "h10": 	"10.2.4.1",     "h11": 	"10.2.5.1",     "h12": 	"10.2.6.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
            ['h7', 'h8', 'h9', 'h10', 'h11', 'h12']
        ]
        groupPackageConf_SA = [(2, 6), (3, 6)]

        hostGroup_NGA = [
            ['h1', 'h4', 'h5', 'h6', 'h7', 'h10'],
            ['h11'],
            ['h2', 'h9', 'h12'],
            ['h3', 'h8']
        ]
        groupPackageConf_NGA = [(2, 6), (3, 1), (1, 3), (4, 2)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO15):
        PSHost = "10.2.8.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01",  "h2": "08:00:00:01:02:01",   "h3": "08:00:00:01:03:01",    "h4": "08:00:00:01:04:01",     "h5": "08:00:00:01:05:01",   "h6": "08:00:00:01:06:01",    "h7": "08:00:00:01:07:01",
            "h8": "08:00:00:02:01:01",  "h9": "08:00:00:02:02:01",   "h10": "08:00:00:02:03:01",   "h11": "08:00:00:02:04:01",   "h12": "08:00:00:02:05:01",   "h13": "08:00:00:02:06:01",   "h14": "08:00:00:02:07:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1",   "h2": "10.1.2.1",  "h3": "10.1.3.1", "h4": "10.1.4.1",    "h5": "10.1.5.1",   "h6": "10.1.6.1",  "h7": "10.1.7.1",
            "h8": "10.2.1.1",   "h9": "10.2.2.1",  "h10": "10.2.3.1",    "h11": "10.2.4.1",  "h12": "10.2.5.1",    "h13": "10.2.6.1",  "h14": "10.2.7.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7'],
            ['h8', 'h9', 'h10', 'h11', 'h12', 'h13', 'h14']
        ]
        groupPackageConf_SA = [(2, 7), (3, 7)]

        hostGroup_NGA = [
            ['h1'],
            ['h2', 'h3', 'h5', 'h7', 'h9' ],
            ['h12', 'h13'],
            ['h4', 'h6', 'h8', 'h10', 'h11', 'h13', 'h14']
        ]
        groupPackageConf_NGA = [(1, 1), (2, 5), (3, 1), (4, 7)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO0307):
        PSHost = "10.3.3.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01",  "h2": "08:00:00:01:02:01",
            "h3": "08:00:00:02:01:01",  "h4": "08:00:00:02:02:01",
            "h5": "08:00:00:03:01:01",  "h6": "08:00:00:03:02:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1",   "h2": "10.1.2.1",
            "h3": "10.2.1.1",   "h4": "10.2.2.1",
            "h5": "10.3.1.1",   "h6": "10.3.2.1"
        }

        hostGroup_SA = [
            ['h1', 'h2'],
            ['h3', 'h4'],
            ['h5', 'h6']
        ]
        groupPackageConf_SA = [(2, 2), (3, 2), (4, 2)]

        hostGroup_NGA = [
            ['h1', 'h2'],
            ['h3', 'h4'],
            ['h5', 'h6']
        ]
        groupPackageConf_NGA = [(2, 2), (3, 2), (4, 2)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO0310):
        PSHost = "10.3.4.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01",  "h2": "08:00:00:01:02:01",    "h3": "08:00:00:01:03:01",
            "h4": "08:00:00:02:01:01",  "h5": "08:00:00:02:02:01",    "h6": "08:00:00:02:03:01",
            "h7": "08:00:00:03:01:01",  "h8": "08:00:00:03:02:01",    "h9": "08:00:00:03:03:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1",   "h2": "10.1.2.1",  "h3": "10.1.3.1",
            "h4": "10.2.1.1",   "h5": "10.2.2.1",  "h6": "10.2.3.1",
            "h7": "10.3.1.1",   "h8": "10.3.2.1",  "h9": "10.3.3.1",
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3'],
            ['h4', 'h5', 'h6'],
            ['h7', 'h8', 'h9']
        ]
        groupPackageConf_SA = [(2, 3), (3, 3), (4, 3)]

        hostGroup_NGA = [
            ['h1', 'h2', 'h3'],
            ['h4', 'h5', 'h6'],
            ['h7', 'h8', 'h9']
        ]
        groupPackageConf_NGA = [(2, 3), (3, 3), (4, 3)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO0313):
        PSHost = "10.3.5.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01",  "h2": "08:00:00:01:02:01",    "h3": "08:00:00:01:03:01",     "h4": "08:00:00:01:04:01",
            "h5": "08:00:00:02:01:01",  "h6": "08:00:00:02:02:01",    "h7": "08:00:00:02:03:01",     "h8": "08:00:00:02:04:01",
            "h9": "08:00:00:03:01:01",  "h10": "08:00:00:03:02:01",   "h11": "08:00:00:03:03:01",    "h12": "08:00:00:03:04:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1",   "h2": "10.1.2.1",  "h3": "10.1.3.1",    "h4": "10.1.4.1",
            "h5": "10.2.1.1",   "h6": "10.2.2.1",  "h7": "10.2.3.1",    "h8": "10.2.4.1",
            "h9": "10.3.1.1",   "h10": "10.3.2.1", "h11": "10.3.3.1",   "h12": "10.3.4.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4'],
            ['h5', 'h6', 'h7', 'h8'],
            ['h9', 'h10', 'h11', 'h12']
        ]
        groupPackageConf_SA = [(2, 4), (3, 4), (4, 4)]

        hostGroup_NGA = [
            ['h1', 'h2'],
            ['h3', 'h4'],
            ['h5', 'h6'],
            ['h7', 'h8'],
            ['h9', 'h10', 'h11', 'h12']
        ]
        groupPackageConf_NGA = [(2, 2), (1, 2), (3, 2), (5, 2), (4, 4)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO0316):
        PSHost = "10.3.6.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01",  "h2": "08:00:00:01:02:01",    "h3": "08:00:00:01:03:01",  "h4": "08:00:00:01:04:01",      "h5": "08:00:00:01:05:01",
            "h6": "08:00:00:02:01:01",  "h7": "08:00:00:02:02:01",    "h8": "08:00:00:02:03:01",  "h9": "08:00:00:02:04:01",      "h10": "08:00:00:02:05:01",
            "h11": "08:00:00:03:01:01", "h12": "08:00:00:03:02:01",  "h13": "08:00:00:03:03:01",   "h14": "08:00:00:03:04:01",    "h15": "08:00:00:03:05:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1",   "h2": "10.1.2.1",     "h3": "10.1.3.1",      "h4": "10.1.4.1",     "h5": "10.1.5.1",
            "h6": "10.2.1.1",   "h7": "10.2.2.1",     "h8": "10.2.3.1",      "h9": "10.2.4.1",     "h10": "10.2.5.1",
            "h11": "10.3.1.1",  "h12": "10.3.2.1",    "h13": "10.3.3.1",     "h14": "10.3.4.1",    "h15": "10.3.5.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4', 'h5'],
            ['h6', 'h7', 'h8', 'h9', 'h10'],
            ['h11', 'h12', 'h13', 'h14', 'h15']
        ]
        groupPackageConf_SA = [(2, 5), (3, 5), (4, 5)]

        hostGroup_NGA = [
            ['h1', 'h2', 'h3'],
            ['h4', 'h5'],
            ['h6', 'h7', 'h8'],
            ['h9', 'h10'],
            ['h11', 'h12'],
            ['h13', 'h14', 'h15']
        ]
        groupPackageConf_NGA = [(2, 3), (1, 2), (3, 3), (5, 2), (4, 2), (0, 3)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)

    elif(TOPO_VERSION == TOPO0319):
        PSHost = "10.3.7.1"
        hostMacMap = {
            "h1": "08:00:00:01:01:01",  "h2": "08:00:00:01:02:01",    "h3": "08:00:00:01:03:01",     "h4": "08:00:00:01:04:01",      "h5": "08:00:00:01:05:01",  "h6": "08:00:00:01:06:01",
            "h7": "08:00:00:02:01:01",  "h8": "08:00:00:02:02:01",    "h9": "08:00:00:02:03:01",     "h10": "08:00:00:02:04:01",     "h11": "08:00:00:02:05:01", "h12": "08:00:00:02:06:01",
            "h13": "08:00:00:03:01:01", "h14": "08:00:00:03:02:01",   "h15": "08:00:00:03:03:01",    "h16": "08:00:00:03:04:01",     "h17": "08:00:00:03:05:01", "h18": "08:00:00:03:06:01"
        }
        hostIPMap = {
            "h1": "10.1.1.1",   "h2": "10.1.2.1",     "h3": "10.1.3.1",     "h4": "10.1.4.1",        "h5": "10.1.5.1",   "h6": "10.1.6.1",
            "h7": "10.2.1.1",   "h8": "10.2.2.1",     "h9": "10.2.3.1",     "h10": "10.2.4.1",       "h11": "10.2.5.1",  "h12": "10.2.6.1",
            "h13": "10.3.1.1",  "h14": "10.3.2.1",    "h15": "10.3.3.1",    "h16": "10.3.4.1",       "h17": "10.3.5.1",  "h18": "10.3.6.1"
        }

        hostGroup_SA = [
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
            ['h7', 'h8', 'h9', 'h10', 'h11', 'h12'],
            ['h13', 'h14', 'h15', 'h16', 'h17', 'h18']
        ]
        groupPackageConf_SA = [(2, 6), (3, 6), (4, 6)]

        hostGroup_NGA = [
            ['h1', 'h2', 'h3'],
            ['h4', 'h5', 'h6'],
            ['h7', 'h8', 'h9'],
            ['h10', 'h11', 'h12'],
            ['h13', 'h14', 'h15', 'h16', 'h17'],
            ['h18']
        ]
        groupPackageConf_NGA = [(2, 3), (1, 3), (3, 3), (5, 3), (4, 5), (0, 1)]

        worker = WritePcap(PSHost, hostMacMap, hostIPMap, hostGroup_SA, groupPackageConf_SA, hostGroup_NGA, groupPackageConf_NGA)

        worker._packet_genarate_all(PKTNUM)