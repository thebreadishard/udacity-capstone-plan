@echo off
rem tools\resume_task.cmd (13 Oct 2026) - what the scheduled task CapstoneResumeJobs runs (hidden, through conhost --headless):
rem tools/resume_laptop_jobs.sh in Git Bash; its own log is probes\watch_state\resume.log, this wrapper's stderr goes to resume_task.err
"C:\Program Files\Git\usr\bin\bash.exe" -l "C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\tools\resume_laptop_jobs.sh" 2>> "C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\watch_state\resume_task.err"
