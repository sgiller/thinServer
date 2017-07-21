from flask import *
import socket, select, string, sys, time, json
from threading import Thread

i = 0
j = 0
ipdict = []
hostnamedict = []
alivedict = []
connections = []
datedict = []
procdict = []
fullclient = []
fullpackage = []
aktuelleVersion = 3.0
aktuellupdate = "Update 3"
aktuellepruefsumme = "ghi"
aktuellLink = "www.ichdownloadeupdate.de"
aktuellCommand = "tarxyz"
needupdate = []
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html', fullclient=fullclient)
@app.route('/updates')
def updates():
    return render_template('updates.html', fullpackage=fullpackage, fullclient=fullclient)
@app.route('/availUpdates')
def availupdates():
    return render_template('availUpdates.html')

def start():
    print("server gestartet")
    host = '0.0.0.0'
    port = 50001
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(3)
    while True:
        c, addr = s.accept()
        if c in connections:
            print("schon in liste")
        else:
            connections.append(c)
            print(addr)
            needupdate.append(False)
            connections.append(c)
            global j
            global i
            j = i
            i  = i+1
            print("Connection from : " + str(addr))
            thread_ = Thread(target = getInfo, args=(c, addr, j))
            thread_.daemon = True
            thread_.start()

def getInfo(c, addr, j):
    data = c.recv(1024)
    new = str(data)
    new = str(new).split("'")
    hostname = new[3]
    ip = new[7]
    alive = str(new[11])
    date = new[15]
    proc = new[19]
    system = new[23]
    ram = new[27]
    fullclient.append([ip, hostname, system, alive, date, proc, ram])
    print("Client:" + str(fullclient))
    data = c.recv(1024)
    data = bytes(data).decode(encoding='UTF-8')
    print(data)
    new_ = str(data)
    new_ = new_.split("'")
    updatename = new_[1]
    updateversion = new_[3]
    pruefsumme = new_[5]
    link = new_[7]
    command = new_[9]
    fullpackage.append([updatename, updateversion, pruefsumme, link, command])
    if (str(updateversion) != aktuelleVersion):
        needupdate[j] = True
        c.send("Das System ist nicht auf dem neusten Stand es wird ein Update empfohlen! antworten sie mit ja um das Update automatisch zu installieren".encode())
        data = c.recv(1024)
        data = bytes(data).decode(encoding='UTF-8')
        if (str(data) == "ja"):
             pass
        print(data)
        versionstext = ("{'"+str(aktuellupdate)+"', '"+str(aktuelleVersion)+"', '"+str(aktuellepruefsumme)+"', '"+str(aktuellLink)+"', '"+str(aktuellCommand)+"'}")
        c.send(versionstext.encode())
        print("Package:"+ str(fullpackage))

    while True:
        data = c.recv(1024)
        if not data:
            print("Client: " + str(addr[1]) + " hat die Verbindung unterbrochen")
            fullclient[j][3] = "notAlive"
            break
        else:
            data = bytes(data).decode(encoding='UTF-8')
            print(data)
            new_ = str(data)
            new_ = new_.split("'")
            updatename = new_[1]
            updateversion = new_[3]
            pruefsumme = new_[5]
            link = new_[7]
            command = new_[9]
            fullpackage[j][0] = updatename
            fullpackage[j][1] = updateversion
            fullpackage[j][2] = pruefsumme
            fullpackage[j][3] = link
            fullpackage[j][4] = command
    c.close()

if __name__ == '__main__':
    tserver = Thread(target = start)
    tserver.daemon = True
    tserver.start()
    tflask = Thread(target = app.run)
    tflask.daemon = True
    tflask.start()
    while True:
        time.sleep(2)