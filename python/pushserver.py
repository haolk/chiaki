import time
import zmq

def producer():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://127.0.0.1:5557")

    print('listening')
    
    while True:
        zmq_socket.send_string("hello")
        time.sleep(1)

producer()