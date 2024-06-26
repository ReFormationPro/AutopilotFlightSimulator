import os
import pty
import termios
import threading
import time
import tty
import re
import json
import serial
from cmds import *
import logging

logging.basicConfig(level=logging.INFO)

# Load test case, which is agents_config
with open("test-case-0.json", 'r') as f:
    lines = f.readlines()
    lines = [line for line in lines if not re.search(r'//', line)]
    TESTCASE = json.loads("\n".join(lines))

master, slave = pty.openpty()
# Master should not read what it has written / stop echo
tty.setraw(master, termios.TCSANOW)
s_name = os.ttyname(slave)

mode_lock = threading.Lock()
mode_cv = threading.Condition(mode_lock)
new_speed = 0
start_time = 0
curr_dist = -1
period = TESTCASE["period"]  # secs

print(f"Slave: '{s_name}'")


def reader_worker():
    global new_speed, curr_dist
    while True:
        msg = os.read(master, 1000)
        cmd = Command.parse_bytes(msg)
        logging.info(f"msg decode: {cmd} at {time.time() - start_time}")
        if type(cmd) == GoCommand:
            cmd: GoCommand
            curr_dist = cmd.total_distance
            with mode_cv:
                mode_cv.notify()
        elif type(cmd) == SpeedCommand:
            # NOTE No synchronization is used here, may cause errors
            cmd: SpeedCommand
            new_speed = cmd.speed


reader_thread = threading.Thread(target=reader_worker)
reader_thread.daemon = True
reader_thread.start()

print(f"Waiting for GO command")
with mode_cv:
    mode_cv.wait()
start_time = time.time()
for i in range(1, 999999999):
    curr_dist -= new_speed
    # Send a distance command
    cmd = DistanceCommand(curr_dist)
    os.write(master, cmd.make_bytes())
    logging.info(f"Wrote {cmd} at {time.time() - start_time}")
    # Sleeping fixed amount is risky, error accumulates quickly
    next_alarm = start_time + i*period
    time.sleep(next_alarm - time.time())
