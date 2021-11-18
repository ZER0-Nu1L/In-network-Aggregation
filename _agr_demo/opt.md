### Demov1

```bash
make run
...
mininet> h3 python3 ./host/receive.py > ./logs/receiver.log &
(new terminal) tail -f ./logs/receiver.log
mininet> h1 python3 ./host/send.py h3 --degree 2 --value 2 &
mininet> h2 python3 ./host/send.py h3 --degree 2 --value 3 &
...
mininet> exit
...
make stop & make clean
...
```