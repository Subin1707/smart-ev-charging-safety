@echo off
setlocal enabledelayedexpansion

if not exist bin\tests mkdir bin\tests

set INCS=-I src/core -I src/vehicle -I src/station -I src/charging -I src/auth -I src/safety -I src/simulation -I src/communication -I src/monitoring -I src/logging -I src/database -I src/utils
set CORE_SRCS=src/core/*.c src/vehicle/*.c src/station/*.c src/auth/*.c src/charging/*.c src/safety/*.c src/logging/*.c src/monitoring/*.c src/simulation/*.c src/database/*.c

echo ============================================================
echo           SMART EV CHARGING SYSTEM - TEST RUNNER            
echo ============================================================
echo.

set FAILED_COUNT=0
set PASSED_COUNT=0

:: UNIT TESTS
set UNIT_TESTS=test_pin test_xe_dien test_cong_sac test_tram_sac test_an_toan test_quan_ly_cong_suat test_database
for %%t in (%UNIT_TESTS%) do (
    gcc -Wall -Wextra -std=c99 %INCS% %CORE_SRCS% tests/unit/%%t.c -o bin/tests/%%t.exe
    if !ERRORLEVEL! EQU 0 (
        bin\tests\%%t.exe
        if !ERRORLEVEL! EQU 0 (
            set /a PASSED_COUNT+=1
        ) else (
            set /a FAILED_COUNT+=1
        )
    ) else (
        echo [BUILD FAIL] tests/unit/%%t.c
        set /a FAILED_COUNT+=1
    )
)

:: INTEGRATION TESTS
set INT_TESTS=test_ket_noi_xac_thuc_sac test_nhieu_xe test_phan_phoi_cong_suat test_dung_khan_cap test_luu_phien_sac_database
for %%t in (%INT_TESTS%) do (
    gcc -Wall -Wextra -std=c99 %INCS% %CORE_SRCS% tests/integration/%%t.c -o bin/tests/%%t.exe
    if !ERRORLEVEL! EQU 0 (
        bin\tests\%%t.exe
        if !ERRORLEVEL! EQU 0 (
            set /a PASSED_COUNT+=1
        ) else (
            set /a FAILED_COUNT+=1
        )
    ) else (
        echo [BUILD FAIL] tests/integration/%%t.c
        set /a FAILED_COUNT+=1
    )
)

:: E2E TESTS
set E2E_TESTS=test_luong_binh_thuong test_luong_qua_nhiet test_luong_loi_xac_thuc test_luong_pin_day test_kich_ban_ngau_nhien
for %%t in (%E2E_TESTS%) do (
    gcc -Wall -Wextra -std=c99 %INCS% %CORE_SRCS% tests/e2e/%%t.c -o bin/tests/%%t.exe
    if !ERRORLEVEL! EQU 0 (
        bin\tests\%%t.exe
        if !ERRORLEVEL! EQU 0 (
            set /a PASSED_COUNT+=1
        ) else (
            set /a FAILED_COUNT+=1
        )
    ) else (
        echo [BUILD FAIL] tests/e2e/%%t.c
        set /a FAILED_COUNT+=1
    )
)

echo ============================================================
echo                    ALL TEST SUITES SUMMARY                  
echo ============================================================
echo Passed Suites : %PASSED_COUNT%
echo Failed Suites : %FAILED_COUNT%
if %FAILED_COUNT% EQU 0 echo OVERALL STATUS: ALL 17 TEST SUITES PASSED (100 PERCENT)
if not %FAILED_COUNT% EQU 0 echo OVERALL STATUS: SOME TESTS FAILED
echo ============================================================

exit /b %FAILED_COUNT%
