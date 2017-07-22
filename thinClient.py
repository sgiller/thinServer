import socket, os, psutil, subprocess, platform, time, sys, math, urllib.request, zipfile
from threading import Thread

#hohlt sich systemspezifische Prozessorinformationen.
def get_processor_info():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        return subprocess.check_output(['/usr/sbin/sysctl', "-n", "machdep.cpu.brand_string"]).strip()
    elif platform.system() == "Linux":
        return platform.processor()
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

    information = "{'Hostname': '"+str(name)+"', 'Alive': 'alive', 'Datum': '"+str(date)+"', 'CPU': '"+str(bytes(proc).decode(encoding='UTF-8'))+"', 'System': '"+operating+"', 'Ram': '"+str(mem)+"GB'}"
    print(information)
    return information

#damit wird das aktuell installierte Update ausgelesen
def readUpdate():
    with open("update.txt", "r") as myfile:
        data = myfile.readline()
        myfile.close()
        str1 = ''.join(data)
        print(str1)
        return str1

#damit wird in die Update.txt geschrieben
def writteUpdate(text):
    updateFile = open("update.txt",'w')
    updateFile.write(text)
    updateFile.close()

def updateThread(client):
    while True:
        time.sleep(10)
        print("hallo!")
        message = "checkupdate"
        client.send(bytes(message, "utf-8"))
        data = client.recv(1024)
        data = bytes(data).decode(encoding='UTF-8')
        print(data)
        writteUpdate(str(data))
        print("Version wurde auf den neusten Stand gebracht")

#main methode client connected zum Server und schickt Informationen rüber
def main():
    host = '127.0.0.1'              #ip des hostst
    port = 50000                   #pport
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))    #connected zum host
    message = " "
    message = str(getInformation())
    client.send(bytes(message,"utf-8"))     #pc-Informationen werden zum Server geschickt
    message = readUpdate()                  #liest das aktuelle Update aus
    time.sleep(1)
    client.send(bytes(message, "utf-8"))    #sendet die aktuellen Updatedaten zum Server
    data = client.recv(1024)                #wartet auf antwort vom Server
    data = bytes(data).decode(encoding='UTF-8')
    print(data)
    if str(data).find("UPDATE!") != -1:
        data = client.recv(1024)
        data = bytes(data).decode(encoding='UTF-8')
        print(data)
        package = data.split("'")
        link = package[7]
        print(link)

        url = 'http://'+link+''
        print(url)
        urllib.request.urlretrieve(url, 'update.zip')
        print("Datei wird heruntergeladen")
        os.remove("update.txt")
        print("alte Updatedatei wird entfernt")
        zip = zipfile.ZipFile("update.zip",'r').extractall("")
        print("neues Update wird extrahiert")
        os.remove("update.zip")
        print("Zip wird entfernt")
        print("Aktuelles Update wurde erfolgreich installiert")

    message = readUpdate()
    time.sleep(1)
    tcheckUpdate = Thread(target=updateThread, args=(client,))
    tcheckUpdate.daemon = True
    tcheckUpdate.start()
    while True:
        if message == 'quit':
            client.close()
            break


main()