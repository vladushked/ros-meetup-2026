#!/usr/bin/env bash

set -e

PACKAGES_SKIP="0"
MAKE_JOBS=""
COLCON_WORKERS=""
CLEAN="0"
PACKAGES_UPTO="0"
VERBOSE="0"
ROSDEP_INSTALL="0"

show_help() {
  cat <<HELP
Usage: $(basename "$0") [OPTIONS] [PACKAGES...]

Build ROS 2 workspace with utility flags.

Options:
  -c        Clean workspace or selected packages
  -j N      Parallel make jobs
  -w N      colcon parallel workers
  -p        Run rosdep install before build
  -u        Build packages and their dependencies
  -v        Verbose output (console_direct+)
  -x        Skip selected packages
  -h        Show help
HELP
}

while getopts "cxj:w:uvph" opt; do
  case $opt in
  h) show_help; exit 0 ;;
  c) CLEAN="1" ;;
  j) MAKE_JOBS="$OPTARG" ;;
  w) COLCON_WORKERS="$OPTARG" ;;
  u) PACKAGES_UPTO="1" ;;
  v) VERBOSE="1" ;;
  p) ROSDEP_INSTALL="1" ;;
  x) PACKAGES_SKIP="1" ;;
  *) show_help; exit 1 ;;
  esac
done

shift $((OPTIND - 1))
PACKAGES=("$@")

if [ "$CLEAN" = "1" ]; then
  if [ "${#PACKAGES[@]}" -eq 0 ]; then
    rm -rf install build log
  else
    for package in "${PACKAGES[@]}"; do
      rm -rf "install/$package" "build/$package"
    done
  fi
  exit 0
fi

if [ "$ROSDEP_INSTALL" = "1" ]; then
  sudo apt update
  rosdep update
  rosdep install -y --from-paths . --ignore-src --rosdistro "$ROS_DISTRO"
fi

BUILD_ARGS=("--symlink-install")

if [ -n "$COLCON_WORKERS" ]; then
  BUILD_ARGS+=("--parallel-workers" "$COLCON_WORKERS")
fi

if [ "$VERBOSE" = "1" ]; then
  BUILD_ARGS+=("--event-handlers" "console_direct+")
fi

if [ "${#PACKAGES[@]}" -ne 0 ]; then
  if [ "$PACKAGES_SKIP" = "1" ]; then
    BUILD_ARGS+=("--packages-skip")
  elif [ "$PACKAGES_UPTO" = "1" ]; then
    BUILD_ARGS+=("--packages-up-to")
  else
    BUILD_ARGS+=("--packages-select")
  fi
  BUILD_ARGS+=("${PACKAGES[@]}")
fi

MAKE_FLAGS=""
if [ -n "$MAKE_JOBS" ]; then
  MAKE_FLAGS="-j${MAKE_JOBS} -l${MAKE_JOBS}"
fi

MAKEFLAGS="$MAKE_FLAGS" colcon build "${BUILD_ARGS[@]}"
