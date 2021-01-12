import threading
import socket
import random
import json
import os
import ipaddress
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import binascii

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

# Clear empty Env Vars for the defaults to override them
for k,v in os.environ.items():
    if not len(v):
        del os.environ[k]

SEED = os.environ.get('SEED', "0"*32)
random.seed(SEED)
TARGETLIST = os.environ.get('TARGETS', "%s/16" % IPADDRESS)
MISSILE = binascii.unhexlify(SEED[:2])
FRIENDLY_FIRE = os.environ.get('FRIENDLY_FIRE', 'False').lower() == 'True'.lower()

HP = int(os.environ.get('HP', 1))
DAMAGE = int(os.environ.get('DAMAGE', 1))
FIRERATE = int(os.environ.get('FIRERATE', 1))

TARGETS = __target_list(TARGETLIST)
PORT = 7587
REMAINING_HP = HP

# ===========

statuses = {
    100: "Spawned",
    200: "Hit",
    404: "Missed",
    500: "Got Hit",
    503: "Dodged",
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen(1)
    while REMAINING_HP > 0:
        conn, addr = s.accept()
        with conn:
            received_buffer = conn.recv(4096)
            received_damage = len(received_buffer)
            if not FRIENDLY_FIRE:
                if bytes([received_buffer[0]]) == MISSILE:
                    log({"code":503, "by":addr[0], "friendly-fire":True, "damage":received_damage})
                    continue
        REMAINING_HP -= received_damage
        log({"code":500, "by":addr[0], "damage":received_damage, "HP":REMAINING_HP})
    die()


def shoot():
    while(True):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = random.choice(TARGETS)
            s.settimeout(1/FIRERATE)
            s.connect((ip, PORT))
            s.sendall(MISSILE * DAMAGE)
            
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
            {
            "app":"KubeWars",
            "HP":{"total":HP,"remaining": REMAINING_HP,
            "percent":int((REMAINING_HP/HP)*100)},
            "missile":MISSILE.hex(),
            "host": str(IPADDRESS),
            "stats": {
                "firerate": FIRERATE,
                "damage": DAMAGE
                },
            "secret": SEED
            }
                ),
            "utf8")
        )

    def log_request(self, code):
    # to not interfere with Pod logs
        pass

# ===========

if __name__ == '__main__':
    
    log({"code":100, "address":str(IPADDRESS), "targets":TARGETLIST})
    

    status_srv = HTTPServer(('', 8080), MyServer)
    status_srv_thr = threading.Thread(target=status_srv.serve_forever)
    status_srv_thr.daemon = True
    status_srv_thr.start()

    shoot_thr = threading.Thread(target=shoot)
    shoot_thr.daemon = True
    shoot_thr.start()

    await_shots()
