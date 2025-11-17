
import esp
import uos, machine
import gc
import network
import time

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect('wifiname', 'wifipass')
        while not sta_if.isconnected():
            pass # wait till connection
    print('Connection success, network config:', sta_if.ifconfig())

#esp.osdebug(None)
gc.collect()
time.sleep(5)
connect()
