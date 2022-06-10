#!/bin/bash 

useradd -m --no-log-init --system --uid 1000 foobob -s /bin/bash -g sudo -G root
echo 'foobob:foobob' | chpasswd
