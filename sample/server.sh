#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR
protoc --python_out=./ -I./ ./test.proto
PYTHONPATH=${PYTHONPATH}:../ python server.py
