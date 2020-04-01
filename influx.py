import datetime
import os
import platform
import subprocess
import sys
from datetime import datetime
from multiprocessing import Process
from os import popen
from time import sleep

from influxdb import InfluxDBClient


def shell(cmd: str):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    return process.stdout.read().decode('utf-8').strip()


client = InfluxDBClient(host='localhost', port=9086)
client.switch_database('temp_db')


def log_temp(disk: str):
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


def fio(disk: str):
    shell(f"fio --name=random-write --ioengine=posixaio --rw=randwrite --bs=1m --size=1g --numjobs=1 --iodepth=1 --runtime=60 --time_based --end_fsync=1 > /dev/null 2>&1")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Should specify disk to test')
        exit()
    disk = sys.argv[1]
    fio_process = Process(target=fio, args=(disk,))
    fio_process.start()

    while fio_process.is_alive():
        log_temp(disk)
