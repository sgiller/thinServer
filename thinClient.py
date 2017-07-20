import socket, threading, time, os, json, psutil, subprocess, platform, time, sys

def get_processor_info():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        return subprocess.check_output(['/usr/sbin/sysctl', "-n", "machdep.cpu.brand_string"]).strip()
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        return subprocess.check_output(command, shell=True).strip()
    return ""

def getInformation():
    mem = psutil.virtual_memory()
    mem = mem.total/1024**3

    proc = str(get_processor_info())
    proc = proc[2:len(proc)-1]

    name = platform.uname().node

    ip =socket.gethostbyname(socket.gethostname())

    date = time.strftime("%d.%m.%Y %H:%M:%S")
    print(str(date))

    operating = sys.platform

    information = {"Hostname": name, "Ip": ip, "Alive": "alive", "Datum": date, "CPU": proc}
    print(information)
    return information

def main():
    host = '127.0.0.1'
    port = 50000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    message = str(getInformation())
    client.send(bytes(message,"utf-8"))
    while message != 'quit':
        message = input("Nachricht: ")
    client.close()


main()