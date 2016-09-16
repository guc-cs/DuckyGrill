import usb.core
import time
from threading import *

printLock = Semaphore(value = 1)

def handle_new_device(idV, idP, bus, add):
    try:
        printLock.acquire()
        print "new device inserted"
        print (idV, idP, bus, add)
    finally:
        printLock.release()

def main():
    devices = set( (dev.idVendor, dev.idProduct, dev.bus, dev.address) for dev in usb.core.find(find_all=True) )

    while True:
        try:
            dev2 = set( (dev.idVendor, dev.idProduct, dev.bus, dev.address) for dev in usb.core.find(find_all=True) )
            if len(dev2) > len(devices) and dev2 != devices:
                for dev in list(dev2 - devices):
                    t = Thread(target = handle_new_device, args = dev)
                    t.start()
            devices = dev2
            time.sleep(1)
        except:
            printLock.acquire()
            print ""
            printLock.release()
            break

if __name__ == "__main__":
    main()
