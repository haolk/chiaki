import time
import zmq

def consumer():

    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://127.0.0.1:5557")
    # send work

    print('connected')
    
    while True:
        print(consumer_receiver.recv())

consumer()