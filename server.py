import sys
import os
import socket
import select
import time
import re
from datetime import datetime

import gpio

# Tasks:
# - open_water 0|1 time (e.g 20m, 1h, 5s) = [ [ 0, open_solenoid Solenoid_0|1 ], [ 5, pause_solenoid Solenoid_0|1 ], [ XXX, close_solenoid Solenoid_0|1 ], [ 5, pause_solenoid Solenoid_0|1 ] ]

# Actions:
# - open_solenoid Solenoid_0|1
# - pause_solenoid Solenoid_0|1
# - close_solenoid Solenoid_0|1
# - cancel_next_open: cancel next open operation

cancel_next_open = False

solenoids_infos = {
        "0": { "in1" : 24, "in2" : 23 },
        "1": { "in1" : 22, "in2" : 27 }
        }

server_address = '/tmp/walter_uds'

def task_consume(task):
    action = task[0]
    timeout = action[0]

    if timeout == 0:
        print(datetime.now(), "-", action[1])
        sys.stdout.flush()
        elts = action[1].split(" ")
        if elts[0] == "open_solenoid":
            gpio.GPIOWrite(solenoids_infos[elts[1]]["in1"], gpio.LOW)
            gpio.GPIOWrite(solenoids_infos[elts[1]]["in2"], gpio.HIGH)
        elif elts[0] == "close_solenoid":
            gpio.GPIOWrite(solenoids_infos[elts[1]]["in1"], gpio.HIGH)
            gpio.GPIOWrite(solenoids_infos[elts[1]]["in2"], gpio.LOW)
        elif elts[0] == "pause_solenoid":
            gpio.GPIOWrite(solenoids_infos[elts[1]]["in1"], gpio.LOW)
            gpio.GPIOWrite(solenoids_infos[elts[1]]["in2"], gpio.LOW)

        task.pop(0)

print(datetime.now(), "-", "Launch server")
sys.stdout.flush()

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    print(datetime.now(), "-", "Exception")
    sys.stdout.flush()
    if os.path.exists(server_address):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

for sol in solenoids_infos:
    for pin in solenoids_infos[sol]:
        pin_id = solenoids_infos[sol][pin]
        if gpio.GPIOExists(pin_id) == False:
            gpio.GPIOExport(pin_id)
        while gpio.GPIOIsDirectionReady(pin_id) == False:
            time.sleep(1)
        gpio.GPIODirectionSet(pin_id, gpio.OUT)

tasks = []

while True:
    readable, _, _ = select.select([sock], [], [], 1)

    if readable:
        # New connection
        connection, client_address = sock.accept()
        # Read data
        data = connection.recv(256)
        print(datetime.now(), "-", "Received command:", data)
        sys.stdout.flush()
        if data:
            elts = data.decode('utf-8').split(" ")
            nb_elts = len(elts)
            task = []
            if elts[0] == "open_water":
                if cancel_next_open == True:
                    print(datetime.now(), "-", "Open cancelled")
                    cancel_next_open = False
                else:
                    if nb_elts == 3 and str(elts[1]) in solenoids_infos:
                        m = re.search("([0-9]+)([hms])", elts[2])
                        if m == None: continue

                        time = int(m.group(1))
                        if m.group(2) == 'm': time *= 60
                        if m.group(2) == 'h': time *= 3600

                        task.append([0, "open_solenoid {}".format(elts[1])])
                        task.append([5, "pause_solenoid {}".format(elts[1])])
                        task.append([time, "close_solenoid {}".format(elts[1])])
                        task.append([5, "pause_solenoid {}".format(elts[1])])
            elif elts[0] == "stop":
                task.append([0, "close_solenoid 0"])
                task.append([0, "close_solenoid 1"])
                task.append([5, "pause_solenoid 0"])
                task.append([0, "pause_solenoid 1"])
            elif elts[0] == "cancel_next_open":
                cancel_next_open = True
            else:
                print(datetime.now(), "-", "Unrecognized command")
                sys.stdout.flush()

            if task != []:
                tasks.append(task)
                print(datetime.now(), "-", tasks)
                sys.stdout.flush()
                task_consume(task)
        connection.close()
    else:
        old_tasks = tasks
        tasks = []
        task_updated = False
        for task in old_tasks:
            if task == []:
                task_updated = True
                continue
            action = task[0]
            if action == []:
                task_updated = True
                continue
            timeout = action[0]
            tasks.append(task)
            if timeout != 0:
                action[0] -= 1
            else:
                task_consume(task)
                task_updated = True
        if task_updated:
            print(datetime.now(), "-", tasks)
            sys.stdout.flush()
