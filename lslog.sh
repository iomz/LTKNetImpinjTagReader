#!/bin/sh
ls -l logs/ | egrep -v 'raw|tmp|total|^[[:space:]]*$' | awk '{print $9}' | sort -V
