# In-network-Aggregation
# 🔝 使用方法

## 测试通用设置

`./utils/config.py`中：

```python
# Control plane
READTABLE_TIME = 2
READ_TIME = 60 * 150

# host monitor
AGGRE_MONITOR_TIME = 60 * 150

# PS as receiver
RECEIVER_LOG = 'logs/receiver.log'

```

- `READTABLE_TIME`表示控制平面读取数据平面`ingressCounter`和`egressCounter`的频率（监测聚合情况）；

- `READ_TIME`表示读取持续时长；

- `AGGRE_MONITOR_TIME`表示mininet下多台主机并发执行预设命令的输出监测持续时间；一般会设置与`READ_TIME`相同的时长。

`_agr_demo/host.py`中

```python
# Number of packages
PKTNUM = 1000
ALLOW_LOSS_RATE = 1

```

- `PKTNUM`表示测试的数据包量；

- `ALLOW_LOSS_RATE`表示测试时允许丢包率， PS收到这些之后就会停止首包，计算吞吐量；



## 测试模式

在`./utils/config.py`中`SEND_MODE`选定测试模式

- `GENERATOR_AND_SEND`，由mininet的每个主机自己生成包，然后发包进行测试。此方法会在测试工程中占用额外大量的CPU和内存（尤其是构造的数据包量大的时候）；

- `TCPREPLAY`，在发包测试前构建好数据包，然后用`tcpreplay`进行重放，且重放速率可控可调。

### 测试模式1：`GENERATOR_AND_SEND`

#### 1. 配置变更

**测试NGA前的配置变更**

- Makefile

```Verilog
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = pod-topo/topologyv4.json

include ../utils/Makefile

```

- utils/config.py

```python
TEST_MODE = OUR_SOLUTION
```

- _agr_demo/host/config.py

```PYTHON
PS_RECEIVE_FLOW = OUR_SOLUTION_FLOW
```

- _agr_demo.p4

```C++
action count_aggr_egress() {
    egressCounter.count((bit<32>) hdr.atp.sequenceId); // TODO: 没有完全懂 workerMap, sequenceId 0
    // hdr.atp.aggregationDegree = 3;  // NOTE: 适配ATP路由策略，对于仅仅聚合一次的路由策略没有太大影响
    // hdr.atp.switchId = 1;       // NOTE: 防止ATP路由策略下，回去的时候又重新聚合。
    // DEBUG:  NGS 和 SwitchML 不能用，ATP用，（尤其是 switchID）
}
```

**测试SwitchML****前的配置变更**

- Makefile

```Verilog
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = pod-topo/topologyv4-swtichML.json

include ../utils/Makefile

```

- utils/config.py

```python
TEST_MODE = SWTICHML
```

- _agr_demo/host/config.py

```PYTHON
PS_RECEIVE_FLOW = SWITCHML_FLOW
```

- _agr_demo.p4

```C++
action count_aggr_egress() {
    egressCounter.count((bit<32>) hdr.atp.sequenceId); // TODO: 没有完全懂 workerMap, sequenceId 0
    // hdr.atp.aggregationDegree = 3;  // NOTE: 适配ATP路由策略，对于仅仅聚合一次的路由策略没有太大影响
    // hdr.atp.switchId = 1;       // NOTE: 防止ATP路由策略下，回去的时候又重新聚合。
    // DEBUG:  NGS 和 SwitchML 不能用，ATP用，（尤其是 switchID）
}
```

**测试ATP****前的配置变更**

- Makefile

```Verilog
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = pod-topo/topologyv4-ATP.json

include ../utils/Makefile

```

- utils/config.py

```python
TEST_MODE = ATP
```

- _agr_demo/host/config.py

```PYTHON
PS_RECEIVE_FLOW = ATP_FLOW
```

- _agr_demo.p4

```C++
action count_aggr_egress() {
    egressCounter.count((bit<32>) hdr.atp.sequenceId); // TODO: 没有完全懂 workerMap, sequenceId 0
    hdr.atp.aggregationDegree = 3;  // NOTE: 适配ATP路由策略，对于仅仅聚合一次的路由策略没有太大影响
    hdr.atp.switchId = 1;       // NOTE: 防止ATP路由策略下，回去的时候又重新聚合。
    // DEBUG:  NGS 和 SwitchML 不能用，ATP用，（尤其是 switchID）
}
```

#### 2. 流量监控建议

四个窗口

```bash
make run
multitail -s 2 ./logs/*-inout.log
tail -f ./logs/receiver.log
htop
```



![p4@p4](https://markdown-img-zer0nu1l.oss-cn-beijing.aliyuncs.com/img/20211126082558.png)

### 测试模式2：`TCPREPLAY`

#### 1. 数据包构造

```bash
cd ./_agr_demo
mkdir ./mypcap 
```

在`_agr_demo/host/config.py`中

```python
# Number of packages
PKTNUM = 1000
ALLOW_LOSS_RATE = 1

# if(SEND_MODE == TCPREPLAY), configure:
REPLAY_PCAP_LOG = 'logs/write_pcap.log' 
REPLAY_PCAP_DIR = 'mypcap/1000/'
REPLAY_PCAP_PREFIX_NGA = 'param_NGA-'
REPLAY_PCAP_PREFIX_SWITCHML = 'param_switchML-'
REPLAY_PCAP_PREFIX_ATP = 'param_switchML-' # 共用
```

设置好包数量、重放包的目录、重放包的前缀名称，并创建目录

```bash
mkdir *REPLAY_PCAP_DIR*
```

> REPLAY_PCAP_DIR根据实际情况输入。我一直用的是`mypcap/PKTNUM/`，例如`'mypcap/1000/'`, `'mypcap/100000/'`。

然后执行：

```bash
sudo python host/writepcap.py # sudo 不可或缺

```

程序执行完，数据包就构建完了。

在`utils/config.py`中同步刚刚的设置：

```python
# if(SEND_MODE == TCPREPLAY), configure:
REPLAY_PCAP_DIR = 'mypcap/1000/'
REPLAY_PCAP_PREFIX_NGA = 'param_NGA-'
REPLAY_PCAP_PREFIX_SWITCHML = 'param_switchML-'
REPLAY_PCAP_PREFIX_ATP = 'param_switchML-' # 共用
```

#### 2. 配置变更

**测试NGA前的配置变更**

- Makefile

```Verilog
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = pod-topo/topologyv4.json

include ../utils/Makefile

```

- utils/config.py

```python
TEST_MODE = OUR_SOLUTION
REPLAY_PCAP_PREFIX = REPLAY_PCAP_PREFIX_NGA
REPLAY_SPEED = 0.01 # M
```

  > 这里指定了重放包以及重发速度。

- _agr_demo/host/condig.py

```PYTHON
PS_RECEIVE_FLOW = OUR_SOLUTION_FLOW
```

- _agr_demo.p4

```C++
action count_aggr_egress() {
    egressCounter.count((bit<32>) hdr.atp.sequenceId); // TODO: 没有完全懂 workerMap, sequenceId 0
    // hdr.atp.aggregationDegree = 3;  // NOTE: 适配ATP路由策略，对于仅仅聚合一次的路由策略没有太大影响
    // hdr.atp.switchId = 1;       // NOTE: 防止ATP路由策略下，回去的时候又重新聚合。
    // DEBUG:  NGS 和 SwitchML 不能用，ATP用，（尤其是 switchID）
}
```

**测试SwitchML****前的配置变更**

- Makefile

```Verilog
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = pod-topo/topologyv4-swtichML.json

include ../utils/Makefile

```

- utils/config.py

```python
TEST_MODE = SWTICHML
REPLAY_PCAP_PREFIX = REPLAY_PCAP_PREFIX_SWITCHML
REPLAY_SPEED = 0.01 # M
```

  > 这里指定了重放包以及重发速度。

- _agr_demo/host/condig.py

```PYTHON
PS_RECEIVE_FLOW = SWITCHML_FLOW
```

- _agr_demo.p4

```C++
action count_aggr_egress() {
    egressCounter.count((bit<32>) hdr.atp.sequenceId); // TODO: 没有完全懂 workerMap, sequenceId 0
    // hdr.atp.aggregationDegree = 3;  // NOTE: 适配ATP路由策略，对于仅仅聚合一次的路由策略没有太大影响
    // hdr.atp.switchId = 1;       // NOTE: 防止ATP路由策略下，回去的时候又重新聚合。
    // DEBUG:  NGS 和 SwitchML 不能用，ATP用，（尤其是 switchID）
}
```

**测试ATP****前的配置变更**

- Makefile

```Verilog
BMV2_SWITCH_EXE = simple_switch_grpc
TOPO = pod-topo/topologyv4-ATP.json

include ../utils/Makefile

```

- utils/config.py

```python
TEST_MODE = ATP
REPLAY_PCAP_PREFIX = REPLAY_PCAP_PREFIX_ATP
REPLAY_SPEED = 0.01 # M
```

  > 这里指定了重放包以及重发速度。

- _agr_demo/host/condig.py

```PYTHON
PS_RECEIVE_FLOW = ATP_FLOW
```

- _agr_demo.p4

```C++
action count_aggr_egress() {
    egressCounter.count((bit<32>) hdr.atp.sequenceId); // TODO: 没有完全懂 workerMap, sequenceId 0
    hdr.atp.aggregationDegree = 3;  // NOTE: 适配ATP路由策略，对于仅仅聚合一次的路由策略没有太大影响
    hdr.atp.switchId = 1;       // NOTE: 防止ATP路由策略下，回去的时候又重新聚合。
    // DEBUG:  NGS 和 SwitchML 不能用，ATP用，（尤其是 switchID）
}
```

#### 3. 流量监控建议

```bash
make run
multitail -s 2 ./logs/*-inout.log
tail -f ./logs/receiver.log
tail -f ./logs/aggregation.log

```

![](https://markdown-img-zer0nu1l.oss-cn-beijing.aliyuncs.com/img/20211202104721.png)