#!/bin/bash
echo "building local image"
podman build -t automations .

echo "run container"
podman run -p 8080:8080 -it --rm --name nextcloud-automations localhost/automations:latest

