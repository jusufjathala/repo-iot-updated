from flask import Flask,render_template,request
import paho.mqtt.client as mqtt
import logging
import time
import pymysql
import pymysql.cursors
application = app = Flask(__name__)

message_received = ""
state = ""

def on_connect(client,userdata,flags,rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hivemq/data")

def on_message(client,userdata,msg):
    try:
        global message_received
        topic = msg.topic
        message_received = msg.payload.decode('utf-8')
        
        #parse message
        message_list = message_received.split(",")
        month=message_list[0]
        day=message_list[1]
        hour=message_list[2]
        minute=message_list[3]
        value=message_list[4]
        id_esp32=message_list[5]
        
        sql = '''insert into mq135_data(month, day, hour, minute, value, id_esp32)
VALUES (%d, %d, %d, %d, %d, %d)''' % (int(month), int(day), int(hour), int(minute), int(value), int(id_esp32))

        cursor.execute(sql)
        connection.commit()
        
    except Exception as e:
        print("error",e)

def on_disconnect(client, userdata,rc=0):
    logging.debug("DisConnected result code "+str(rc))
    client.loop_stop()
    
    
# mysql init
connection = pymysql.connect(host='host',
                     port = 3306 ,
                     user='user',
                     password='password',
                    #  database='db',
                     cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

sql = "create database if not exists mq135;"
cursor.execute(sql)
sql = "use mq135;"
cursor.execute(sql)
# print(data)
sql = '''create table if not exists mq135_data (
    id int not null auto_increment,
    month int,
    day int,
    hour int,
    minute int,
    value int,
    id_esp32 int,
    primary key(id)
    );'''
cursor.execute(sql)

#mqtt init
client= mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set("username_pw_set","username_pw_set")
# client.loop_start()
client.connect("client.connect",8883,60)
            

@application.route('/', methods =["GET", "POST"])
def index():
    
    if request.method == 'POST':
        while True :
            time.sleep(60) #wait
            client.loop_start() #start the loop
            client.publish("hivemq/test", payload="db_receiv_on", qos=0)
            print("mesg receiv: "+str(message_received))
            time.sleep(60) #wait
            client.loop_stop()
    
    return render_template('index.html')
