@echo off
rem backup_task.cmd (9 Oct 2026; the user: "Ja, maak die geplande taak maar aan") - run by the Windows scheduled task CapstoneDataBackup every night
rem at 03:30 (and at the next start when the laptop was off). Replaces tools/backup_loop.sh, a Git Bash loop that died with an app restart on
rem 29 Sep 2026 and left the capstone-data mirror ten days behind. The log carries every run.
set PYTHONUTF8=1
echo [%date% %time%] backup task start >> "%LOCALAPPDATA%\Temp\claude\backup_task.log"
"C:\Users\thebr\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\tools\backup_data.py" >> "%LOCALAPPDATA%\Temp\claude\backup_task.log" 2>&1
echo [%date% %time%] backup task end, exit %errorlevel% >> "%LOCALAPPDATA%\Temp\claude\backup_task.log"
rem 11 Oct 2026: then every test suite of the repository (tools/run_test_suites.py, about 4 min at idle priority); its own log, so the
rem backup never depends on it. The result lands in probes/watch_state/test_suites.json, which state.sh shows.
echo [%date% %time%] test suites start >> "%LOCALAPPDATA%\Temp\claude\test_suites_task.log"
"C:\Users\thebr\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\tools\run_test_suites.py" >> "%LOCALAPPDATA%\Temp\claude\test_suites_task.log" 2>&1
echo [%date% %time%] test suites end, exit %errorlevel% >> "%LOCALAPPDATA%\Temp\claude\test_suites_task.log"
