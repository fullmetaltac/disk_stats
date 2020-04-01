#!/bin/bash

docker-compose up -d

while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:4000)" != "302" ]]; do echo 'Waiting grafana...'; sleep 1; done
while [[ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:9086)" != "404" ]]; do echo 'Waiting influxdb...'; sleep 1; done

echo
curl -XPOST 'http://localhost:9086/query' --data-urlencode 'q=CREATE DATABASE temp_db'

echo

curl -XPOST -u admin:admin  http://localhost:4000/api/datasources -H "content-type: application/json"  -d @./datasource.json

echo
curl -XPOST -u admin:admin  http://localhost:4000/api/dashboards/db -H "content-type: application/json"  -d @./dashboard.json

python3 influx.py $0