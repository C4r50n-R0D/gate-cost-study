#!/bin/sh
# Downloads BigCodeBench v0.1.4 at the pinned revision and checks its SHA-256. Needs network; run it once, outside the scoring container.
set -e
mkdir -p data
URL=https://huggingface.co/datasets/bigcode/bigcodebench/resolve/b74c0d0bf70d2c0bc459be537895cca163007f1a/data/v0.1.4-00000-of-00001.parquet
curl -L -o data/v0.1.4.parquet "$URL"
echo "d9a4965821c9507ebdfb551c288656b2d5fe553234f5183044333ca8a4018267  data/v0.1.4.parquet" | shasum -a 256 -c -
