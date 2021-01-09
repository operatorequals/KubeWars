import threading
import socket
import random
import json
import os
import ipaddress
import sys
import time

def __target_list(target_list_str):
    targets = []

    for t in target_list_str.split(','):
        if('/' in t):
            net = ipaddress.ip_network(t, strict=False)
            for h in net.hosts():
                targets.append(str(ipaddress.ip_address(h)))
        else:
            targets.append(str(ipaddress.ip_address(t)))

    return targets

with os.popen("hostname -i") as p:
    IPADDRESS = ipaddress.ip_address(p.read().strip())

HP = int(os.environ.get('HP', 1))
DAMAGE = int(os.environ.get('DAMAGE', 1))
FIRERATE = int(os.environ.get('FIRERATE', 1))

SEED = os.environ.get('SEED', "0"*32)
TARGETLIST = os.environ.get('TARGETS', "%s/16" % IPADDRESS)

TARGETS = __target_list(TARGETLIST)
PORT = 7587
REMAINING_HP = HP

statuses = {
    100: "Spawned",
    200: "Hit",
    404: "Missed",
    500: "Got Hit",
    504: "Killed",
}

def log(line):
    line["text"] = statuses[line["code"]]
    line["time"] = int(time.time())
    print(json.dumps(line))


def die():
    log({"code":504})
    sys.exit(0)


def await_shots():
    global REMAINING_HP
    while REMAINING_HP > 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                received_damage = len(conn.recv(4096))
                REMAINING_HP -= received_damage
                log({"code":500, "by":addr[0], "damage": received_damage, "HP":REMAINING_HP})
    die()


def shoot():
    while(True):
        # time.sleep()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = random.choice(TARGETS)
            s.settimeout(1/FIRERATE)
            s.connect((ip, PORT))
            s.sendall(b'B'*DAMAGE)
            
            log({"code":200, "whom":ip, "damage":DAMAGE})
        except:
            log({"code":404, "whom":ip})


if __name__ == '__main__':
    
    log({"code":100, "address":str(IPADDRESS), "targets":TARGETLIST})
    
    random.seed(SEED)
    
    s = threading.Thread(target=shoot)
    s.daemon = True
    s.start()

    await_shots()
