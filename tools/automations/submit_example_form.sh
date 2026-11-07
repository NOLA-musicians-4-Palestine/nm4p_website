#!/bin/bash

ssh -t nm4p-ovhcloud "sudo docker exec -it nextcloud-automations curl -X POST localhost:8080/form_submitted -H 'Content-Type: application/json' --data @example_payload.json"
