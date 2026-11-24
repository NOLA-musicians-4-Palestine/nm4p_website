#!/bin/bash
echo "copying files to server"
scp automations.py Dockerfile requirements.txt form_submission_payload.json row_update_payload.json nm4p-ovhcloud:automations/

echo "building image on server"
echo "cd automations && sudo docker build . -t automations"
ssh nm4p-ovhcloud "cd automations && sudo docker build . -t automations"

#ssh nm4p-ovhcloud "sudo docker container stop nextcloud-automations"

echo "run automations container"

# Run once and watch
# ssh -t nm4p-ovhcloud "sudo docker compose -f automations/compose.yaml run --rm --name nextcloud-automations nextcloud-automations"

# run auto-restart detached
ssh nm4p-ovhcloud "sudo docker compose -f automations/compose.yaml down"
ssh nm4p-ovhcloud "sudo docker compose -f automations/compose.yaml up -d"

