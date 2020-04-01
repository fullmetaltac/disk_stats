import datetime
import os
import platform
import subprocess
from datetime import datetime
from os import popen
from time import sleep

from influxdb import InfluxDBClient

disk = 'disk1s1'


def shell(cmd: str):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read().decode('utf-8').strip()


client = InfluxDBClient(host='localhost', port=9086)
client.switch_database('temp_db')


def log_temp():
    json_body = [
        {
            "measurement": "disk_temp",
            "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "fields": {
                "temp": shell(f"smartctl -a {disk} | grep Temperature |" + "awk '{print $2}'")
            }
        }
    ]

    print(json_body)
    client.write_points(json_body)
    sleep(1)


def fio():
    shell(
        f"fio --name=random-write --ioengine=posixaio --rw=randwrite --bs=1m --size=1g --numjobs=1 --iodepth=1 --runtime=60 --time_based --end_fsync=1 > /dev/null 2>&1")


if __name__ == '__main__':
    fio_process = Process(target=fio)
    fio_process.start()

    while fio_process.is_alive():
        log_temp()
