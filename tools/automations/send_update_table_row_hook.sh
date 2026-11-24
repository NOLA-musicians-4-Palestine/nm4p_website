#!/bin/bash

echo "copying files to server"
scp row_update_payload.json nm4p-ovhcloud:automations/

ssh -t nm4p-ovhcloud "sudo docker exec -it nextcloud-automations curl -X POST localhost:8080/approval_table_updated -H 'Content-Type: application/json' --data @row_update_payload.json"
