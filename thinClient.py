import socket, threading, time, os, json, psutil, subprocess, platform, time, sys, math

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

#main methode client connected zum Server und schickt Informationen rüber
def main():
    host = '127.0.0.1'              #ip des hostst
    port = 50001                    #pport
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
        writteUpdate(str(data))
        print("Aktuelles Update wurde erfolgreich installiert")

    message = readUpdate()
    time.sleep(1)
    client.send(bytes(message, "utf-8"))
    while True:
        message = input("send um erneut Paketinformationen zu schicken quit um verbindung zu trennen")
        if message == 'quit':
            break
        else:
            message = "needUpdate"
            time.sleep(1)
            client.send(bytes(message, "utf-8"))
            data = client.recv(1024)
            data = bytes(data).decode(encoding='UTF-8')
            print(data)
            writteUpdate(str(data))

    client.close()


main()