#!/bin/bash

ssh -t ovh-vps3 "sudo docker exec -it nextcloud-automations curl -X POST localhost:8080/form_submitted -H 'Content-Type: application/json' --data @example_payload.json"
