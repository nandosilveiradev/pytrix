#!/bin/bash
gcc /root/pytrix/pytrix_utils/c/px-code.c -o /root/pytrix/pytrix_bin/utils/px-code -lncurses -no-pie

cp -f /root/pytrix/pytrix_bin/utils/px-code /bin/px-code