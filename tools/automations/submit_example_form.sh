#!/bin/bash

echo "copying files to server"
scp form_submission_payload.json nm4p-ovhcloud:automations/

ssh -t nm4p-ovhcloud "sudo docker exec -it nextcloud-automations curl -X POST localhost:8080/form_submitted -H 'Content-Type: application/json' --data @form_submission_payload.json"
