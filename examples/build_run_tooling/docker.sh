#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$PROJ_DIR/.env"

if [ -f "$ENV_FILE" ]; then
  while IFS='=' read -r key value || [[ -n "$key" ]]; do
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    if [[ "$key" == "UID" ]]; then
      export HOST_UID="$value"
    else
      export "$key=$value"
    fi
  done < "$ENV_FILE"
fi

ROS_DOMAIN_ID="${1:-${ROS_DOMAIN_ID:-52}}"
HOST_UID="${HOST_UID:-$(id -u)}"
USER_NAME="${USER_NAME:-docker}"
PROJECT_NAME="${PROJECT_NAME:-workspace}"
IMAGE_URL="${IMAGE_URL:-example/ros2-dev:latest}"

if [[ -n "$DISPLAY" ]]; then
  X11_PARAMS="--env=DISPLAY --env=QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix"
else
  X11_PARAMS=""
fi

docker run --rm -it \
  --privileged \
  --net=host \
  --ipc=host \
  ${X11_PARAMS} \
  -e UID="$HOST_UID" \
  -e USER_NAME="$USER_NAME" \
  -e ROS_DOMAIN_ID="$ROS_DOMAIN_ID" \
  -v "$PROJ_DIR":/workspace \
  -w /workspace \
  "$IMAGE_URL"
