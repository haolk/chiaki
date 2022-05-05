import zmq
from time import sleep

fcontext = zmq.Context()
fsocket = fcontext.socket(zmq.REP)
fsocket.bind("tcp://127.0.0.1:5555")

while True:
    print("listen")
    msg = fsocket.recv()
    print(msg)
    fsocket.send_string('0')
 