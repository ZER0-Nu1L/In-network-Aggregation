# How to restruct the project
1. File naming consistency: foldername,  *.p4, p4info in sX-runtime.json, bmv2_json...
2. ......
## How to run the project
### Demov1
Makefile:
```
TOPO = pod-topo/topologyv1.json
```
CLI: 
```bash
make run
...
mininet> h3 python3 receive.py > ./logs/receiver.log &
mininet> h1 python3 send.py h3 --value 12 --degree 2
mininet> h2 python3 send.py h3 --value 3 --degree 2
mininet> exit
...
make stop & make clean
...
```

### Demov2
Makefile:
```
TOPO = pod-topo/topologyv2.json
```
CLI: 
```bash
make run
...
mininet> h4 python3 receive.py > ./logs/receiver.log &
mininet> h1 python3 send.py h4 --value 12 --degree 3
mininet> h2 python3 send.py h4 --value 3 --degree 3
mininet> h3 python3 send.py h4 --value 1 --degree 3
mininet> exit
...
make stop & make clean
...
```


## How to add feature
1. hosts(include client and server) have mechanism to support the new feature.
1. the P4 program have mechanism to support the new feature.

 current feature:
1. two hosts' value agregation 
    1. host send packet with `ShortField("value", 0)` feild in ATP header 
    1. P4 switch
        1. parse ATP header
        1. register `agrValueVector`
1. multi hosts' value agregation: one-hot encoding
    1. packet 
        1. aggregationDegree(5bits) feild in ATP header 
    1. hosts
        1. genarate these to two values(TODO: get from workers)
    2. P4 switch
        1. register `count_reg` for count aggregated worker's number.
        2. register `agrValueVector` for aggregation
