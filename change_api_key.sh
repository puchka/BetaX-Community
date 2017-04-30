#!/usr/bin/env bash

for y in `ls *`;
do sed "s/YOUR_API_KEY/YOUR_NEW_API_KEY/g" $y > temp; mv temp $y;
done
