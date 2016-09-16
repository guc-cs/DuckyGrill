import usb.core
import hid
import time
import pyglet
from pygame import mixer
from threading import *

printLock = Semaphore(value = 1)
dictionaryLock = Semaphore(value = 1)

q = True

dictionary = {
4 : "A",
5 : "B",
6 : "C",
7 : "D",
8 : "E",
9 : "F",
10 : "G",
11 : "H",
12 : "I",
13 : "J",
14 : "K",
15 : "L",
16 : "M",
17 : "N",
18 : "O",
19 : "P",
20 : "Q",
21 : "R",
22 : "S",
23 : "T",
24 : "U",
25 : "V",
26 : "W",
27 : "X",
28 : "Y",
29 : "Z",
30 : "1",
31 : "2",
32 : "3",
33 : "4",
34 : "5",
35 : "6",
36 : "7",
37 : "8",
38 : "9",
39 : "0",
40 : "Enter"
}

class find_class(object):
    def __init__(self, class_):
        self._class = class_
    def __call__(self, device):
        # first, let's check the device
        if device.bDeviceClass == self._class:
            return True
        # ok, transverse all devices to find an
        # interface that matches our class
        for cfg in device:
            # find_descriptor: what's it?
            intf = usb.util.find_descriptor(
                                        cfg,
                                        bInterfaceClass=self._class
                                )
            if intf is not None:
                return True

        return False

def getId(dev):
    return (dev.idVendor, dev.idProduct, dev.bus, dev.address)

def state_machine(idV, idP, goal):
    state = 0
    try:
        h = hid.device()
        h.open(idV, idP)
        while True:
            try:
                ret = h.read(16)
                for i in ret:
                    if i > 3:

                        print i
                        if q:
                            try:
                                mixer.init()
                                quack = mixer.Sound('quack1.wav')
                                quack.play()
                            except:
                                pass

                        dictionaryLock.acquire()
                        if (i in dictionary.keys()) and dictionary[i] == goal[state]:
                            state += 1
                        else:
                            state = 0
                            if (i in dictionary.keys()) and dictionary[i] == goal[state]:
                                state += 1
                        dictionaryLock.release()
                        break
                if state == len(goal):
                    print "Access granted"
                    break
            except IOError, e:
                break
    except IOError, e:
        pass
    finally:
        h.close()

def handle_new_device(dev, goal):
    try:
        printLock.acquire()
        print "new device inserted"
        print getId(dev)
    finally:
        printLock.release()
    state_machine(dev.idVendor, dev.idProduct, goal)

def detect_hot_plug():
    devices =  list(usb.core.find(find_all=True, custom_match=find_class(3)))
    devices_set = set( getId(dev) for dev in devices )
    while True:
        try:
            dev_new = list(usb.core.find(find_all=True, custom_match=find_class(3)))
            dev_new_set = set( getId(dev) for dev in dev_new )
            new_dev_id = set(dev_new_set) - set(devices_set)
            if len(new_dev_id) > 0 :
                for id in new_dev_id:
                    dev = [x for x in dev_new if getId(x) == id]
                    t = Thread(target = handle_new_device, args = (dev[0], "ABCD"))
                    t.start()
            devices = dev_new
            devices_set = dev_new_set
            time.sleep(1)
        except:
            printLock.acquire()
            print ""
            printLock.release()
            break

def main():
    detect_hot_plug()

if __name__ == "__main__":
    main()
