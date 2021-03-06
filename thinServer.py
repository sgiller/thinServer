# -*- coding: utf-8 -*-
from flask import *
import socket, time, os
from threading import Thread
i = 0
j = 0                       #i,j hilfvariablen um zu wissen der wievielte client in der Liste geändert werden muss
fullclient = []             #Liste aller Clients mit Informationen
fullpackage = []            #Liste aller Packete der Clients
aktuelleVersion = 3.0       #Aktuellste Version des Servers
aktuellupdate = "Update 3"  #Aktuellster Updatename des Servers
aktuellepruefsumme = "ghi"  #Prüfsumme Pakets
aktuellLink = "/downloads/update3" #Downloadlink des aktuellsten Packetes
fulltext ="{'Update 3', '3.0', 'ghi', '/downloads/update3', 'tarxyz'}"
aktuellCommand = "tarxyz"                   #Befehl zum entpacken des Packetes
needupdate = []                             #Liste um zu schauen welcher client ein Update benötigt
app = Flask(__name__)

def getTime():
    '''Hohlt sich die Aktuelle Uhrzeit'''
    date = time.strftime("%d.%m.%Y %H:%M:%S")
    return str(date)

#Server wird gestartet
def start():
    print("server gestartet")
    host = '0.0.0.0'                        #host
    port = 50000                            #port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    print("Warte auf Verbindung eines Clienten")
    s.listen(3)
    while True:
        c, addr = s.accept()        #verbindungsinformationen in c und ip+port in addr
        needupdate.append(False)
        global j                    #Hilfsvariable (counter für Clienten)
        global i                    #Ebenfalls
        j = i                       #j wird gleich i gesetzt um die aktuelle clientid in j zu speichern
        i  = i+1                    #i wird um 1 erhöht damit sich die nächste id um 1 erhöht.
        print("Connection from : " + str(addr))         #ip des neu verbundenen Clienten
        thread_ = Thread(target = getInfo, args=(c, addr, j))       #Thread mit adresse counter und connection wird gestartet
        thread_.daemon = True                                       #um sich die Pc informationen und Paketinformationen zu hohlen
        thread_.start()

#Schickt alle 10 Sekunden aktuelles Update an den Clienten
def updateThread(c, j, ip, index):
    while True:
        time.sleep(10)
        print("aktuellstes Update:")
        versionstext = "{'" + str(aktuellupdate) + "', '" + str(aktuelleVersion) + "', '" + str(aktuellepruefsumme) + "', '" + str(aktuellLink) + "', '" + str(aktuellCommand) + "'}"
        print(versionstext)
        c.send(versionstext.encode())
        data = c.recv(1024)
        data = bytes(data).decode(encoding='UTF-8')
        if not data:
            print("Client: " + str(ip) + " hat die Verbindung unterbrochen")
            fullclient[index][3] = "notAlive"                                   #bricht die Verbindung zu einem Clienten ab wird der entsprechende wert of notAlive gesetzt
            break
        print("folgendes update ist auf dem Clienten installiert")
        print(data)
        new_ = str(data)
        checktext = new_
        new_ = new_.split("'")  # Informationen werden in das richtige Format gebracht
        updatename = new_[1]
        updateversion = new_[3]    #und in Variablen zwischengespeichert.
        pruefsumme = new_[5]
        link = new_[7]
        command = new_[9]
        print("Paketinformationen werden aktualisiert")
        if checktext != fulltext:
            fullpackage.append([ip, getTime(), updatename, updateversion,pruefsumme, link, command])
        else:
            pass
    c.close()               #entsprechender Sockel wird geschlossen

#hier gehts rein wenn client erfolgreich connected ist--> Daten werden vom Clienten geholt und in den entsprechenden listen gespeichert.
def getInfo(c, addr, j):
    k = j
    already = False;                #boolean um zu testen ob Client bereits in den Verbindungen auftaucht
    data = c.recv(1024)             #wartet auf daten des Clienten
    new = str(data)
    new = str(new).split("'")
    hostname = new[3]
    ip = addr[0]
    index = 0                       #counter für Listeneintrag
    for x in fullclient:            #in dieser for loop wird überprüft ob die ip sich bereits verbunden hatte, dann werden die entsprechenden Listeneinträge
        for y in x:                 #geändert und nicht appendet.
            if y == ip:
                fullclient[index][3] = "alive"
                already = True      #boolean der sagt ob eintrag von ip gefunden wurde.
                break
        if already :
            break
        index+=1

    alive = str(new[7])
    date = new[11]
    proc = new[15]
    system = str(new[19])
    ram = new[23]
    if (already == True):                   #wenn verbindung bereits vorhanden werden die listen mit den Clientdaten verändert
        fullclient[index][0] = ip
        fullclient[index][1] = hostname
        fullclient[index][2] = system
        fullclient[index][4] = date
        fullclient[index][5] = proc
        fullclient[index][6] = ram
    else:
        fullclient.append([ip, hostname, system, alive, date, proc, ram])    #ansonten wird ein neuer Listeneintrag erstlelt.
    print("Client:" + str(fullclient))
    data = c.recv(1024)                     #server wartet auf packetinformationen des Clienten.
    data = bytes(data).decode(encoding='UTF-8')
    print(data)
    new_ = str(data)
    checktext = new_
    new_ = new_.split("'")                  #Informationen werden in das richtige Format gebracht
    updatename = new_[1]
    updateversion = new_[3]
    pruefsumme = new_[5]
    link = new_[7]
    command = new_[9]

    fullpackage.append([ip, getTime(),updatename, updateversion, pruefsumme, link, command])       #Packetinformationen werden der Liste hinzugefügt + der zuständgen IP
    k = k+1
    print("VERGLEICH:"+str(checktext)+"     mit: "+str(fulltext))
    if (str(checktext) != str(fulltext)):                                    #anhand der Updateversion wird überprüft ob der CLient das aktuellste Update besitzt
        needupdate[j] = True
        c.send("UPDATE! Das System ist nicht auf dem neusten Stand es wird ein Update automatisch installiert!".encode())
        versionstext = ("{'"+str(aktuellupdate)+"', '"+str(aktuelleVersion)+"', '"+str(aktuellepruefsumme)+"', '"+str(aktuellLink)+"', '"+str(aktuellCommand)+"'}")     #Daten mit dem Aktuellen Update werden an den Clienten geschickt
        c.send(versionstext.encode())
        fullpackage.append([ip, getTime(), aktuellupdate, aktuelleVersion,aktuellepruefsumme, aktuellLink, aktuellCommand])
        k = k+1
        print("Package:"+ str(fullpackage))
    if (str(checktext) == str(fulltext)):
        needupdate[j] = False
        c.send("Das System ist bereits auf dem neusten Stand kein Update notwendig".encode())

    #thread wird gestartet der alle 10 sekund das Aktuellste update an den Clienten schickt.
    thread_ = Thread(target=updateThread, args=(c, j, ip, index))
    thread_.daemon = True
    thread_.start()
def checkforquit():
    while True:
        end = input("")
        if end == 'quit':
            break
    os._exit(-1)

#Hauptseine(alle Clienten die sich verbunden haben werden angezeigt)
@app.route('/')
def hello_world():
    return render_template('index.html', fullclient=fullclient)
#Updateseite hostname und packet werden angezeigt.
@app.route('/updates')
def updates():
    return render_template('updates.html', fullpackage=fullpackage)
#alle updates werden angezeigt die auf dem Server verfügbar sind.
@app.route('/availUpdates')
def availupdates():
    return render_template('availUpdates.html')
#downloadfile für die zip
@app.route('/downloads/<path:filename>')
def downloads(filename):
    file = filename+".zip"
    return send_from_directory('downloads',file)
#Übersicht der möglichen Downloads und manueller Download hier möglich
@app.route('/download')
def download():
    return render_template('Download.html')

#Main methode startet Thread für Flask und normalen Server.
if __name__ == '__main__':
    tserver = Thread(target = start)
    tserver.daemon = True
    tserver.start()                                         #threads für server und überprüfen ob quit eingegeben wird zum verlassen werden gestartet
    tquit = Thread(target = checkforquit)
    tquit.daemon = True                                     #durch daemon beendet sich der thread wenn das programm beendet wird
    tquit.start()
    app.run(host="0.0.0.0", port="12345")