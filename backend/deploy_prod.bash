#!/bin/bash

# 현재 스크립트가 위치한 디렉토리를 기준으로 PYTHONPATH 설정
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
export PYTHONPATH=$SCRIPT_DIR

git pull

pip install -r req.txt

pm2 delete api
pm2 start "gunicorn --workers 9 --bind 0.0.0.0:9000 run:app" --name backend