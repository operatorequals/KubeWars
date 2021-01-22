#!/usr/local/bin/python
from dashing import *

import math
import urllib.request
import json
import ipaddress
from pathlib import Path
import random
import string
import sys
import threading
import time

KUBEWARS_FILE = '/tmp/kubewars.ui'

def __get_status(host='127.0.0.1'):
    try:
        ret = json.loads(urllib.request.urlopen(f'http://{host}:8080', timeout=2).read())
        return ret
    except Exception as e:
        return None


initial_status = __get_status()
if not initial_status:
    print ("Are you sure there is a Spacecraft?")
    sys.exit(1)

target_ui = HSplit(
        ColorRangeVGauge(   # HP
            title="HP",
            val=0,
            border_color=3,
            colormap=(
                (26, 1),
                (51, 3),
                (100, 2),
            )
        ),
        Text(
            text="-",
            title="Stats",
            border_color=3,
            color=3
        ),
        title = "Target",
        border_color=3,
    )

null_ui = Text(text = "Someone is on command of this spaceship already!", title="Status", border_color=6, color=7)

debug_ui = HSplit(
    Text(text = "-", title="Status", border_color=6, color=7),
    Text(text = "-", title="General Messages", border_color=6, color=7),
    title="Debug Panel", border_color=6
    )

STATUS_TEXT = debug_ui.items[0]
DEBUG_TEXT = debug_ui.items[1]

nav_ui = HBrailleChart(title="Nav (Just Admire the Grahic)", border_color=5, color=6)

TARGET_HP = target_ui.items[0]
TARGET_TEXT = target_ui.items[1]

TARGET_HOST = ""

main_ui = HSplit(
            HSplit(
                ColorRangeVGauge(   # HP
                    title="HP",
                    val=100,
                    border_color=2,
                    colormap=(
                        (26, 1),
                        (51, 3),
                        (100, 2),
                    )
                ),
                ColorRangeVGauge(   # Fire
                    val=-100,
                    border_color=1,
                    colormap=(
                        (33, 2),
                        (66, 3),
                        (100, 1),
                    )
                ),
            ),
            VSplit(
                VSplit(
                    HBrailleChart(title=f"Local Connection -> '{initial_status['host']}'", border_color=2, color=3),
                    VSplit(
                        Text(text="Enter a target IP", title="Target", border_color=5, color=2),    # Debug
                        HBrailleChart(title=f"Remote Connection", border_color=3, color=3),
                    )
                ),
                target_ui
            ),
        title='KubeWars Spacecraft',
        color=1,
        border_color=5
       
    )

UI_INDEX = 0
UIs = [main_ui, nav_ui, debug_ui]

UI = null_ui
TERM = None # Useful for calls to blessed terminal for input

HP_GAUGE = main_ui.items[0].items[0]
FIRE_GAUGE = main_ui.items[0].items[1]

AIM_TEXT = main_ui.items[1].items[0].items[1].items[0]

NAV_UI = main_ui.items[1].items[1]

HOST_GRAPHIC = main_ui.items[1].items[0].items[0]
TARGET_GRAPHIC = main_ui.items[1].items[0].items[1].items[1]

def connection_graphic(braille_graphic = None, while_ = 'True'):
    if braille_graphic == None:
        braille_graphic = HOST_GRAPHIC
    cycle = 0
    while eval(while_):
        cycle += 1
        braille_graphic.append(50 + 50 * math.sin(cycle / 6.0))

        time.sleep(0.01)
    # Empty the graphic
    for i in range(1024):
        braille_graphic.append(0)

def hit(host):
    if host:
        with open(KUBEWARS_FILE,'w') as f:
            f.write(json.dumps({"target": TARGET_HOST, "time":time.time()}))

def hit_bar():
    for i in range(100):
        FIRE_GAUGE.value = i
        time.sleep(0.002)
    FIRE_GAUGE.border_color=3
    for i in range(100):
        FIRE_GAUGE.value = 100-i
        time.sleep(0.002)
    FIRE_GAUGE.border_color=1
    FIRE_GAUGE.value = -100

def __target_friend():
    TARGET_HP.border_color = 2
    TARGET_TEXT.border_color = 2
    target_ui.border_color = 2
    TARGET_GRAPHIC.color = 2

def __target_enemy():
    TARGET_HP.border_color = 1
    TARGET_TEXT.border_color = 1
    target_ui.border_color = 1
    TARGET_GRAPHIC.color = 1

def __target_neutral():
    TARGET_HP.border_color = 3
    TARGET_TEXT.border_color = 3
    target_ui.border_color = 3
    TARGET_GRAPHIC.color = 1

def __target_thread(while_ = 'TARGET_HOST'):
    global TARGET_HOST
    while eval(while_):
        enemy_status = __get_status(TARGET_HOST)
        if enemy_status is None:
            __unset_target_nav()
            continue
        TARGET_TEXT.text = "Refreshing..."
        time.sleep(0.2)
        __set_target_nav(enemy_status)
        time.sleep(0.5)
    __unset_target_nav()


def __start_enemy_thread(target_status):
    __set_target_nav(target_status)

    enemy_thr = threading.Thread(target=__target_thread)
    enemy_thr.daemon = True
    enemy_thr.start()

    enemy_graph_thr = threading.Thread(target=connection_graphic, args=(TARGET_GRAPHIC, 'TARGET_HOST'))
    enemy_graph_thr.daemon = True
    enemy_graph_thr.start()


def __set_target_nav(enemy_status = None):
    if enemy_status is None:
        return

    if enemy_status['secret'] == initial_status['secret']:
        __target_friend()
    else:
        __target_enemy()

    stat_template = f"""HP: {enemy_status["HP"]["remaining"]}/{enemy_status["HP"]["total"]}
DAMAGE: {enemy_status["stats"]["damage"]}
FIRERATE: {enemy_status["stats"]["firerate"]}
    """

    TARGET_GRAPHIC.title = f"Remote Connection ({enemy_status['host']})"
    TARGET_TEXT.text = stat_template
    TARGET_HP.value = enemy_status["HP"]["percent"]


def __unset_target_nav():
    TARGET_GRAPHIC.title = f"Remote Connection"
    TARGET_TEXT.text = "-"
    TARGET_HP.value = 0
    TARGET_HOST = ""
    __target_neutral()


def __nav_graphic():
    # Fill the sky with stars!
    for i in range(1920):
        star = random.randint(0, 100)
        nav_ui.append(star)

    while True:
        star = random.randint(0, 100)
        nav_ui.append(star)
        time.sleep(0.01)

def keyboard_listen():

    global TARGET_HOST, UI, UI_INDEX
    with TERM.cbreak():
        val = ''
        while val.lower() != 'q':
            val = TERM.inkey(timeout=2)

            if not val:
                AIM_TEXT.text = " "
                pass

            elif val.lower() == ' ':    # Pressing space fires
                hit_bar()
                hit(TARGET_HOST)

            elif val.name == "KEY_ENTER":
                TARGET_HOST = ""
                __unset_target_nav()
                try:
                    ip = ipaddress.ip_address(AIM_TEXT.text.strip())
                    target_status = __get_status(str(ip))
                    if target_status is None:
                        raise ValueError()
                    if target_status['app'] == "KubeWars":
                        TARGET_HOST = str(ip)
                        __start_enemy_thread(target_status)
                except ValueError:
                    AIM_TEXT.text = "Invalid host!"
                    pass

            elif val.name == "KEY_BACKSPACE":
                AIM_TEXT.text = " "

            elif val.name == "KEY_TAB":
                UI_INDEX += 1
                UI = UIs[UI_INDEX % len(UIs)]

            elif val == "." or val in string.digits:
                AIM_TEXT.text += val
            # elif val.is_sequence:
            #        AIM_TEXT.text = " "


def display_ui():
    global UI
    UI = UIs[UI_INDEX]

    i = 0
    while True:
        if i % 24 == 0:
            status = __get_status()
            STATUS_TEXT.text = json.dumps(status, indent = 1, separators=(',', ':'))
        i += 1
        if status is None:
            continue

        hp = status["HP"]["percent"]

        HP_GAUGE.value = hp
        HP_GAUGE.title = f'HP - {status["HP"]["remaining"]}/{status["HP"]["total"]}'

        UI.display()
        time.sleep(1/25)


def set_ui_opened():
    try:
        Path(KUBEWARS_FILE).touch(exist_ok = False)
        return True
    except FileExistsError:
        return False

def set_ui_closed():
    try:
        Path(KUBEWARS_FILE).unlink()
        return True
    except FileExistsError:
        return False

def password_check():
    import hashlib
    import getpass
    password = bytes(getpass.getpass("Spacecraft's Password: "), 'utf8')
    password_hash = hashlib.sha256(password).hexdigest().lower()
    spacecraft_password = initial_status['secret']
    return password_hash == spacecraft_password

if __name__ == '__main__':

    if not password_check():
        print("Wrong password.")
        sys.exit(2)

    if not set_ui_opened():
        UI.display()
        sys.exit(3)

    UI.display()
    TERM = UI._terminal

    display_thr = threading.Thread(target=display_ui)
    display_thr.daemon = True
    display_thr.start()

    nav_thr = threading.Thread(target=__nav_graphic)
    nav_thr.daemon = True
    nav_thr.start()

    graphic_thr = threading.Thread(target=connection_graphic)
    graphic_thr.daemon = True
    graphic_thr.start()

    try:
        keyboard_listen()
    except (Exception, KeyboardInterrupt) as e:
        DEBUG_TEXT.text = str(e)
    finally:
        set_ui_closed()
