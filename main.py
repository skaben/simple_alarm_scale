import  time, math, ujson, network
import umqttsimple 
import config 

timeData = {'On':config.TIMEON, 'Off':config.TIMEOFF,
            'Flag':'On', 'color':{'On':[0,0,0], 'Off':[0,0,0]},
            'numLEDs':0, 'Prev':0, 'Current':0}

newCom = {'borders':[50,100,150], 'level':0, 'state':'blue'}

def parse_command(command):

    for t in command:
        newCom[t] = command[t]
    print(newCom)
    if newCom['level'] < newCom['borders'][0]:
        timeData['numLEDs'] = int(newCom['level']/newCom['borders'][0]*16)
        timeData['color']['On'] = (0,config.FULLB,0)
    elif newCom['level'] in range(newCom['borders'][0], newCom['borders'][1]):
        rel_level = newCom['level']-newCom['borders'][0]
        rel_range = newCom['borders'][1]-newCom['borders'][0]
        timeData['numLEDs'] = int(rel_level/rel_range*16)+1
        timeData['color']['On'] = (config.HALFB,config.HALFB,0)
    else:
        rel_level = newCom['level']-newCom['borders'][1]
        rel_range = newCom['borders'][2]-newCom['borders'][1]
        timeData['numLEDs'] = int(rel_level/rel_range*16)+1
        if timeData['numLEDs'] >= 16:
            timeData['numLEDs'] = 16
        timeData['color']['On'] = (config.FULLB,0,0)
    if newCom['state'] == 'blue':
        timeData['color']['Off'] = (0,0,config.FULLB)
    elif newCom['state'] == 'lightblue':
        timeData['color']['Off'] = (0,config.HALFB,config.HALFB)
    else:
        timeData['color']['Off'] = timeData['color']['On']
  
def mqtt_callback(topic, msg):
    if topic in (config.topics['sub'], config.topics['sub_id']):
        print(msg)
        try:
            command = ujson.loads(msg)
            parse_command(command)
        except:
            time.sleep(.2)
            return
    
def connect_and_subscribe():
    server = config.cfg.get('broker_ip')
    client = umqttsimple.MQTTClient(config.cfg.get('client_id'), server)
    client.set_callback(mqtt_callback)
    client.connect()
    sub_topics = [config.topics[t] for t in config.topics if 'sub' in t]
    for t in sub_topics:
        client.subscribe(t)
    print('connected to {}, subscribed to {}'.format(server, sub_topics))
    for i in range (config.LINELEN):
        config.scale[i] = (0,0,0)
    config.scale.write()
    cmd_out = 'CUP/{"lts":"'+str(time.ticks_ms())+'"}'
    client.publish(config.topics['pub_id'], cmd_out)
    return client

def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    for x in range(10):
        config.scale[0]=(0,255,0)
        config.scale.write()
        time.sleep_ms(250)
        config.scale[0]=(0,0,0)
        config.scale.write()
        time.sleep_ms(250)
    machine.reset()
    
def wifi_init():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(config.cfg['wlan_ssid'], config.cfg['wlan_password'])
    while station.isconnected() == False:
        for x in range (4):
            config.scale[0]=(255,0,0)
            config.scale.write()
            time.sleep_ms(250)
            config.scale[0]=(0,0,0)
            config.scale.write()
            time.sleep_ms(250)
    print('Connection successful')
    print(station.ifconfig())

def main():
    try:
        wifi_init()
    except OSError as e:
        print(e)
        restart_and_reconnect()
    try:
        client = connect_and_subscribe()
    except OSError as e:
        print(e)
        restart_and_reconnect()
    flag_on = 0    
    while True:
        timeData['Current'] = time.ticks_ms()
        try:
            client.check_msg()
            if (timeData['Current'] - timeData['Prev']) >= timeData[timeData['Flag']]:
                timeData['Prev'] = timeData['Current']
                flag_on = (flag_on + 1) % 2
                timeData['Flag'] = config.FLAGS[flag_on]
                for i in range(timeData['numLEDs']):
                    config.scale[i] = timeData['color'][timeData['Flag']]
                for i in range(timeData['numLEDs'], config.LINELEN):
                    config.scale[i] = (0,0,0)
                config.scale.write()
        except OSError as e:
            machine.reset()


main()


