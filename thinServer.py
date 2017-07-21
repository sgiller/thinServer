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
fullpackage = []

app = Flask(__name__)

def getInfo(c, addr, j):
    while True:
        data = c.recv(1024)
        if not data:
           print("Client: " + str(addr[1]) + " hat die Verbindung unterbrochen")
           fullclient[j][3] = "notAlive"
           break
        data = bytes(data).decode(encoding='UTF-8')
        print(data)
        if str(data).find("Update") != -1:
            new_ = str(data)
            new_ = new_.split("'")
            updatename = new_[1]
            updateversion = new_[3]
            pruefsumme = new_[5]
            link = new_[7]
            command = new_[9]
            fullpackage.append([updatename, updateversion, pruefsumme, link, command])
            print("Package:"+ str(fullpackage))
            continue

        if str(data).find("Hostname") != 1:
            new = str(data)
            new = str(new).split("'")
            print("Hier kommt irgendwo der Fehler!"+str(new))
            hostname = new[3]
            ip = new[7]
            alive = str(new[11])
            date = new[15]
            proc = new[19]
            system = new[23]
            ram = new[27]
            fullclient.append([ip, hostname, system, alive, date, proc, ram])
            print("Client:"+str(fullclient))
            continue

def start():
    print("server gestartet")
    host = '0.0.0.0'
    port = 50000
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
        thread_ = Thread(target = getInfo, args=(c, addr, j))
        thread_.daemon = True
        thread_.start()
        client_info.append([str(addr)])

@app.route('/')
def hello_world():
    return render_template('index.html', fullclient=fullclient)
@app.route('/updates')
def updates():
    return render_template('updates.html', fullpackage=fullpackage, fullclient=fullclient)

if __name__ == '__main__':
    tserver = Thread(target = start)
    tserver.daemon = True
    tserver.start()
    tflask = Thread(target = app.run)
    tflask.daemon = True
    tflask.start()
    while True:
        pass