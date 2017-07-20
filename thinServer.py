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
fullclient = []

app = Flask(__name__)

def getInfo(c, addr, j):
    while True:
        data = c.recv(1024)
        if not data:
           print(j)
           print("Client: " + str(addr) + " hat die Verbindung unterbrochen")
           fullclient[j][2] = "notAlive"
           print(alivedict)
           break
        print("From Connected user: " + str(data))


        new = json.dumps(str(data).replace("\\", ""))
        new = str(new[2:len(new) - 1])
        new = new.replace("\\", "")
        new = eval(new)
        new = str(new).split("'")
        hostname = new[3]
        ip = new[7]
        alive = str(new[11])
        date = new[15]
        proc = new[19]
        system = new[23]
        ram = new[27]

        fullclient.append([ip, hostname, system, alive, date, proc, ram])
        print(fullclient)
    c.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def start():
    print("server gestartet")
    host = '0.0.0.0'
    port = 50000
    s.bind((host, port))
    s.listen(3)
    while True:
        c, addr = s.accept()
        global j
        global i
        j = i
        i  = i+1
        print("Connection from : " + str(addr))
        thread_ = Thread(target = getInfo, args=(c, addr, j))
        thread_.daemon = True
        thread_.start()
        tPackage = Thread(target= packageInfo, args=(c, addr, j))
        tPackage.daemon = True
        tPackage.start()
        client_info.append([str(addr)])

def packageInfo(c, addr, j):
    while True:
        data = c.recv(1024)
        if not data:
            print(j)
            print("Client: " + str(addr) + " hat die Verbindung unterbrochen")
            fullclient[j][2] = "notAlive"
            print(alivedict)
            break
        print("From Connected user: " + str(data))

@app.route('/')
def hello_world():
    return render_template('index.html', fullclient=fullclient)
@app.route('/updates')
def updates():
    return render_template('updates.html')

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
            s.close()
            sys.exit()