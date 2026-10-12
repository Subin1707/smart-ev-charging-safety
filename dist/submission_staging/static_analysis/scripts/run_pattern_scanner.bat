@echo off
if not exist reports\analysis mkdir reports\analysis
echo ============================================================
echo          RUNNING SECURITY PATTERN SCANNER (BEFORE vs AFTER) 
echo ============================================================
echo.
echo [1] SCANNING VULNERABLE DIRECTORY:
python static_analysis/scripts/pattern_scanner.py static_analysis/vulnerable > reports\analysis\pattern_vulnerable.txt 2>&1
type reports\analysis\pattern_vulnerable.txt
echo.
echo [2] SCANNING FIXED DIRECTORY:
python static_analysis/scripts/pattern_scanner.py static_analysis/fixed > reports\analysis\pattern_fixed.txt 2>&1
type reports\analysis\pattern_fixed.txt
