import machine, time, math, ujson, network, urandom
import ubinascii, micropython, neopixel
from umqttsimple import MQTTClient

ssid = 'P2797-24'
password = 'z0BcfpHu'
mqtt_server = '192.168.137.1'

topic_sub = b'SCALE'
topic_pub = b'SCALEASK'

last_message = 0
message_interval = 5
counter = 0

timeSlice = dict()
timeSlice['On'] = 250
timeSlice['Off'] = 250
timeFlag = 'On'

color = dict()
color['On'] = (0,0,0)
color['Off'] = (0,0,0)
numLEDs = 0

scale = neopixel.NeoPixel(machine.Pin(5), 16)
client_id = ubinascii.hexlify(machine.unique_id())
station = network.WLAN(network.STA_IF)

newCom = dict()
newCom['borders'] = (50,100,150)

timePrev = 0

def parse_command():
  global newCom, color, numLEDs
  if 'level' in newCom:
    if newCom['level'] < newCom['borders'][0]:
      numLEDs = int(newCom['level']*16/newCom['borders'][0])
      color['On'] = (0,32,0)
    elif newCom['level'] >= newCom['borders'][0] and newCom['level'] < newCom['borders'][1]:
      numLEDs = int((newCom['level']-newCom['borders'][0])*16/(newCom['borders'][1]-newCom['borders'][0]))+1
      color['On'] = (16,16,0)
    else:
      numLEDs = int((newCom['level']-newCom['borders'][1])*16/(newCom['borders'][2]-newCom['borders'][1]))+1
      print(numLEDs)
      if numLEDs >= 16:
        numLEDs = 16
      color['On'] = (32,0,0)
    if 'state' in newCom:  
      # set new color state
      if newCom['state'] == 'RESET':
        machine.reset()
      elif newCom['state'] == 'blue':
        color['Off'] = (0,0,32)
      elif newCom['state'] == 'lightblue':
        color['Off'] = (0,16,16)
      else:
        color['Off'] = color['On']
  
def sub_cb(topic, msg):
  global myMAC, topic_sub, topic_sub_id, newCom
  print(msg)
  if topic == topic_sub or topic == topic_sub_id:
    try:
      newCom = ujson.loads(msg)
    except:
      time.sleep_ms(200)
      return
    parse_command()
    
def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub, myMAC
  global redPWM, greenPWM, bluePWM
  client = MQTTClient(client_id, mqtt_server)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  client.subscribe(topic_sub_id)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub_id))
  client.publish(topic_pub+'/'+myMAC, 'CUP/{"lts":"'+str(time.ticks_ms())+'"}')
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  for x in range(10):
    scale[0]=(0,255,0)
    scale.write()
    time.sleep_ms(250)
    scale[0]=(0,0,0)
    scale.write()
    time.sleep_ms(250)
  machine.reset()

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  for x in range (4):
    scale[0]=(255,0,0)
    scale.write()
    time.sleep_ms(250)
    scale[0]=(0,0,0)
    scale.write()
    time.sleep_ms(250)
  pass
myMAC = ubinascii.hexlify(network.WLAN().config('mac'))  
print('Connection successful')
print(station.ifconfig())
topic_sub_id = b'SCALE/'+myMAC

try:
  client = connect_and_subscribe()
  print ('Connect successfull')
except OSError as e:
  restart_and_reconnect()

while True:
  timeCurrent = time.ticks_ms()
  try:
    client.check_msg()
    if (timeCurrent - timePrev) >= timeSlice[timeFlag]:
      timePrev = timeCurrent
      if timeFlag == 'On':
        timeFlag = 'Off'
        for i in range(numLEDs):
          scale[i] = color['Off']
        for i in range(numLEDs, 16):
          scale[i] = (0,0,0)
      else:
        timeFlag = 'On'
        for i in range(numLEDs):
          scale[i] = color['On']
        for i in range(numLEDs, 16):
          scale[i] = (0,0,0)
      scale.write()
  except OSError as e:
    machine.reset()

