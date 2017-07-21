from flask import *
import socket, select, string, sys, time, json, os
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
aktuellLink = "127.0.0.1:5000/downloads/a"
aktuellCommand = "tarxyz"
needupdate = []
app = Flask(__name__)

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
    already = False;
    data = c.recv(1024)
    new = str(data)
    new = str(new).split("'")
    hostname = new[3]
    ip = addr[0]
    index = 0
    for x in fullclient:
        for y in x:
            if y == ip:
                print (index)
                fullclient[index][3] = "alive"
                already = True
                break
        if already :
            break
        index+=1

    alive = str(new[7])
    date = new[11]
    proc = new[15]
    system = str(new[19])
    ram = new[23]
    print(index)
    if (already == True):
        fullclient[index][0] = ip
        fullclient[index][1] = hostname
        fullclient[index][2] = system
        fullclient[index][4] = date
        fullclient[index][5] = proc
        fullclient[index][6] = ram
    else:
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
    if (str(updateversion) != str(aktuelleVersion)):
        needupdate[j] = True
        c.send("UPDATE! Das System ist nicht auf dem neusten Stand es wird ein Update automatisch installiert!".encode())
        versionstext = ("{'"+str(aktuellupdate)+"', '"+str(aktuelleVersion)+"', '"+str(aktuellepruefsumme)+"', '"+str(aktuellLink)+"', '"+str(aktuellCommand)+"'}")
        c.send(versionstext.encode())
        fullpackage[j][0] = aktuellupdate
        fullpackage[j][1] = aktuelleVersion
        fullpackage[j][2] = aktuellepruefsumme
        fullpackage[j][3] = aktuellLink
        fullpackage[j][4] = aktuellCommand
        print("Package:"+ str(fullpackage))
    if (str(updateversion) == str(aktuelleVersion)):
        needupdate[j] = False
        c.send("Das System ist bereits auf dem neusten Stand kein Update notwendig".encode())

    while True:
        data = c.recv(1024)
        if not data:
            print("Client: " + str(addr[1]) + " hat die Verbindung unterbrochen")
            fullclient[index][3] = "notAlive"
            break
        else:
            versionstext = ("{'" + str(aktuellupdate) + "', '" + str(aktuelleVersion) + "', '" + str(aktuellepruefsumme) + "', '" + str(aktuellLink) + "', '" + str(aktuellCommand) + "'} Wird installiert")
            c.send(versionstext.encode())
            fullpackage[j][0] = aktuellupdate
            fullpackage[j][1] = aktuelleVersion
            fullpackage[j][2] = aktuellepruefsumme
            fullpackage[j][3] = aktuellLink
            fullpackage[j][4] = aktuellCommand
    c.close()

@app.route('/')
def hello_world():
    return render_template('index.html', fullclient=fullclient)
@app.route('/updates')
def updates():
    return render_template('updates.html', fullpackage=fullpackage, fullclient=fullclient)
@app.route('/availUpdates')
def availupdates():
    return render_template('availUpdates.html')
@app.route('/downloads/<path:filename>')
def downloads(filename):
    file = filename+".zip"
    return send_from_directory('downloads',file)
@app.route('/download')
def download():
    return render_template('Download.html')

if __name__ == '__main__':
    tserver = Thread(target = start)
    tserver.daemon = True
    tserver.start()
    tflask = Thread(target = app.run)
    tflask.daemon = True
    tflask.start()
    while True:

        time.sleep(2)