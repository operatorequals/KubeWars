import threading
import socket
import random
import json
import os
import ipaddress
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# ===========

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

# ===========

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

# ===========

def await_shots():
    global REMAINING_HP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', PORT))
        s.listen()
        while REMAINING_HP > 0:
            conn, addr = s.accept()
            with conn:
                received_damage = len(conn.recv(4096))
            REMAINING_HP -= received_damage
            log({"code":500, "by":addr[0], "damage": received_damage, "HP":REMAINING_HP})
    die()


def shoot():
    while(True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = random.choice(TARGETS)
            s.settimeout(1/FIRERATE)
            s.connect((ip, PORT))
            s.sendall(b'B'*DAMAGE)
            
            log({"code":200, "target":ip, "damage":DAMAGE})
        except:
            log({"code":404, "target":ip})

# ===========

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Server", "KubeWars")
        self.end_headers()
        self.wfile.write(
            bytes(json.dumps(
            {"HP":{"total":HP,"remaining": REMAINING_HP, "percent":int((REMAINING_HP/HP)*100) }}
                ),
            "utf8")
        )

    def log_request(self, code):
    # to not interfere with Pod logs
        pass

# ===========

if __name__ == '__main__':
    
    log({"code":100, "address":str(IPADDRESS), "targets":TARGETLIST})
    
    random.seed(SEED)
    
    shoot_thr = threading.Thread(target=shoot)
    shoot_thr.daemon = True
    shoot_thr.start()

    status_srv = HTTPServer(('', 8080), MyServer)
    status_srv_thr = threading.Thread(target=status_srv.serve_forever)
    status_srv_thr.daemon = True
    status_srv_thr.start()

    await_shots()
