#!/bin/bash
echo "copying files to server"
scp automations.py Dockerfile requirements.txt example_payload.json nm4p-ovhcloud:automations/

echo "building image on server"
echo "cd automations && sudo docker build . -t automations"
ssh nm4p-ovhcloud "cd automations && sudo docker build . -t automations"

#ssh nm4p-ovhcloud "sudo docker container stop nextcloud-automations"

echo "run automations container"
#echo "sudo docker run --network nextcloud-aio --rm -it --name nextcloud-automations automations:latest"
echo "sudo docker compose -f automations/compose.yaml run --rm --name nextcloud-automations nextcloud-automations"
ssh -t nm4p-ovhcloud "sudo docker compose -f automations/compose.yaml run --rm --name nextcloud-automations nextcloud-automations"

