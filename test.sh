#!/bin/bash

for t in {1..5}
do
    python3 client.py 0 lowint$t & python3 client.py 1 lowint$t & python3 client.py 2 lowint$t
    sleep 1
done