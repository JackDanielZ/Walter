from gpio import *
import time
import argparse

pins = {
        "Solenoid_0": { "in1" : 24, "in2" : 23 },
        "Solenoid_1": { "in1" : 22, "in2" : 27 }
        }

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["start", "stop"])
parser.add_argument("sol_id", type=int, choices=[0, 1])
args = parser.parse_args()

sol_name = "Solenoid_"+str(args.sol_id)
print(pins[sol_name])

in1 = pins[sol_name]["in1"]
in2 = pins[sol_name]["in2"]

if GPIOExists(in1) == False:
    GPIOExport(in1)
if GPIOExists(in2) == False:
    GPIOExport(in2)

while GPIOIsDirectionReady(in1) == False and GPIOIsDirectionReady(in2) == False:
    time.sleep(1)

GPIODirectionSet(in1, OUT)
GPIODirectionSet(in2, OUT)

if args.action == "start":
    GPIOWrite(in1, LOW)
    GPIOWrite(in2, HIGH)
else:
    GPIOWrite(in1, HIGH)
    GPIOWrite(in2, LOW)

time.sleep(5)

GPIOWrite(in1, LOW)
GPIOWrite(in2, LOW)

GPIOUnexport(in1)
GPIOUnexport(in2)
