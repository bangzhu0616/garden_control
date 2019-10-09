from datetime import datetime

import sqlite3
import os

import RPi.GPIO as GPIO
import Adafruit_DHT

from status import set_status


light = 17
heater = 27
sensor = 4
light_on_start = 10
light_on_end = 16
db_name = 'database.db'

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(light, GPIO.OUT)
GPIO.setup(heater, GPIO.OUT)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = sensor

conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + '/database.db')
c = conn.cursor()

light_is_on = GPIO.input(light)
heater_is_on = GPIO.input(heater)

now_year = datetime.now().year
now_month = datetime.now().month
now_day = datetime.now().day
now_hour = datetime.now().hour
now_minute = datetime.now().minute
light_should_on_now = light_on_start <= now_hour < light_on_end

humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
temperature_too_low = temperature < 15
temperature_too_high = temperature > 23

light_status, heater_status = set_status(light_is_on,
                                         heater_is_on,
                                         light_should_on_now,
                                         temperature_too_low,
                                         temperature_too_high)
try:
    GPIO.output(light, light_status)
    GPIO.output(heater, heater_status)
except:
    pass

c.execute('insert into sensor_data values (%s, %s, %s, %s, %s, %s, %s)' % (str(now_year), str(now_month), str(now_day), str(now_hour), str(now_minute), '%.1f'%(temperature), '%.1f'%(humidity)))
conn.commit()

c.execute('select count(*) from heater_stat where year=%s and month=%s and day=%s' % (str(now_year), str(now_month), str(now_day)))
count = cursor.fetchone()[0]
if count == 0:
    if heater_is_on and not heater_status:
        c.execute('insert into heater_status values (%s, %s, %s, %s, %s, %s, %s, %s)' % (str(now_year), str(now_month), str(now_day), '0', '0', str(now_hour), str(now_minute)))
    if heater_is_on and heater_status:
        c.execute('insert into heater_status (year, month, day, start_hour, start_minute) values (%s, %s, %s, %s, %s, %s, %s, %s)' % (str(now_year), str(now_month), str(now_day), '0', '0'))
else:
    if not heater_is_on and heater_status:
        c.execute('insert into heater_status (year, month, day, start_hour, start_minute) values (%s, %s, %s, %s, %s, %s, %s, %s)' % (str(now_year), str(now_month), str(now_day), str(now_hour), str(now_minute)) )
    if heater_is_on and not heater_status
        c.execute('update heater_stat set end_hour=%s end_minute=%s where id=(select MAX(id) from heater_stat where year=%s and month=%s and day=%s)' % (str(now_hour), str(now_minute), str(now_year), str(now_month), str(now_day)))
conn.commit()

conn.close()