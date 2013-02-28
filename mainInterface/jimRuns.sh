#! /bin/sh -x

# Doesn't yet work!!!!!!!!!

export DATE=`date +%y%m%d_%H%M%S`
m4 -D TIMESTAMP=$DATE timestamp.html > current.html
scp current.html yosinski.com:s.yosinski.com/web
./jimRuns.py "$1" "\""$2""\" "$DATE" "$4"
