from datetime import datetime, timedelta
import sqlite3


conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + '/database.db')
c = conn.cursor()

yesterday = datetime.now() - timedelta(1)
yesterday_year = yesterday.year
yesterday_month = yesterday.month
yesterday_day = yesterday.day

