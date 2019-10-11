create table sensor_data (
    id INTEGER primary key,
    time TEXT,
    temperature REAL,
    humidity REAL
);

create table heater_stat (
    id INTEGER primary key,
    start_time TEXT,
    end_time TEXT,
    running_time REAL
);