create table sensor_data (
    id INTEGER primary key,
    year INT,
    month INT,
    day INT,
    hour INT,
    minute INT,
    temperature REAL,
    humidity REAL
);

create table heater_stat (
    id INTEGER primary key,
    year INT,
    month INT,
    day INT,
    start_hour INT,
    start_minute INT,
    end_hour INT,
    end_minute INT,
    electricity_charge REAL
);