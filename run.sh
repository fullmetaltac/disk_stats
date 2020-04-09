#!/bin/bash

if [ "$1" == "" ]; then
    echo "Requires disk parameter for testing [ e.g ./run.sh disk1s3]"
    exit 1
fi

brew list fio || brew install fio
brew list ioping || brew install ioping
brew list smartmontools || brew install smartmontools

docker-compose up -d

while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:4000)" != "302" ]]; do echo 'Waiting grafana...'; sleep 1; done
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:9086)" != "404" ]]; do echo 'Waiting influxdb...'; sleep 1; done

curl -XPOST 'http://localhost:9086/query' --data-urlencode 'q=CREATE DATABASE temp_db'
echo -e '\n'

curl -XPOST -u admin:admin  http://localhost:4000/api/datasources -H "content-type: application/json"  -d @./datasource.json
echo -e '\n'

curl -XPOST -u admin:admin  http://localhost:4000/api/dashboards/db -H "content-type: application/json"  -d @./dashboard.json
echo -e '\n'

python3 influx.py $1
