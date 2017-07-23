import socket, os, psutil, subprocess, platform, time, sys, math, urllib.request, zipfile, cpuinfo
from threading import Thread
from pathlib import Path

host = '192.168.0.31'  # ip des hostst
flaskport = 12345
port = 50000  #port

#hohlt sich systemspezifische Prozessorinformationen.
def get_processor_info():
    if platform.system() == "Windows":
         return cpuinfo.get_cpu_info().get('brand')
    elif platform.system() == "Darwin":
        return subprocess.check_output(['/usr/sbin/sysctl', "-n", "machdep.cpu.brand_string"]).strip()
    elif platform.system() == "Linux":
         return cpuinfo.get_cpu_info().get('brand')
    return ""

#in dieser Funktion werden alle nötigen Informationen zusammengefasst
def getInformation():
    mem = psutil.virtual_memory()
    mem = mem.total/1024**3
    mem = math.ceil(mem*100)/100

    proc = get_processor_info()

    name = platform.uname().node

    date = time.strftime("%d.%m.%Y %H:%M:%S")
    print(str(date))

    operating = sys.platform
    if(platform.system() == "Darwin"):
        information = "{'Hostname': '"+str(name)+"', 'Alive': 'alive', 'Datum': '"+str(date)+"', 'CPU': '"+str(bytes(proc).decode(encoding='UTF-8'))+"', 'System': '"+operating+"', 'Ram': '"+str(mem)+"GB'}"
    else:
        information = "{'Hostname': '" + str(name) + "', 'Alive': 'alive', 'Datum': '" + str(date) + "', 'CPU': '" +proc+"', 'System': '"+operating+"', 'Ram': '"+str(mem)+"GB'}"

    print(information)
    return information

#damit wird das aktuell installierte Update ausgelesen
def readUpdate():
    my_file = Path("update.txt")
    if my_file.is_file():
        with open("update.txt", "r") as myfile:
            data = myfile.readline()
            myfile.close()
            str1 = ''.join(data)
            print(str1)
            myfile.close()
            return str1
    else:
        file = open("update.txt", 'w+')
        file.write("{'Update 3', '3.0', 'ghi', '"+host+":"+str(flaskport)+"/downloads/update3', 'tarxyz'}")
        file.close()
        with open("update.txt", "r") as myfile:
            data = myfile.readline()
            myfile.close()
            str1 = ''.join(data)
            print(str1)
            myfile.close()
            return str1

#damit wird in die Update.txt geschrieben
def writteUpdate(text):
    updateFile = open("update.txt",'w')
    updateFile.write(text)
    updateFile.close()

def changeFile(data):
    package = data.split("'")
    print(data)
    link = package[7]
    print(link)

    url = 'http://' +host+":"+str(flaskport)+ link + ''
    print(url)
    urllib.request.urlretrieve(url, 'update.zip')
    print("Datei wird heruntergeladen")
    os.remove("update.txt")
    print("alte Updatedatei wird entfernt")
    zip = zipfile.ZipFile("update.zip", 'r').extractall("")
    print("neues Update wird extrahiert")
    os.remove("update.zip")
    print("Zip wird entfernt")
    print("Aktuelles Update wurde erfolgreich installiert")

def updateThread(client):
    while True:
        data = client.recv(1024)
        data = bytes(data).decode(encoding='UTF-8')
        if data != readUpdate():
            print("neues update wird heruntergeladen")
            changeFile(data)
        message = readUpdate()  # liest das aktuelle Update aus
        time.sleep(1)
        print("sende update an Server-->")
        client.send(bytes(message, "utf-8"))  # sendet die aktuellen Updatedaten zum Server

#main methode client connected zum Server und schickt Informationen rüber
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))    #connected zum host
    message = " "
    message = str(getInformation())
    print ("folgende Informationen werden an den Server geschickt!")
    client.send(bytes(message,"utf-8"))     #pc-Informationen werden zum Server geschickt
    message = readUpdate()                  #liest das aktuelle Update aus
    print("folgende Packetinformationen werden an den Server geschickt!")
    print(message)
    time.sleep(1)
    client.send(bytes(message, "utf-8"))    #sendet die aktuellen Updatedaten zum Server
    data = client.recv(1024)                #wartet auf antwort vom Server
    data = bytes(data).decode(encoding='UTF-8')
    print(data)
    if str(data).find("UPDATE!") != -1:     #bekommt der CLient UPDATE! weiß er das er ein neues Update benötigt
        data = client.recv(1024)
        data = bytes(data).decode(encoding='UTF-8')
        print(data)
        changeFile(data)



    message = readUpdate()
    time.sleep(1)
    tcheckUpdate = Thread(target=updateThread, args=(client,))      #Thread kommuniziert mit server bekommt alle 10 sekunden aktuellstes Serverpaket
    tcheckUpdate.daemon = True
    tcheckUpdate.start()
    while True:
        pass

main()