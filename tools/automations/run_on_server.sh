#!/bin/bash
echo "copying files to server"
scp automations.py Dockerfile requirements.txt example_payload.json ovh-vps3:automations/

echo "building image on server"
echo "cd automations && sudo docker build . -t automations"
ssh ovh-vps3 "cd automations && sudo docker build . -t automations"

#ssh ovh-vps3 "sudo docker container stop nextcloud-automations"

echo "run automations container"
echo "sudo docker run --network nextcloud-aio --rm -it --name nextcloud-automations automations:latest"
ssh -t ovh-vps3 "sudo docker run --network nextcloud-aio --rm -it --name nextcloud-automations automations:latest"

