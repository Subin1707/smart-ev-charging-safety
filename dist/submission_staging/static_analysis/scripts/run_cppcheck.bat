@echo off
if not exist reports\analysis mkdir reports\analysis
echo ============================================================
echo         RUNNING CPPCHECK STATIC ANALYSIS (BEFORE vs AFTER)  
echo ============================================================
echo.
echo [1] CPPCHECK ON VULNERABLE CODE:
cppcheck --enable=all --inconclusive --std=c17 --quiet static_analysis/vulnerable > reports\analysis\cppcheck_vulnerable.txt 2>&1
type reports\analysis\cppcheck_vulnerable.txt
echo.
echo [2] CPPCHECK ON FIXED CODE:
cppcheck --enable=all --inconclusive --std=c17 --quiet static_analysis/fixed > reports\analysis\cppcheck_fixed.txt 2>&1
type reports\analysis\cppcheck_fixed.txt
