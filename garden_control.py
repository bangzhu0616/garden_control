from datetime import datetime, timedelta

import sqlite3
import os
import time

import RPi.GPIO as GPIO
import Adafruit_DHT

from utils import set_status

with open(os.path.dirname(os.path.abspath(__file__)) + '/config') as fp:
    config = [int(c) for c in fp.read().split(',')]

light = 17
heater = 27
sensor = 4
[light_on_start1, light_on_end1, light_on_start2, light_on_end2, temperature_low_bound, temperature_high_bound] = config

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(light, GPIO.OUT)
GPIO.setup(heater, GPIO.OUT)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = sensor

conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + '/garden.db')
c = conn.cursor()

light_is_on = GPIO.input(light)
heater_is_on = GPIO.input(heater)

now = datetime.now()
yesterday = now - timedelta(1)
light_should_on_now = light_on_start1 <= now.hour < light_on_end1 or light_on_start2 <= now.hour < light_on_end2

humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
temperature_too_low = temperature < temperature_low_bound
temperature_too_high = temperature > temperature_high_bound

light_status, heater_status = set_status(light_is_on,
                                         heater_is_on,
                                         light_should_on_now,
                                         temperature_too_low,
                                         temperature_too_high)
try:
    GPIO.output(light, light_status)
    GPIO.output(heater, heater_status)
except:
    print("set light or heater status error")

c.execute('insert into sensor_data (time, temperature, humidity) values ("%s", %s, %s)' % (now.strftime('%Y-%m-%dT%H:%M'), '%.1f'%(temperature), '%.1f'%(humidity)))
conn.commit()

c.execute('select count(*) from heater_stat where strftime("%Y-%m-%d", start_time)="' + now.strftime("%Y-%m-%d") + '"')
count = c.fetchone()[0]
if count == 0:
    if heater_is_on:
        c.execute('select * from heater_stat where id=(select MAX(id) from heater_stat)')
        current = c.fetchone()
        diff = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59) - datetime.strptime(current[1], '%Y-%m-%dT%H:%M')
        running = divmod(diff.total_seconds(), 60)[0] + 1
        c.execute('update heater_stat set end_time="%s" where where id=(select MAX(id) from heater_stat)' % (yesterday.strftime('%Y-%m-%dT23:59')))
    if heater_is_on and not heater_status:
        diff = datetime(now.year, now.month, now.day, now.hour, now.minute) - datetime(now.year, now.month, now.day, 0, 0)
        running = divmod(diff.total_seconds(), 60)[0]
        c.execute('insert into heater_stat (start_time, end_time, running) values ("%s", "%s", %s)' % (now.strftime('%Y-%m-%dT00:00'), now.strftime('%Y-%m-%dT%H:%M'), str(diff)))
    if heater_is_on and heater_status:
        c.execute('insert into heater_stat (start_time) values ("%s")' % (now.strftime('%Y-%m-%dT00:00')))
    if not heater_is_on and heater_status:
        c.execute('insert into heater_stat (start_time) values ("%s")' % (now.strftime('%Y-%m-%dT%H:%M')))
else:
    if not heater_is_on and heater_status:
        c.execute('insert into heater_stat (start_time) values ("%s")' % (now.strftime('%Y-%m-%dT%H:%M')))
    if heater_is_on and not heater_status:
        c.execute('select * from heater_stat where id=(select MAX(id) from heater_stat)')
        current = c.fetchone()
        diff = datetime(now.year, now.month, now.day, now.hour, now.minute) - datetime.strptime(current[1], '%Y-%m-%dT%H:%M')
        running = divmod(diff.total_seconds(), 60)[0]
        c.execute('update heater_stat set end_time="%s", running_time=%s where id=(select MAX(id) from heater_stat)' % (now.strftime('%Y-%m-%dT%H:%M'), str(running)))
conn.commit()

conn.close()


