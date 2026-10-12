@echo off
python scripts\verify_all.py %*
exit /b %ERRORLEVEL%
