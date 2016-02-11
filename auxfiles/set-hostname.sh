#!/bin/bash

localip=\`ip -o -4 a s | awk -F'[ /]+' '\$2!~/lo/{print \$4}'\`
[ -z "\`grep \$localip /etc/hosts\`" ] && echo -e "\\n\$localip \$1 \${1%%.*}" >> /etc/hosts
