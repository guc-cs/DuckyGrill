import usb.core
import time
from threading import *

printLock = Semaphore(value = 1)

def getId(dev):
    return (dev.idVendor, dev.idProduct, dev.bus, dev.address)

def handle_new_device(dev):
    try:
        printLock.acquire()
        print "new device inserted"
        print getId(dev)
    finally:
        printLock.release()

def detect_hot_plug():
    devices =  list(usb.core.find(find_all=True))
    devices_set = set( getId(dev) for dev in devices )
    while True:
        try:
            dev_new = list(usb.core.find(find_all=True))
            dev_new_set = set( getId(dev) for dev in dev_new )
            new_dev_id = set(dev_new_set) - set(devices_set)
            if len(new_dev_id) > 0 :
                for id in new_dev_id:
                    new_dev = (x for x in dev_new if getId(x) == id)
                    t = Thread(target = handle_new_device, args = new_dev)
                    t.start()
            devices = dev_new
            devices_set = dev_new_set
            time.sleep(1)
        except Exception, e:
            printLock.acquire()
            print ""
            print e
            printLock.release()
            break

def main():
    detect_hot_plug()

if __name__ == "__main__":
    main()
