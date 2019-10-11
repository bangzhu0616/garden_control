import sqlite3
from datetime import datetime

conn = sqlite3.connect('database.db')
conn2 = sqlite3.connect('garden.db')

c = conn.cursor()
c2 = conn2.cursor()

c.execute('select * from sensor_data')

r = c.fetchall()

for record in r:
    r_time = datetime(record[1], record[2], record[3], record[4], record[5]).strftime("%Y-%m-%dT%H:%M")
    c2.execute('insert into sensor_data (time, temperature, humidity) values ("%s", %s, %s)' % (r_time, str(record[6]), str(record[7])))

conn2.commit()

c.execute('select * from heater_stat')

r = c.fetchall()

for record in r:
    start = datetime(record[1], record[2], record[3], record[4], record[5])
    end = datetime(record[1], record[2], record[3], record[6], record[7])
    diff = end - start
    running = divmod(diff.total_seconds(), 60)[0]
    c2.execute('insert into heater_stat (start_time, end_time, running_time) values ("%s", "%s", %s)' % (start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M"), str(running)))

conn2.commit()

conn.close()
conn2.close()