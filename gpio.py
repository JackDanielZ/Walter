import os

GPIO_ROOT = '/sys/class/gpio'
GPIO_EXPORT = os.path.join(GPIO_ROOT, 'export')
GPIO_UNEXPORT = os.path.join(GPIO_ROOT, 'unexport')
FMODE = 'w'
IN, OUT = 'in', 'out'
LOW, HIGH = 0, 1

def GPIOExport(pin):
    with open(GPIO_EXPORT, FMODE) as f:
        f.write(str(pin))
#        f.flush()

def GPIOUnexport(pin):
    with open(GPIO_UNEXPORT, FMODE) as f:
        f.write(str(pin))
#        f.flush()

def GPIOExists(pin):
    return os.path.isfile(GPIO_ROOT+"/gpio"+str(pin)+"/direction")

def GPIODirectionSet(pin, dir):
    with open(GPIO_ROOT+"/gpio"+str(pin)+"/direction", FMODE) as f:
        f.write(dir)
        f.flush()

def GPIOWrite(pin, value):
    with open(GPIO_ROOT+"/gpio"+str(pin)+"/value", FMODE) as f:
        f.write(str(value))
        f.flush()
