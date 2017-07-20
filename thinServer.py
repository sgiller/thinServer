from flask import *
import socket, select, string, sys, time, json
from threading import Thread

app = Flask(__name__)

def start():
    host = '0.0.0.0'
    port = 50001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(3)
    while True:
        c, addr = s.accept()
        print("Connection from : " + str(addr))

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    tserver = Thread(target=start)
    tserver.daemon = True
    tserver.start()
    tflask = Thread(target=app.run)
    tflask.daemon = True
    tflask.start()
    while True:
        time.sleep(2)
        message = input("Type Exit to end server!")
        if message == 'Exit':
            sys.exit()

