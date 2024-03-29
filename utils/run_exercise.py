#!/usr/bin/env python3
# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Adapted by Robert MacDavid (macdavid@cs.princeton.edu) from scripts found in
# the p4app repository (https://github.com/p4lang/p4app)
#
# We encourage you to dissect this script to better understand the BMv2/Mininet
# environment used by the P4 tutorial.
#
import os, sys, json, subprocess, re, argparse
from time import sleep
from time import time
from signal import SIGINT

from p4_mininet import P4Switch, P4Host

from mininet.net import Mininet
from mininet.topo import SingleSwitchReversedTopo, Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.util import pmonitor
from config import *

from p4runtime_switch import P4RuntimeSwitch
import p4runtime_lib.simple_controller

def configureP4Switch(**switch_args):
    """ Helper class that is called by mininet to initialize
        the virtual P4 switches. The purpose is to ensure each
        switch's thrift server is using a unique port.
    """
    if "sw_path" in switch_args and 'grpc' in switch_args['sw_path']:
        # If grpc appears in the BMv2 switch target, we assume will start P4Runtime
        class ConfiguredP4RuntimeSwitch(P4RuntimeSwitch):
            def __init__(self, *opts, **kwargs):
                kwargs.update(switch_args)
                P4RuntimeSwitch.__init__(self, *opts, **kwargs)

            def describe(self):
                print("%s -> gRPC port: %d" % (self.name, self.grpc_port))

        return ConfiguredP4RuntimeSwitch
    else:
        class ConfiguredP4Switch(P4Switch):
            next_thrift_port = 9090
            def __init__(self, *opts, **kwargs):
                global next_thrift_port
                kwargs.update(switch_args)
                kwargs['thrift_port'] = ConfiguredP4Switch.next_thrift_port
                ConfiguredP4Switch.next_thrift_port += 1
                P4Switch.__init__(self, *opts, **kwargs)

            def describe(self):
                print("%s -> Thrift port: %d" % (self.name, self.thrift_port))

        return ConfiguredP4Switch


class ExerciseTopo(Topo):
    """ The mininet topology class for the P4 tutorial exercises.
    """
    def __init__(self, hosts, switches, links, log_dir, bmv2_exe, pcap_dir, **opts):
        Topo.__init__(self, **opts)
        host_links = []
        switch_links = []

        # assumes host always comes first for host<-->switch links
        for link in links:
            if link['node1'][0] == 'h':
                host_links.append(link)
            else:
                switch_links.append(link)

        for sw, params in switches.items():
            if "program" in params:
                switchClass = configureP4Switch(
                        sw_path=bmv2_exe,
                        json_path=params["program"],
                        log_console=True,
                        pcap_dump=pcap_dir)
            else:
                # add default switch
                switchClass = None
            self.addSwitch(sw, log_file="%s/%s.log" %(log_dir, sw), cls=switchClass)

        for link in host_links:
            host_name = link['node1']
            sw_name, sw_port = self.parse_switch_node(link['node2'])
            host_ip = hosts[host_name]['ip']
            host_mac = hosts[host_name]['mac']
            self.addHost(host_name, ip=host_ip, mac=host_mac)
            self.addLink(host_name, sw_name,
                         delay=link['latency'], bw=link['bandwidth'],
                         port2=sw_port)

        for link in switch_links:
            sw1_name, sw1_port = self.parse_switch_node(link['node1'])
            sw2_name, sw2_port = self.parse_switch_node(link['node2'])
            self.addLink(sw1_name, sw2_name,
                        port1=sw1_port, port2=sw2_port,
                        delay=link['latency'], bw=link['bandwidth'])


    def parse_switch_node(self, node):
        assert(len(node.split('-')) == 2)
        sw_name, sw_port = node.split('-')
        try:
            sw_port = int(sw_port[1:])
        except:
            raise Exception('Invalid switch node in topology file: {}'.format(node))
        return sw_name, sw_port


class ExerciseRunner:
    """
        Attributes:
            log_dir  : string   // directory for mininet log files
            pcap_dir : string   // directory for mininet switch pcap files
            quiet    : bool     // determines if we print logger messages

            hosts    : dict<string, dict> // mininet host names and their associated properties
            switches : dict<string, dict> // mininet switch names and their associated properties
            links    : list<dict>         // list of mininet link properties

            switch_json : string // json of the compiled p4 example
            bmv2_exe    : string // name or path of the p4 switch binary

            topo : Topo object   // The mininet topology instance
            net : Mininet object // The mininet instance

    """
    def logger(self, *items):
        if not self.quiet:
            print(' '.join(items))

    def format_latency(self, l):
        """ Helper method for parsing link latencies from the topology json. """
        if isinstance(l, str):
            return l
        else:
            return str(l) + "ms"


    def __init__(self, topo_file, log_dir, pcap_dir,
                       switch_json, bmv2_exe='simple_switch', quiet=False):
        """ Initializes some attributes and reads the topology json. Does not
            actually run the exercise. Use run_exercise() for that.

            Arguments:
                topo_file : string    // A json file which describes the exercise's
                                         mininet topology.
                log_dir  : string     // Path to a directory for storing exercise logs
                pcap_dir : string     // Ditto, but for mininet switch pcap files
                switch_json : string  // Path to a compiled p4 json for bmv2
                bmv2_exe    : string  // Path to the p4 behavioral binary
                quiet : bool          // Enable/disable script debug messages
        """

        self.quiet = quiet
        self.logger('Reading topology file.')
        with open(topo_file, 'r') as f:
            topo = json.load(f)
        self.hosts = topo['hosts']
        self.switches = topo['switches']
        self.links = self.parse_links(topo['links'])

        # Ensure all the needed directories exist and are directories
        for dir_name in [log_dir, pcap_dir]:
            if not os.path.isdir(dir_name):
                if os.path.exists(dir_name):
                    raise Exception("'%s' exists and is not a directory!" % dir_name)
                os.mkdir(dir_name)
        self.log_dir = log_dir
        self.pcap_dir = pcap_dir
        self.switch_json = switch_json
        self.bmv2_exe = bmv2_exe


    def run_exercise(self):
        setLogLevel( 'info' )

        """ Sets up the mininet instance, programs the switches,
            and starts the mininet CLI. This is the main method to run after
            initializing the object.
        """
        # Initialize mininet with the topology specified by the config
        self.create_network()
        self.net.start()
        sleep(1)

        # some programming that must happen after the net has started
        self.program_hosts()
        # self.program_switches() # NOTE: 拆开如下：

        if(TOPO_VERSION <= TOPO15):
            # 生成五个进程（一个主进程，另外四个用于启动控制平面和四个交换机的交互）
            index = 0
            while index < 4:
                pid = os.fork()
                if pid == 0:
                    break
                index += 1
            
            if (index < 4):
                # for sw_name, sw_dict in self.switches.items():
                sw_name = 's' + str(index+1) # TODO: 硬编码
                sw_dict = self.switches[sw_name]
                # self.program_switch_p4runtime(sw_name, sw_dict) # NOTE: 拆开如下：
                sw_obj = self.net.get(sw_name)
                grpc_port = sw_obj.grpc_port
                device_id = sw_obj.device_id
                runtime_json = sw_dict['runtime_json']
                self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
                
                with open(runtime_json, 'r') as sw_conf_file:
                    outfile = '%s/%s-p4runtime-requests.txt' %(self.log_dir, sw_name)
                    p4runtime_lib.simple_controller.program_switch(
                        addr='127.0.0.1:%d' % grpc_port,
                        device_id=device_id,
                        sw_conf_file=sw_conf_file,
                        workdir=os.getcwd(),
                        proto_dump_fpath=outfile)
                print(sw_name + " finish its work.")
                sys.exit(0) # NOTE: 结束子进程
        else:
            # 生成七个进程（一个主进程，另外六个用于启动控制平面和六个交换机的交互）
            index = 0
            while index < 6:
                pid = os.fork()
                if pid == 0:
                    break
                index += 1
            
            if (index < 6):
                # for sw_name, sw_dict in self.switches.items():
                sw_name = 's' + str(index+1) # TODO: 硬编码
                sw_dict = self.switches[sw_name]
                # self.program_switch_p4runtime(sw_name, sw_dict) # NOTE: 拆开如下：
                sw_obj = self.net.get(sw_name)
                grpc_port = sw_obj.grpc_port
                device_id = sw_obj.device_id
                runtime_json = sw_dict['runtime_json']
                self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
                
                with open(runtime_json, 'r') as sw_conf_file:
                    outfile = '%s/%s-p4runtime-requests.txt' %(self.log_dir, sw_name)
                    p4runtime_lib.simple_controller.program_switch(
                        addr='127.0.0.1:%d' % grpc_port,
                        device_id=device_id,
                        sw_conf_file=sw_conf_file,
                        workdir=os.getcwd(),
                        proto_dump_fpath=outfile)
                print(sw_name + " finish its work.")
                sys.exit(0) # NOTE: 结束子进程

        ## Test aggregation
        sleep(15) # 等待连接都完成
        print('')
        print('======================================================================')
        print('Start test In-network aggregation')
        print('======================================================================')
        print('')


        popens = {}
        if(SEND_MODE == GENERATOR_AND_SEND):
            PS = self.net.hosts[PS_INDEX]
            # workdir = os.getcwd()
            # logDir = os.path.join(workdir, RECEIVER_LOG)
            # PS.cmd("python3 ./host/receive.py" + " > " + logDir + " &")
            PS.cmd("python3 ./host/receive.py" + " &")
            sleep(5) # DEBUG:
            print("SEND_MODE == GENERATOR_AND_SEND")
            if(TEST_MODE == NGA):
                print("TEST_MODE == NGA")
                if(TOPO_VERSION == DEMOV4):
                    print("TOPO_VERSION == DEMOV4")
                    # 1. Our solution
                    # h1, h5, h8, h13, h16, h19, h24
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[4], self.net.hosts[7], self.net.hosts[12], self.net.hosts[15], self.net.hosts[18], self.net.hosts[23]]
                    # h4, h7, h12, h15, h18, h23
                    hostGroup2 = [self.net.hosts[3], self.net.hosts[6], self.net.hosts[11], self.net.hosts[14], self.net.hosts[17], self.net.hosts[22]]
                    # h2, h11, h14, h17, h20, h22
                    hostGroup3 = [self.net.hosts[1], self.net.hosts[10], self.net.hosts[13], self.net.hosts[16], self.net.hosts[19], self.net.hosts[21]]
                    # h3, h6, h9
                    hostGroup4 = [self.net.hosts[2], self.net.hosts[5], self.net.hosts[8]]
                    # h10, h21
                    hostGroup5 = [self.net.hosts[9], self.net.hosts[20]]

                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 7 --switchId 1')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 6 --switchId 2')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 6 --switchId 3')
                        elif host in hostGroup4:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 3 --switchId 4')
                        elif host in hostGroup5:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 2 --switchId 0')

                elif(TOPO_VERSION == TOPO07):
                    print("TOPO_VERSION == TOPO07")
                    # h3, h5, h6
                    hostGroup1 = [self.net.hosts[2], self.net.hosts[4], self.net.hosts[5]]
                    # h1
                    hostGroup2 = [self.net.hosts[0]]
                    # h2, h4
                    hostGroup3 = [self.net.hosts[1], self.net.hosts[3]]

                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.4.1 --degree 3 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.4.1 --degree 1 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.4.1 --degree 2 --switchId 4')

                elif(TOPO_VERSION == TOPO09):
                    print("TOPO_VERSION == TOPO09")
                    # h3, h4, h5, h7
                    hostGroup1 = [self.net.hosts[2], self.net.hosts[3], self.net.hosts[4], self.net.hosts[6]]
                    # h1
                    hostGroup2 = [self.net.hosts[0]]
                    # h2, h6, h8
                    hostGroup3 = [self.net.hosts[1], self.net.hosts[5], self.net.hosts[7]]

                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.5.1 --degree 4 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.5.1 --degree 1 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.5.1 --degree 3 --switchId 4')

                elif(TOPO_VERSION == TOPO11):
                    print("TOPO_VERSION == TOPO11")
                    # h1, h2, h4, h6, h10
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[3], self.net.hosts[5], self.net.hosts[9]]
                    # h3
                    hostGroup2 = [self.net.hosts[2]]
                    # h5, h7, h8, h9
                    hostGroup3 = [self.net.hosts[4], self.net.hosts[6], self.net.hosts[7], self.net.hosts[8]]

                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.6.1 --degree 5 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.6.1 --degree 1 --switchId 1')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.6.1 --degree 4 --switchId 4')

                # TODO: 这个写的Group顺序有点乱
                elif(TOPO_VERSION == TOPO13):
                    print("TOPO_VERSION == TOPO13")
                    # h1, h4, h5, h6, h7, h10
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[3], self.net.hosts[4], self.net.hosts[5], self.net.hosts[6], self.net.hosts[9]]
                    # h11
                    hostGroup2 = [self.net.hosts[10]]
                    # h2, h9, h12
                    hostGroup3 = [self.net.hosts[1], self.net.hosts[8], self.net.hosts[11]]
                    # h3, h8
                    hostGroup4 = [self.net.hosts[2], self.net.hosts[7]]

                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.7.1 --degree 6 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.7.1 --degree 1 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.7.1 --degree 3 --switchId 1')
                        elif host in hostGroup4:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.7.1 --degree 2 --switchId 4')

                elif(TOPO_VERSION == TOPO15):
                    print("TOPO_VERSION == TOPO15")
                    # h1
                    hostGroup1 = [self.net.hosts[0]]
                    # h2, h3, h5, h7, h9 
                    hostGroup2 = [self.net.hosts[1], self.net.hosts[2], self.net.hosts[4], self.net.hosts[6], self.net.hosts[8]]
                    # h12, h13
                    hostGroup3 = [self.net.hosts[11]]
                    # h4, h6, h8, h10, h11, h13, h14
                    hostGroup4 = [self.net.hosts[3], self.net.hosts[5], self.net.hosts[7], self.net.hosts[9], self.net.hosts[10], self.net.hosts[12], self.net.hosts[13]]

                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.8.1 --degree 1 --switchId 1')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.8.1 --degree 5 --switchId 2')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.8.1 --degree 1 --switchId 3')
                        elif host in hostGroup4:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.8.1 --degree 7 --switchId 4')

                elif(TOPO_VERSION == TOPO0307):
                    print("TOPO_VERSION == TOPO0307")
                    # h1, h2
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1]]
                    # h3, h4
                    hostGroup2 = [self.net.hosts[2], self.net.hosts[3]]
                    # h5, h6
                    hostGroup3 = [self.net.hosts[4], self.net.hosts[5]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.3.1 --degree 2 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.3.1 --degree 2 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.3.1 --degree 2 --switchId 4')

                elif(TOPO_VERSION == TOPO0310):
                    print("TOPO_VERSION == TOPO0310")
                    # h1, h2, h3
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2]]
                    # h4, h5, h6
                    hostGroup2 = [self.net.hosts[3], self.net.hosts[4], self.net.hosts[5]]
                    # h7, h8, h9
                    hostGroup3 = [self.net.hosts[6], self.net.hosts[7], self.net.hosts[8]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.4.1 --degree 3 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.4.1 --degree 3 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.4.1 --degree 3 --switchId 4')

                elif(TOPO_VERSION == TOPO0313):
                    print("TOPO_VERSION == TOPO0313")
                    # h1, h2
                    hostGroup1_1 = [self.net.hosts[0], self.net.hosts[1]]
                    # h3, h4
                    hostGroup1_2 = [self.net.hosts[2], self.net.hosts[3]]
                    # h5, h6
                    hostGroup2_1 = [self.net.hosts[4], self.net.hosts[5]]
                    # h7, h8
                    hostGroup2_2 = [self.net.hosts[6], self.net.hosts[7]]
                    # h9, h10, h11, h12
                    hostGroup3 = [self.net.hosts[8], self.net.hosts[9], self.net.hosts[10], self.net.hosts[11]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 2 --switchId 2')
                        if  host  in hostGroup1_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 2 --switchId 1')
                        elif host in hostGroup2_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 2 --switchId 3')
                        elif host in hostGroup2_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 2 --switchId 5')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 4 --switchId 4')

                elif(TOPO_VERSION == TOPO0316):
                    print("TOPO_VERSION == TOPO0316")
                    # h1, h2, h3
                    hostGroup1_1 = [self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2]]
                    # h4, h5
                    hostGroup1_2 = [self.net.hosts[3],  self.net.hosts[4] ]
                    # h6, h7, h8
                    hostGroup2_1 = [self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7]]
                    # h9, h10
                    hostGroup2_2 = [self.net.hosts[8],  self.net.hosts[9] ]
                    # h11, h12
                    hostGroup3_1 = [self.net.hosts[10], self.net.hosts[11]]
                    # h13, h14, h15
                    hostGroup3_2 = [self.net.hosts[12], self.net.hosts[13], self.net.hosts[14]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 3 --switchId 2')
                        elif host in hostGroup1_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 2 --switchId 1')
                        if  host  in hostGroup2_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 3 --switchId 3')
                        elif host in hostGroup2_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 2 --switchId 5')
                        elif host in hostGroup3_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 2 --switchId 4')
                        elif host in hostGroup3_2: # NOTE: FIXME:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 3 --switchId 0')

                elif(TOPO_VERSION == TOPO0319):
                    print("TOPO_VERSION == TOPO0319")
                    # h1, h2, h3
                    hostGroup1_1 = [self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2]]
                    # h4, h5, h6
                    hostGroup1_2 = [self.net.hosts[3],  self.net.hosts[4] , self.net.hosts[5]]
                    # h7, h8, h9
                    hostGroup2_1 = [self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8]]
                    # h10, h11, h12
                    hostGroup2_2 = [self.net.hosts[9],  self.net.hosts[10], self.net.hosts[11]]
                    # h13, h14, h15, h16, h17
                    hostGroup3_1 = [self.net.hosts[12], self.net.hosts[13], self.net.hosts[14], self.net.hosts[15], self.net.hosts[16]]
                    # h18
                    hostGroup3_2 = [self.net.hosts[17]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 3 --switchId 2')
                        elif  host  in hostGroup1_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 3 --switchId 1')
                        elif host in hostGroup2_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 3 --switchId 3')
                        elif host in hostGroup2_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 3 --switchId 5')
                        elif host in hostGroup3_1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 5 --switchId 4')
                        elif host in hostGroup3_2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 1 --switchId 0')

            elif (TEST_MODE == SWTICHML or TEST_MODE == ATP):
                if(TEST_MODE == SWTICHML):
                    print("TEST_MODE == SWTICHML")
                elif(TEST_MODE == ATP):
                    print("TEST_MODE == ATP")

                if(TOPO_VERSION == DEMOV4):
                    print("TOPO_VERSION == DEMOV4")
                    hostGroup1 = [self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4],  self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7]]
                    hostGroup2 = [self.net.hosts[8],  self.net.hosts[9],  self.net.hosts[10], self.net.hosts[11], self.net.hosts[12], self.net.hosts[13], self.net.hosts[14], self.net.hosts[15]]
                    hostGroup3 = [self.net.hosts[16], self.net.hosts[17], self.net.hosts[18], self.net.hosts[19], self.net.hosts[20], self.net.hosts[21], self.net.hosts[22], self.net.hosts[23]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 8 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 8 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.9.1 --degree 8 --switchId 4')
                
                elif(TOPO_VERSION == TOPO07):
                    print("TOPO_VERSION == TOPO07")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2]]
                    hostGroup2 = [self.net.hosts[3], self.net.hosts[4], self.net.hosts[5]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.4.1 --degree 3 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.4.1 --degree 3 --switchId 3')

                elif(TOPO_VERSION == TOPO09):
                    print("TOPO_VERSION == TOPO09")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2], self.net.hosts[3]]
                    hostGroup2 = [self.net.hosts[4], self.net.hosts[5], self.net.hosts[6], self.net.hosts[7]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.5.1 --degree 4 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.5.1 --degree 4 --switchId 3')
                
                elif(TOPO_VERSION == TOPO11):
                    print("TOPO_VERSION == TOPO11")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2], self.net.hosts[3], self.net.hosts[4]]
                    hostGroup2 = [self.net.hosts[5], self.net.hosts[6], self.net.hosts[7], self.net.hosts[8], self.net.hosts[9]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.6.1 --degree 5 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.6.1 --degree 5 --switchId 3')

                elif(TOPO_VERSION == TOPO13):
                    print("TOPO_VERSION == TOPO13")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2], self.net.hosts[3], self.net.hosts[4], self.net.hosts[5]]
                    hostGroup2 = [self.net.hosts[6], self.net.hosts[7], self.net.hosts[8], self.net.hosts[9], self.net.hosts[10],self.net.hosts[11]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.7.1 --degree 6 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.7.1 --degree 6 --switchId 3')

                elif(TOPO_VERSION == TOPO15):
                    print("TOPO_VERSION == TOPO15")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2], self.net.hosts[3],  self.net.hosts[4],  self.net.hosts[5],  self.net.hosts[6]]
                    hostGroup2 = [self.net.hosts[7], self.net.hosts[8], self.net.hosts[9], self.net.hosts[10], self.net.hosts[11], self.net.hosts[12], self.net.hosts[13]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.8.1 --degree 7 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.2.8.1 --degree 7 --switchId 3')

                elif(TOPO_VERSION == TOPO0307):
                    print("TOPO_VERSION == TOPO0307")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1]]
                    hostGroup2 = [self.net.hosts[2], self.net.hosts[3]]
                    hostGroup3 = [self.net.hosts[4], self.net.hosts[5]]
                    for host in self.net.hosts:
                        if host in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.3.1 --degree 2 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.3.1 --degree 2 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.3.1 --degree 2 --switchId 4')

                elif(TOPO_VERSION == TOPO0310):
                    print("TOPO_VERSION == TOPO0310")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2]]
                    hostGroup2 = [self.net.hosts[3], self.net.hosts[4], self.net.hosts[5]]
                    hostGroup3 = [self.net.hosts[6], self.net.hosts[7], self.net.hosts[8]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.4.1 --degree 3 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.4.1 --degree 3 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.4.1 --degree 3 --switchId 4')

                elif(TOPO_VERSION == TOPO0313):
                    print("TOPO_VERSION == TOPO0313")
                    hostGroup1 = [self.net.hosts[0], self.net.hosts[1], self.net.hosts[2],  self.net.hosts[3] ]
                    hostGroup2 = [self.net.hosts[4], self.net.hosts[5], self.net.hosts[6],  self.net.hosts[7] ]
                    hostGroup3 = [self.net.hosts[8], self.net.hosts[9], self.net.hosts[10], self.net.hosts[11]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 4 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 4 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.5.1 --degree 4 --switchId 4')

                elif(TOPO_VERSION == TOPO0316):
                    print("TOPO_VERSION == TOPO0316")
                    hostGroup1 = [self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4] ]
                    hostGroup2 = [self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9] ]
                    hostGroup3 = [self.net.hosts[10], self.net.hosts[11], self.net.hosts[12], self.net.hosts[13], self.net.hosts[14]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 5 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 5 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.6.1 --degree 5 --switchId 4')

                elif(TOPO_VERSION == TOPO0319):
                    print("TOPO_VERSION == TOPO0319")
                    hostGroup1 = [self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4] , self.net.hosts[5] ]
                    hostGroup2 = [self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9],  self.net.hosts[10], self.net.hosts[11]]
                    hostGroup3 = [self.net.hosts[12], self.net.hosts[13], self.net.hosts[14], self.net.hosts[15], self.net.hosts[16], self.net.hosts[17]]
                    for host in self.net.hosts:
                        if  host  in hostGroup1:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 6 --switchId 2')
                        elif host in hostGroup2:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 6 --switchId 3')
                        elif host in hostGroup3:
                            popens[host] = host.popen('python3 ./host/send.py 10.3.7.1 --degree 6 --switchId 4')

        elif(SEND_MODE == TCPREPLAY):
            PS = self.net.hosts[PS_INDEX]
            PS.cmd("python3 ./host/receive.py" + " &")
            print("SEND_MODE == TCPREPLAY")
            sleep(5) # DEBUG:
            if(TOPO_VERSION == DEMOV4):
                print("TOPO_VERSION == DEMOV4")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4],  self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7],
                    self.net.hosts[8],  self.net.hosts[9],  self.net.hosts[10], self.net.hosts[11], self.net.hosts[12], self.net.hosts[13], self.net.hosts[14], self.net.hosts[15],
                    self.net.hosts[16], self.net.hosts[17], self.net.hosts[18], self.net.hosts[19], self.net.hosts[20], self.net.hosts[21], self.net.hosts[22], self.net.hosts[23]
                ]
            if(TOPO_VERSION == TOPO07):
                print("TOPO_VERSION == TOPO07")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],
                    self.net.hosts[3],  self.net.hosts[4],  self.net.hosts[5]
                ]
            elif(TOPO_VERSION == TOPO09):
                print("TOPO_VERSION == TOPO09")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],
                    self.net.hosts[4],  self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7]
                ]
            elif(TOPO_VERSION == TOPO11):
                print("TOPO_VERSION == TOPO11")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4],
                    self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9]
                ]
            elif(TOPO_VERSION == TOPO13):
                print("TOPO_VERSION == TOPO13")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3], self.net.hosts[4],   self.net.hosts[5],
                    self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9], self.net.hosts[10],  self.net.hosts[11],
                ]
            elif(TOPO_VERSION == TOPO15):
                print("TOPO_VERSION == TOPO15")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],   self.net.hosts[4],   self.net.hosts[5], self.net.hosts[6],  
                    self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9],  self.net.hosts[10],  self.net.hosts[11],  self.net.hosts[12], self.net.hosts[13]
                ]
            elif(TOPO_VERSION == TOPO0307):
                print("TOPO_VERSION == TOPO0307")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],
                    self.net.hosts[2],  self.net.hosts[3],
                    self.net.hosts[4],  self.net.hosts[5]
                ]
            elif(TOPO_VERSION == TOPO0310):
                print("TOPO_VERSION == TOPO0310")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],
                    self.net.hosts[3],  self.net.hosts[4],  self.net.hosts[5],
                    self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8]
                ]
            elif(TOPO_VERSION == TOPO0313):
                print("TOPO_VERSION == TOPO0313")
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],
                    self.net.hosts[4],  self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7],
                    self.net.hosts[8],  self.net.hosts[9],  self.net.hosts[10], self.net.hosts[11]
                ]
            elif(TOPO_VERSION == TOPO0316):
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4],
                    self.net.hosts[5],  self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9],
                    self.net.hosts[10], self.net.hosts[11], self.net.hosts[12], self.net.hosts[13], self.net.hosts[14]
                ]
            elif(TOPO_VERSION == TOPO0319):
                hostGroup = [
                    self.net.hosts[0],  self.net.hosts[1],  self.net.hosts[2],  self.net.hosts[3],  self.net.hosts[4],  self.net.hosts[5],
                    self.net.hosts[6],  self.net.hosts[7],  self.net.hosts[8],  self.net.hosts[9],  self.net.hosts[10], self.net.hosts[11],
                    self.net.hosts[12], self.net.hosts[13], self.net.hosts[14], self.net.hosts[15], self.net.hosts[16], self.net.hosts[17]
                ]

            workdir = os.getcwd()
            replayPcapDir = os.path.join(workdir, REPLAY_PCAP_DIR)
            for host in hostGroup:
                cmd = 'tcpreplay -i eth0 -M' + ' ' + str(REPLAY_SPEED) + ' ' + (replayPcapDir+REPLAY_PCAP_PREFIX+host.name+'.pcap')
                popens[host] = host.popen(cmd)

        elif(SEND_MODE == MININET_CLI):
            self.do_net_cli()
        
        endTime = time() + AGGRE_MONITOR_TIME
        
        # 对输出进行检测
        # logDir = os.path.join(workdir, AGGRE_MONITOR_LOG)
        # with open(logDir, 'w') as file:
        for host, _ in pmonitor( popens, timeoutms=500 ): # _ -> line
            # DEBUG: 
            # if host in hostGroup1:
            #     aggreNum = 1
            # elif host in hostGroup2:
            #     aggreNum = 2
            # elif host in hostGroup3:
            #     aggreNum = 3
            
            # if host:
            #     file.write( '[aggre-%s]<%s>: %s' % ( str(a    ggreNum), host.name, line ) )
            if time() >= endTime:
                for switchProcess in popens.values():
                    switchProcess.send_signal( SIGINT )

        sleep(20)   # DEBUG: 
        # self.do_net_cli()

        # stop right after the CLI is exited
        self.net.stop()


    def parse_links(self, unparsed_links):
        """ Given a list of links descriptions of the form [node1, node2, latency, bandwidth]
            with the latency and bandwidth being optional, parses these descriptions
            into dictionaries and store them as self.links
        """
        links = []
        for link in unparsed_links:
            # make sure each link's endpoints are ordered alphabetically
            s, t, = link[0], link[1]
            if s > t:
                s,t = t,s

            link_dict = {'node1':s,
                        'node2':t,
                        'latency':'0ms',
                        'bandwidth':None
                        }
            if len(link) > 2:
                link_dict['latency'] = self.format_latency(link[2])
            if len(link) > 3:
                link_dict['bandwidth'] = link[3]

            if link_dict['node1'][0] == 'h':
                assert link_dict['node2'][0] == 's', 'Hosts should be connected to switches, not ' + str(link_dict['node2'])
            links.append(link_dict)
        return links


    def create_network(self):
        """ Create the mininet network object, and store it as self.net.

            Side effects:
                - Mininet topology instance stored as self.topo
                - Mininet instance stored as self.net
        """
        self.logger("Building mininet topology.")

        defaultSwitchClass = configureP4Switch(
                                sw_path=self.bmv2_exe,
                                json_path=self.switch_json,
                                log_console=True,
                                pcap_dump=self.pcap_dir)

        self.topo = ExerciseTopo(self.hosts, self.switches, self.links, self.log_dir, self.bmv2_exe, self.pcap_dir)

        self.net = Mininet(topo = self.topo,
                      link = TCLink,
                      host = P4Host,
                      switch = defaultSwitchClass,
                      controller = None)

    def program_switch_p4runtime(self, sw_name, sw_dict):
        """ This method will use P4Runtime to program the switch using the
            content of the runtime JSON file as input.
        """
        sw_obj = self.net.get(sw_name)
        grpc_port = sw_obj.grpc_port
        device_id = sw_obj.device_id
        runtime_json = sw_dict['runtime_json']
        self.logger('Configuring switch %s using P4Runtime with file %s' % (sw_name, runtime_json))
        with open(runtime_json, 'r') as sw_conf_file:
            outfile = '%s/%s-p4runtime-requests.txt' %(self.log_dir, sw_name)
            p4runtime_lib.simple_controller.program_switch(
                addr='127.0.0.1:%d' % grpc_port,
                device_id=device_id,
                sw_conf_file=sw_conf_file,
                workdir=os.getcwd(),
                proto_dump_fpath=outfile)

    def program_switch_cli(self, sw_name, sw_dict):
        """ This method will start up the CLI and use the contents of the
            command files as input.
        """
        cli = 'simple_switch_CLI'
        # get the port for this particular switch's thrift server
        sw_obj = self.net.get(sw_name)
        thrift_port = sw_obj.thrift_port

        cli_input_commands = sw_dict['cli_input']
        self.logger('Configuring switch %s with file %s' % (sw_name, cli_input_commands))
        with open(cli_input_commands, 'r') as fin:
            cli_outfile = '%s/%s_cli_output.log'%(self.log_dir, sw_name)
            with open(cli_outfile, 'w') as fout:
                subprocess.Popen([cli, '--thrift-port', str(thrift_port)],
                                 stdin=fin, stdout=fout)

    def program_switches(self):
        """ This method will program each switch using the BMv2 CLI and/or
            P4Runtime, depending if any command or runtime JSON files were
            provided for the switches.
        """
        for sw_name, sw_dict in self.switches.items():
            if 'cli_input' in sw_dict:
                self.program_switch_cli(sw_name, sw_dict)
            if 'runtime_json' in sw_dict:
                self.program_switch_p4runtime(sw_name, sw_dict)

    def program_hosts(self):
        """ Execute any commands provided in the topology.json file on each Mininet host
        """
        for host_name, host_info in list(self.hosts.items()):
            h = self.net.get(host_name)
            if "commands" in host_info:
                for cmd in host_info["commands"]:
                    h.cmd(cmd)


    def  do_net_cli(self):
        """ Starts up the mininet CLI and prints some helpful output.

            Assumes:
                - A mininet instance is stored as self.net and self.net.start() has
                  been called.
        """
        for s in self.net.switches:
            s.describe()
        for h in self.net.hosts:
            h.describe()
        self.logger("Starting mininet CLI")
        # Generate a message that will be printed by the Mininet CLI to make
        # interacting with the simple switch a little easier.
        print('')
        print('======================================================================')
        print('Welcome to the BMV2 Mininet CLI!')
        print('======================================================================')
        print('Your P4 program is installed into the BMV2 software switch')
        print('and your initial runtime configuration is loaded. You can interact')
        print('with the network using the mininet CLI below.')
        print('')
        if self.switch_json:
            print('To inspect or change the switch configuration, connect to')
            print('its CLI from your host operating system using this command:')
            print('  simple_switch_CLI --thrift-port <switch thrift port>')
            print('')
        print('To view a switch log, run this command from your host OS:')
        print('  tail -f %s/<switchname>.log' %  self.log_dir)
        print('')
        print('To view the switch output pcap, check the pcap files in %s:' % self.pcap_dir)
        print(' for example run:  sudo tcpdump -xxx -r s1-eth1.pcap')
        print('')
        if 'grpc' in self.bmv2_exe:
            print('To view the P4Runtime requests sent to the switch, check the')
            print('corresponding txt file in %s:' % self.log_dir)
            print(' for example run:  cat %s/s1-p4runtime-requests.txt' % self.log_dir)
            print('')

        CLI(self.net)


def get_args():
    cwd = os.getcwd()
    default_logs = os.path.join(cwd, 'logs')
    default_pcaps = os.path.join(cwd, 'pcaps')
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', help='Suppress log messages.',
                        action='store_true', required=False, default=False)
    parser.add_argument('-t', '--topo', help='Path to topology json',
                        type=str, required=False, default='./topology.json')
    parser.add_argument('-l', '--log-dir', type=str, required=False, default=default_logs)
    parser.add_argument('-p', '--pcap-dir', type=str, required=False, default=default_pcaps)
    parser.add_argument('-j', '--switch_json', type=str, required=False)
    parser.add_argument('-b', '--behavioral-exe', help='Path to behavioral executable',
                                type=str, required=False, default='simple_switch')
    return parser.parse_args()


if __name__ == '__main__':
    # from mininet.log import setLogLevel
    setLogLevel("info")

    args = get_args()
    exercise = ExerciseRunner(args.topo, args.log_dir, args.pcap_dir,
                              args.switch_json, args.behavioral_exe, args.quiet)

    exercise.run_exercise()

