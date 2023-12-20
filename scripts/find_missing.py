#!/usr/bin/env python3
# Author: Sean Pesce

"""
Iterate through dates to determine which daily Ghost Network configurations are missing

Note that Ghost Networks were seemingly never generated (by Eidos/Square Enix) for the following date ranges:
    [2020-08-11, 2020-08-26]
    [2020-11-19, 2020-11-23]
    [2020-12-01, 2020-12-06]

Therefore, this script will always determine that there are at least 27 missing Ghost Networks.

Evidence for missing Ghost Networks:
    August/November 2020: https://steamcommunity.com/app/337000/discussions/0/3862353324242873119/
    August/December 2020: https://forum.psnprofiles.com/topic/93516-when-do-breach-ghost-nodes-decrypt/
    November 2020: https://old.reddit.com/r/Deusex/comments/jzvrn3/dxmd_breach_offline_again/
"""

import os
import sys
from datetime import datetime, timedelta


MISSING_NETWORKS = []
DIR = ''
FNAME_PREFIX = ''
# Release date of Ghost Networks feature:
# https://www.rockpapershotgun.com/deus-ex-breach-launches-random-daily-networks
START_DATE = datetime(2017, 2, 14)


if __name__ == '__main__':
    now = datetime.now()
    END_DATE = datetime(now.year, now.month, now.day)  # Today
    END_DATE += timedelta(days=1)  # Tomorrow
    
    if '-h' in sys.argv or '--help' in sys.argv:
        print(f'Usage:\n\n{sys.argv[0]} [Ghost Networks directory]\n\nIf no folder path is provided, the script checks the current working directory for Ghost Network configurations.\n')
        sys.exit()
    
    if len(sys.argv) > 1:
        DIR = sys.argv[1]

    cur_day = START_DATE
    while cur_day != END_DATE:
        date_str = f'{cur_day.year}-{cur_day.month:02}-{cur_day.day:02}'
        fname = f'{FNAME_PREFIX}{date_str}.json'
        fname = os.path.join(DIR, fname)

        if not os.path.exists(fname):
            MISSING_NETWORKS.append(date_str)
            print(date_str)

        cur_day += timedelta(days=1)

    print(f'\n{len(MISSING_NETWORKS)} missing')
