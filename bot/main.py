import threading
import socket
import random
import json
import os
import ipaddress
import sys

PORT = 7587

statuses = {
    100: "Spawned",
    200: "Hit",
    404: "Missed",
    500: "Killed"
}

def log(line):
    line["text"] = statuses[line["code"]]
    print(json.dumps(line))

def await_shots():    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            log({"code":500, "by":addr[0]})

def shoot():
    while(True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = random.choice(TARGETS)

            s.connect((ip, PORT))
            s.sendall(b'Pew')
            
            log({"code":200, "whom":ip})
        
        except:
            log({"code":404, "whom":ip})

if __name__ == '__main__':
    SEED = os.getenv('SEED')
    FIRERATE = os.getenv('FIRERATE')
    TARGETLIST = os.getenv('TARGETS')

    TARGETS = []

    for t in TARGETLIST.split(','):
        if('/' in t):
            net = ipaddress.ip_network(t)
            for h in net.hosts:
                TARGETS.append(str(ipaddress.ip_address(h)))
        else:
            TARGETS.append(str(ipaddress.ip_address(t)))
    
    log({"code":100})
    
    bot = threading.Thread(target=await_shots)
    
    random.seed(SEED)
    
    for i in range(int(FIRERATE)):
        s = threading.Thread(target=shoot)
        s.daemon = True
        s.start()

    bot.start()
    bot.join()
    sys.exit()

