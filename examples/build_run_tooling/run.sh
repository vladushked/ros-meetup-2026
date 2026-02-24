#!/usr/bin/env bash

set -e

DEFAULT_PACKAGE="system_bringup"
VISUALIZE="false"
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v)
      VISUALIZE="true"
      shift
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}"

PACKAGE="${1:-$DEFAULT_PACKAGE}"
LAUNCH_FILE="${2:-$PACKAGE}"

if ! ros2 pkg list | grep -wq "^$PACKAGE$"; then
  echo "Package '$PACKAGE' not found"
  exit 1
fi

PKG_PREFIX=$(ros2 pkg prefix "$PACKAGE")
LAUNCH_DIR="$PKG_PREFIX/share/$PACKAGE/launch"

if [ ! -f "$LAUNCH_DIR/$LAUNCH_FILE.launch.py" ]; then
  echo "Launch file '$LAUNCH_FILE.launch.py' not found in $LAUNCH_DIR"
  exit 1
fi

mkdir -p debug/console_logs
export ROS_LOG_DIR="$PWD/debug/console_logs/$(date +%Y%m%d_%H%M%S)"

ros2 launch "$PACKAGE" "$LAUNCH_FILE.launch.py" "visualize:=$VISUALIZE" 2>&1 \
  | tee "$ROS_LOG_DIR/console_output.log"
