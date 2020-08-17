#!/usr/bin/env bash
# -----
# -v VERSION
set -e

VERSION="BETA"

while [[ $# -gt 0 ]]
do
  case "$1" in
    "--version")
      VERSION="$2"
      shift
      ;;
    *)
      echo "$1 $0 -v|--version" && exit 1
      ;;
  esac
  shift
done

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
application=newsrooom

echo "Building app container"
(cd $script_dir/.. && docker build -t ${application}/api:$VERSION -f api/Dockerfile .)
# (cd $script_dir/.. && docker build -t ${application}/cron:$VERSION -f cron/Dockerfile .)
(cd $script_dir/../frontend && docker build -t ${application}/frontend:$VERSION .)

# tag application version -> latest
docker tag ${application}/api:$VERSION ${application}/api:latest
# docker tag ${application}/cron:$VERSION ${application}/cron:latest
docker tag ${application}/frontend:$VERSION ${application}/frontend:latest
