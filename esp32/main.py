import math
import time
from machine import ADC
from machine import deepsleep
import ntptime
from umqtt.simple import MQTTClient

## mq135 to pin 34
## buzzer to pin 32

## ID 
id_esp32 = 1

def start_mq135():
    """MQ135 lib example"""
    time.sleep(5)
    led = machine.Pin(2, machine.Pin.OUT)
    led.value(0)
    failcount = 0
    while True:
    #time
        try:
            ntptime.settime()	# this queries the time from an NTP server
            break 
        except:
            print("ntp fail : 1")
            if (failcount==3):
                print("restarting...")
                deepsleep(10)
                break
            failcount = failcount+1
            led.value(1)
            time.sleep(5)
            led.value(0)
            
    #connected feedback
    led.value(1)
    time.sleep(0.5)
    led.value(0)
    
    UTC_OFFSET = 7 * 60 * 60   # change the '-4' according to your timezone
    actual_time = time.localtime(time.time() + UTC_OFFSET)
    [year , month , day , hour , minute , second , x , y ] = actual_time
    
    # mqtt subscription
    topic_state = 'hivemq/state'
    topic_data = 'hivemq/data'
#     mqttc.set_callback(callback_prod)
#     mqttc.subscribe(topic_command)
    
    CLIENT_NAME = b'CLIENT_NAME'
    BROKER_ADDR = b'BROKER_ADDR'
    USER_NAME = b'USER_NAME'
    USER_PASS = b'USER_PASS'
    mqttc = MQTTClient(CLIENT_NAME,
                       BROKER_ADDR,
                       port=8883,
                       user=USER_NAME,
                       password=USER_PASS,
                       keepalive=60,
                       ssl=True,
                       ssl_params={'server_hostname':'server_hostname'})
    print("init mqtt connect")
    
    while True:
        try:
            mqttc.connect()
            time.sleep(1)
            mqttc.publish( topic_state,(str(day)+','+str(hour)+','+str(minute)+','+str('loopstart')+','+str(id_esp32)).encode() )
            time.sleep(1)
            mqttc.disconnect()
            break 
        except:
            print("Mqtt conn fail : 1")
            led.value(1)
            time.sleep(5)
            led.value(0)
    
    pin = machine.Pin(34, machine.Pin.IN)
    pin_buzzer = machine.Pin(32, machine.Pin.OUT)
    adc = ADC(pin)  # create an ADC object acting on a pin
    
    print(actual_time)
    
    while True:
        
        actual_time = time.localtime(time.time() + UTC_OFFSET)
        [year , month , day , hour , minute , second , x , y ] = actual_time

#         5 minute interval
        mintosleep = 0
        minute_modulo = minute % 5
        if (minute_modulo == 0):
            print('a1')
            print(str(hour)+','+str(minute))
            val = adc.read()
            
            print("MQ135 analog to digital value:" + str(val))
            if (val>1000):
                pin_buzzer.value(1)
                time.sleep(1)
                pin_buzzer.value(0)
                time.sleep(1)
                pin_buzzer.value(1)
                time.sleep(1)
                pin_buzzer.value(0)
            
            #reconnect
            mqttc = MQTTClient(CLIENT_NAME,
                       BROKER_ADDR,
                       port=8883,
                       user=USER_NAME,
                       password=USER_PASS,
                       keepalive=60,
                       ssl=True,
                       ssl_params={'server_hostname':'server_hostname'})
            print("init mqtt connect")
            failcount = 0
            while True:
                try:
                    mqttc.connect()
                    print("sending data")
                    time.sleep(1)
                    mqttc.publish( topic_state,(str(day)+','+str(hour)+','+str(minute)+','+str('sendingval')+','+str(id_esp32)).encode() )
                    time.sleep(1)
                    mqttc.publish( topic_data,(str(month)+','+str(day)+','+str(hour)+','+str(minute)+','+str(val)+','+str(id_esp32)).encode() )
                    time.sleep(1)
                    mqttc.publish( topic_state,(str(month)+','+str(day)+','+str(hour)+','+str(minute)+','+str(val)+','+str(id_esp32)).encode() )
                    time.sleep(1)
                    mqttc.disconnect()
                    break 
                except:
                    print("Mqtt conn fail : 2")
                    if (failcount==5):
                        break
                    failcount = failcount+1
                    led.value(1)
                    time.sleep(5)
                    led.value(0)
                    
            print("start deepsleep")
            
            actual_time = time.localtime(time.time() + UTC_OFFSET)
            [year , month , day , hour , minute , second , x , y ] = actual_time
            
            minute_modulo = minute % 5
            mintosleep = 3 - minute_modulo
            if (mintosleep < 0):
                mintosleep = 0
            if (mintosleep!=0):
                deepsleep(mintosleep*60 * 1000)    #deepsleep milisecond
        else : 
            print('a2')
            mintosleep = 3 - minute_modulo
            if (mintosleep < 0):
                mintosleep = 0
            print((mintosleep*60)  + (60-second))
            time.sleep((mintosleep*60)  + (60-second)) 
            
        print(str(second)+','+'a4')
        time.sleep(10)
#         time.sleep(mintosleep*60)
    
if __name__ == "__main__":
    start_mq135()
    
    

    