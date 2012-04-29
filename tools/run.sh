#!/bin/sh

if [ "${1}" == "su" ]; then
    shift
    su -c "$*"
else
    exec "$@"    
fi
