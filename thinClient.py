import socket, threading, time, os, json, psutil, subprocess, platform, time, sys, math

def get_processor_info():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        return subprocess.check_output(['/usr/sbin/sysctl', "-n", "machdep.cpu.brand_string"]).strip()
    elif platform.system() == "Linux":
        return platform.processor()
    return ""

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

def readUpdate():
    with open("update.txt", "r") as myfile:
        data = myfile.readline()
        myfile.close()
        str1 = ''.join(data)
        print(str1)
        return str1

def writteUpdate(text):
    updateFile = open("update.txt",'w')
    updateFile.write(text)
    updateFile.close()


def main():
    host = '127.0.0.1'
    port = 50001
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    message = " "
    message = str(getInformation())
    client.send(bytes(message,"utf-8"))
    message = readUpdate()
    time.sleep(1)
    client.send(bytes(message, "utf-8"))
    data = client.recv(1024)
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