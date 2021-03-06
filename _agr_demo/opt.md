# How to restruct the project
1. File naming consistency: foldername,  *.p4, p4info in sX-runtime.json, bmv2_json...
2. ......
## How to run the project
### Demov1
> not support anymore.

Makefile:
```
TOPO = pod-topo/topologyv1.json
```
CLI: 
```bash
make run
...
mininet> h3 python3 ./host/receive.py > ./logs/receiver.log &
(new terminal) tail -f ./logs/receiver.log
mininet> h1 python3 ./host/send.py h3 --degree 2 &
mininet> h2 python3 ./host/send.py h3 --degree 2 &
mininet> exit
...
make stop & make clean
...
```

### Demov2
> not support anymore.

Makefile:
```
TOPO = pod-topo/topologyv2.json
```
CLI: 
```bash
make run
...
mininet> h4 python3 ./host/receive.py > ./logs/receiver.log &
(new terminal) tail -f ./logs/receiver.log
mininet> h1 python3 ./host/send.py h4 --degree 3 &
mininet> h2 python3 ./host/send.py h4 --degree 3 &
mininet> h3 python3 ./host/send.py h4 --degree 3 &
mininet> exit
...
make stop & make clean
...
```

### Demov3

**Example:**

Makefile:
```
TOPO = pod-topo/topologyv3.json
```
CLI: 
```bash
make run
...
mininet> h9 python3 ./host/receive.py > ./logs/receiver.log &
(new terminal) tail -f ./logs/receiver.log
mininet> h1 python3 ./host/send.py h9 --degree 3 --switchId 1 # switchId 4, 3 is okay.
mininet> h2 python3 ./host/send.py h9 --degree 3 --switchId 1
mininet> h3 python3 ./host/send.py h9 --degree 3 --switchId 1

mininet> h4 python3 ./host/send.py h9 --degree 3 --switchId 2 # switchId 4, 3 is okay.
mininet> h5 python3 ./host/send.py h9 --degree 3 --switchId 2
mininet> h6 python3 ./host/send.py h9 --degree 3 --switchId 2

mininet> h7 python3 ./host/send.py h9 --degree 2 --switchId 3 # switchId 4 is okay.
mininet> h8 python3 ./host/send.py h9 --degree 2 --switchId 3
mininet> exit
...
make stop & make clean
...
```


### Demov4

**Example:**

Makefile:
```
TOPO = pod-topo/topologyv4.json
```
CLI: 
```bash
make run
...
# hX -> s1 -> PS
mininet> h25 python3 ./host/receive.py > ./logs/receiver.log &
(new terminal) tail -f ./logs/receiver.log
mininet> h1  python3 ./host/send.py h25 --degree 7 --switchId 1
mininet> h5  python3 ./host/send.py h25 --degree 7 --switchId 1
mininet> h8  python3 ./host/send.py h25 --degree 7 --switchId 1
mininet> h13 python3 ./host/send.py h25 --degree 7 --switchId 1
mininet> h16 python3 ./host/send.py h25 --degree 7 --switchId 1
mininet> h19 python3 ./host/send.py h25 --degree 7 --switchId 1
mininet> h24 python3 ./host/send.py h25 --degree 7 --switchId 1
# hX -> s2 -> PS
mininet> h4  python3 ./host/send.py h25 --degree 6 --switchId 2
mininet> h7  python3 ./host/send.py h25 --degree 6 --switchId 2
mininet> h12 python3 ./host/send.py h25 --degree 6 --switchId 2
mininet> h15 python3 ./host/send.py h25 --degree 6 --switchId 2
mininet> h18 python3 ./host/send.py h25 --degree 6 --switchId 2
mininet> h23 python3 ./host/send.py h25 --degree 6 --switchId 2
# hX -> s3 -> PS
mininet> h2  python3 ./host/send.py h25 --degree 6 --switchId 3
mininet> h11 python3 ./host/send.py h25 --degree 6 --switchId 3
mininet> h14 python3 ./host/send.py h25 --degree 6 --switchId 3
mininet> h17 python3 ./host/send.py h25 --degree 6 --switchId 3
mininet> h20 python3 ./host/send.py h25 --degree 6 --switchId 3
mininet> h22 python3 ./host/send.py h25 --degree 6 --switchId 3
# hX -> s4 -> PS
mininet> h3  python3 ./host/send.py h25 --degree 3 --switchId 4
mininet> h6  python3 ./host/send.py h25 --degree 3 --switchId 4
mininet> h9  python3 ./host/send.py h25 --degree 3 --switchId 4
# hX -> PS
mininet> h10  python3 ./host/send.py h25 --degree 2 --switchId 0
mininet> h21  python3 ./host/send.py h25 --degree 2 --switchId 0
m
mininet> exit
...
make stop & make clean
...
```

## How to add feature
1. hosts(include client and server) have mechanism to support the new feature.
1. the P4 program have mechanism to support the new feature.

**Current capability:**
Multi hosts' value agregation on any switches which is on the way to the destination.