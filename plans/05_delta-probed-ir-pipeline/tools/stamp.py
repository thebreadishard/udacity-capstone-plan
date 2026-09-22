"""Print the ledger time stamp from the clock, never from memory (22 September 2026: four stamps were written ahead of the clock that day).

    python tools/stamp.py          -> 17:5x          (the form the ledger uses: hour, tens of minutes, x)
    python tools/stamp.py --date   -> 2026-09-22 17:5x
    python tools/stamp.py --full   -> 2026-09-22 17:53:07 +0200  (for blog front matter, two minutes behind the clock so Pages never sees a future date)

Patch scripts take the stamp as their argument: `python patch_x.py "$(python tools/stamp.py)"`.
"""
import sys
from datetime import datetime, timedelta

now = datetime.now().astimezone()
if "--full" in sys.argv:
    print((now - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S %z"))
elif "--date" in sys.argv:
    print(now.strftime("%Y-%m-%d %H:%M")[:-1] + "x")
else:
    print(now.strftime("%H:%M")[:-1] + "x")
