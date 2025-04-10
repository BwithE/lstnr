#!/bin/bash

# Create the shared volume (this will not overwrite existing volumes)
docker volume create shared-tools

# Build and run the uppy container in the background
docker build -t uppy ./uppy
docker run -d --name uppy \
  -p 80:80 \
  -v shared-tools:/opt/tools \
  uppy

# Wait for a few seconds to ensure uppy is up and running
sleep 5

# Build and run the lstnr container interactively
docker build -t lstnr ./lstnr
docker run -it --name lstnr \
  -p 443:443 \
  -v shared-tools:/opt/tools \
  lstnr
