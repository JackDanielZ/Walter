import os
import stat

GPIO_ROOT = '/sys/class/gpio'
GPIO_EXPORT = os.path.join(GPIO_ROOT, 'export')
GPIO_UNEXPORT = os.path.join(GPIO_ROOT, 'unexport')
IN, OUT = 'in', 'out'
LOW, HIGH = 0, 1

def GPIOExport(pin):
    with open(GPIO_EXPORT, 'w') as f:
        f.write(str(pin))
#        f.flush()

def GPIOUnexport(pin):
    with open(GPIO_UNEXPORT, 'w') as f:
        f.write(str(pin))
#        f.flush()

def GPIOIsDirectionReady(pin):
    actual = os.stat(GPIO_ROOT+"/gpio"+str(pin)+"/direction").st_mode
    return stat.S_IMODE(actual) & stat.S_IWOTH == stat.S_IWOTH

def GPIOExists(pin):
    return os.path.isfile(GPIO_ROOT+"/gpio"+str(pin)+"/direction")

def GPIODirectionSet(pin, dir):
    with open(GPIO_ROOT+"/gpio"+str(pin)+"/direction", 'w') as f:
        f.write(dir)
        f.flush()

def GPIOWrite(pin, value):
    with open(GPIO_ROOT+"/gpio"+str(pin)+"/value", 'w') as f:
        f.write(str(value))
        f.flush()
        print("Write", value, "to pin", pin)
