import usb.core
import hid
import time
import optparse
from pygame import mixer
from threading import *

printLock = Semaphore(value = 1)
dictionaryLock = Semaphore(value = 1)

challenge = "ABCD"
d = False
q = False
dictionary = { 4 : "A", 5 : "B", 6 : "C", 7 : "D", 8 : "E", 9 : "F", 10 : "G", 11 : "H", 12 : "I", 13 : "J", 14 : "K", 15 : "L", 16 : "M", 17 : "N", 18 : "O", 19 : "P", 20 : "Q", 21 : "R", 22 : "S", 23 : "T", 24 : "U", 25 : "V", 26 : "W", 27 : "X", 28 : "Y", 29 : "Z", 30 : "1", 31 : "2", 32 : "3", 33 : "4", 34 : "5", 35 : "6", 36 : "7", 37 : "8", 38 : "9", 39 : "0" }

class find_class(object):
    def __init__(self, class_):
        self._class = class_
    def __call__(self, device):
        #check the device
        if device.bDeviceClass == self._class:
            return True
        #transverse all devices to find an
        #interface that matches our class
        for cfg in device:
            #find_descriptor
            intf = usb.util.find_descriptor(
                                        cfg,
                                        bInterfaceClass=self._class
                                )
            if intf is not None:
                return True

        return False

def getId(dev):
    #generate unique identifing tuple of three values to each device
    return (dev.idVendor, dev.idProduct, dev.bus, dev.address)

def state_machine(h, goal):
    #initial state
    state = 0
    try:
        #continuesly block device
        while True:
            try:
                #blocking io read of device
                ret = h.read(8)
                #check the array of bytes sent by the device for an integer maching USB escape code letters
                for i in ret:
                    if i > 3 and i < 40:
                        if(d):
                            try:
                                printLock.acquire()
                                #print the escape code for debugging
                                print "[+] %d" % i
                            finally:
                                printLock.release()
                        #quack the wrong key for quack
                        if q:
                            try:
                                mixer.init()
                                quack = mixer.Sound('quack1.wav')
                                quack.play()
                            except Exception, e:
                                pass
                        try:
                            #check the dictionary to translate escape code to character of corresponding state
                            dictionaryLock.acquire()
                            if (i in dictionary.keys()) and dictionary[i] == goal[state]:
                                #if a match happens advance to next state
                                state += 1
                            else:
                                #if not return to initial state
                                state = 0
                                #if not, maybe the last transition matches the transition from state 0 to 1
                                if (i in dictionary.keys()) and dictionary[i] == goal[state]:
                                    state += 1
                        finally:
                            dictionaryLock.release()
                            break
                #if final state is reached
                if state == len(goal):
                    if(d):
                        try:
                            printLock.acquire()
                            #print grant access debugging
                            print "[+] Access granted"
                        finally:
                            printLock.release()
                    #break out of blocking io loop
                    break
            except IOError, e:
                break
    except IOError, e:
        pass
    finally:
        h.close()

def detect_hot_plug():
    my_threads = []
    #store current connected devices as reference point filter only devices with class 3 interfaces
    devices_set = set( getId(dev) for dev in usb.core.find(find_all=True, custom_match=find_class(3)) )
    #continuesly check for state change of USB devices
    while True:
        try:
            #capture current connected devices filter only devices with class 3 interfaces
            dev_new = list(usb.core.find(find_all=True, custom_match=find_class(3)))
            #generate unique device identifier set
            dev_new_set = set( getId(dev) for dev in dev_new )
            #the difference between current device set and old device set
            diff = set(dev_new_set) - set(devices_set)
            #if there exist a difference for each new device, acquire a descriptor and pass it to a state machine thread
            if len(diff) > 0 :
                for dev in diff:
                    if(d):
                        print "[+] new device inserted"
                        print dev
                    h = hid.device()
                    h.open(dev[0], dev[1])
                    t = Thread(target = state_machine, args = (h, challenge))
                    my_threads.append(t)
                    t.start()
            #update old device set
            devices_set = dev_new_set
            #time.sleep(1)
        except KeyboardInterrupt:
            break

def main():
    parser = optparse.OptionParser('usage prog -c <challenge string>')
    parser.add_option('-c', '--challenge', dest='challenge', type='string', help='specify challenge to be entered by HID in highercase')
    parser.add_option('-d', '--debug', action="store_true", dest="debug", help="enable printing debug statements")
    parser.add_option('-q', '--quack', action="store_true", dest="quack", help="enable quacking on HID key stroke")
    (options, args) = parser.parse_args()
    if options.challenge == None:
        print parser.usage
        exit(0)

    global d, q, challenge

    d = options.debug
    q = options.quack
    #set challenge string
    challenge = options.challenge
    #start listening for new USB devices
    detect_hot_plug()

if __name__ == "__main__":
    main()
