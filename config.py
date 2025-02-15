import machine
import neopixel
from network import WLAN
from ubinascii import hexlify

ENV = 'dev'  

LINELEN = 16
LINEPIN = 12

FLAGS = ['On', 'Off']

cfg = {
    'client_id': hexlify(machine.unique_id()),
    'mac': hexlify(WLAN().config('mac')),
    'last_message': 0,
    'message_interval': 5,
    'counter': 0,
    'wlan_ssid': 'ArmyDep',  
    'wlan_password': 'z0BcfpHu'
}

scale = neopixel.NeoPixel(machine.Pin(LINEPIN), LINELEN)

topics = {
    'sub': b'scale',
    'pub': b'ask/scale',
    'pub_id': b'ask/scale/' + cfg['mac'],
    'sub_id': b'scale/' + cfg['mac']
}

FULLB = 32
HALFB = 32

TIMEON = 250
TIMEOFF = 250


