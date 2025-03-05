#!/bin/bash

for t in {1..5}
do
    python3 client.py 0 normal$t & python3 client.py 1 normal$t & python3 client.py 2 normal$t
done