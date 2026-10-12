@echo off
echo ############################################################
echo #       SMART EV CHARGING SYSTEM - ALL SECURITY CHECKS     #
echo ############################################################
echo.
call static_analysis\scripts\run_pattern_scanner.bat
echo.
call static_analysis\scripts\run_cppcheck.bat
echo.
call static_analysis\scripts\run_asan.bat
echo.
call static_analysis\scripts\run_ubsan.bat
echo.
echo ############################################################
echo #             SECURITY VERIFICATION COMPLETED              #
echo ############################################################
