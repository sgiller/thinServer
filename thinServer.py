from flask import *
import socket, select, string, sys, time, json
from threading import Thread

i = 0
j = 0
client_info =[]
ipdict = []
hostnamedict = []
alivedict = []
datedict = []
procdict = []

app = Flask(__name__)

def sendInfo(c, addr, j):
    while True:
        data = c.recv(1024)
        if not data:
           print(j)
           print("Client: " + str(addr) + " hat die Verbindung unterbrochen")
           alivedict[j] = "NotAlive"
           print(alivedict)
           break
        print("From Connected user: " + str(data))
        new = json.dumps(str(data).replace("\\", ""))
        new = str(new[2:len(new) - 1])
        new = new.replace("\\", "")
        new = eval(new)
        new = str(new).split("'")
        #print(new)
        hostname = new[3]
        ip = new[7]
        alive = str(new[11])
        date = new[15]
        proc = new[19]

        #print("sending: " + str(data))
        ipdict.append(ip)
        hostnamedict.append(hostname)
        alivedict.append(alive)
        datedict.append(date)
        procdict.append(proc)
        print(ipdict)
        print(ipdict[0])
    c.close()

def start():
    print("gestartet")
    host = '0.0.0.0'
    port = 50001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(3)
    while True:
        c, addr = s.accept()
        global j
        global i
        j = i
        i  = i+1
        print("Connection from : " + str(addr))
        thread_ = Thread(target = sendInfo, args=(c, addr, j))
        thread_.daemon = True
        thread_.start()
        client_info.append([str(addr)])

@app.route('/')
def hello_world():
    return 'Hello world'
@app.route('/test')
def test():
    return render_template('index.html', c = client_info)

if __name__ == '__main__':
    tserver = Thread(target = start)
    tserver.daemon = True
    tserver.start()
    tflask = Thread(target = app.run)
    tflask.daemon = True
    tflask.start()
    while True:
        time.sleep(2)
        message = input("Type Exit to end server!")
        if message == 'Exit':
            sys.exit()