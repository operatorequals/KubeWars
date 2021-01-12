#!/usr/local/bin/python
from dashing import *

import math
import urllib.request
import json
import ipaddress
import string
import threading
import time


def __get_status(host='127.0.0.1'):
    try:
        ret = json.loads(urllib.request.urlopen(f'http://{host}:8080', timeout=2).read())
        return ret
    except Exception as e:
        return None

initial_status = __get_status()

enemy_ui = HSplit(
        ColorRangeVGauge(   # HP
            title="HP",
            val=0,
            border_color=1,
            colormap=(
                (100, 1),
                (66, 3),
                (33, 3),
            )
        ),
        Text(
            text="-",
            title="Stats",
            border_color=1,
            color=3
        ),
        title = "Enemy"
    )

nav_ui = Text(text="No target", title="Nav", border_color=5, color=1)

ENEMY_HP = enemy_ui.items[0]
ENEMY_TEXT = enemy_ui.items[1]

ENEMY_HOST = ""

ui = HSplit(
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
                    val=0,
                    border_color=3,
                    colormap=(
                        (33, 2),
                        (66, 3),
                        (100, 1),
                    )
                ),
            ),
            VSplit(
                VSplit(
                    HBrailleChart(title=f"Local Connection -> '{initial_status['host']}'", border_color=2, color=2),
                    VSplit(
                        Text(text="Enter a target IP", title="Target", border_color=5, color=2),    # Debug
                        HBrailleChart(title=f"Remote Connection", border_color=1, color=1),
                    )
                ),
                enemy_ui
            ),
        title='KubeWars Spacecraft',
        color=1,
        border_color=1
       
    )
ui.display()
term = ui._terminal

HP_GAUGE = ui.items[0].items[0]
FIRE_GAUGE = ui.items[0].items[1]

TARGET_TEXT = ui.items[1].items[0].items[1].items[0]

NAV_UI = ui.items[1].items[1]

HOST_GRAPHIC = ui.items[1].items[0].items[0]
ENEMY_GRAPHIC = ui.items[1].items[0].items[1].items[1]

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


def hit_bar():
    for i in range(100):
        FIRE_GAUGE.value = i
        time.sleep(0.0015)
    FIRE_GAUGE.border_color=1
    for i in range(100):
        FIRE_GAUGE.value = 100-i
        time.sleep(0.0015)
    FIRE_GAUGE.border_color=3


def __enemy_thread(while_ = 'ENEMY_HOST'):
    global ENEMY_HOST
    while eval(while_):
        enemy_status = __get_status(ENEMY_HOST)
        # ENEMY_TEXT.text = str(enemy_status)
        if enemy_status is None:
            continue
        ENEMY_TEXT.text = "Refreshing..."
        time.sleep(0.2)
        __set_enemy_nav(enemy_status)
        time.sleep(0.5)
    __unset_enemy_nav()
    # ENEMY_TEXT.text = str(bool(eval(while_)))


def __start_enemy_thread(target_status):
    __set_enemy_nav(target_status)

    enemy_thr = threading.Thread(target=__enemy_thread)
    enemy_thr.daemon = True
    enemy_thr.start()

    enemy_graph_thr = threading.Thread(target=connection_graphic, args=(ENEMY_GRAPHIC, 'ENEMY_HOST'))
    enemy_graph_thr.daemon = True
    enemy_graph_thr.start()


def __set_enemy_nav(enemy_status = None):
    if enemy_status is None:
        return

    stat_template = f"""HP: {enemy_status["HP"]["remaining"]}/{enemy_status["HP"]["total"]}
DAMAGE: {enemy_status["stats"]["damage"]}
FIRERATE: {enemy_status["stats"]["firerate"]}
    """

    ENEMY_GRAPHIC.title = f"Remote Connection ({enemy_status['host']})"
    ENEMY_TEXT.text = stat_template
    ENEMY_HP.value = enemy_status["HP"]["percent"]


def __unset_enemy_nav():
    ENEMY_GRAPHIC.title = f"Remote Connection"
    ENEMY_TEXT.text = "-"
    ENEMY_HP.value = 0
    ENEMY_HOST = ""
    NAV_UI = nav_ui


def keyboard_listen():

    global ENEMY_HOST
    with term.cbreak():
        val = ''
        while val.lower() != 'q':
            val = term.inkey(timeout=2)

            if not val:
                TARGET_TEXT.text = " "
                pass

            elif val.lower() == ' ':    # Pressing space fires
                hit_bar()

            elif val.name == "KEY_ENTER":
                try:
                    ip = ipaddress.ip_address(TARGET_TEXT.text.strip())
                    target_status = __get_status(str(ip))
                    if target_status['app'] == "KubeWars":
                        ENEMY_HOST = str(ip)
                        # __set_enemy_nav(target_status)
                        __start_enemy_thread(target_status)
                except ValueError:
                    TARGET_TEXT.text = "Invalid host!"
                    ENEMY_HOST = ""
                    __unset_enemy_nav()

            elif val.name == "KEY_BACKSPACE":
                TARGET_TEXT.text = " "

            elif val == "." or val in string.digits:
                TARGET_TEXT.text += val
            # elif val.is_sequence:
            #        TARGET_TEXT.text = " "


def display_ui():

    i = 0
    while True:
        if i % 24 == 0:
            status = __get_status()
        i += 1
        if status is None:
            continue

        hp = status["HP"]["percent"]

        HP_GAUGE.value = hp
        HP_GAUGE.title = f'HP - {status["HP"]["remaining"]}/{status["HP"]["total"]}'

        ui.display()
        time.sleep(1/25)


if __name__ == '__main__':

    display_thr = threading.Thread(target=display_ui)
    display_thr.daemon = True
    display_thr.start()

    graphic_thr = threading.Thread(target=connection_graphic)
    graphic_thr.daemon = True
    graphic_thr.start()


    keyboard_listen()
