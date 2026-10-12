@echo off
if not exist bin mkdir bin
gcc -Wall -Wextra -std=c17 -I src/core -I src/vehicle -I src/station -I src/charging -I src/auth -I src/safety -I src/simulation -I src/communication -I src/monitoring -I src/logging -I src/database -I src/utils src/core/*.c src/vehicle/*.c src/station/*.c src/auth/*.c src/charging/*.c src/safety/*.c src/communication/*.c src/monitoring/*.c src/logging/*.c src/simulation/*.c src/database/*.c src/utils/*.c src/main.c -o bin/smart_ev.exe
if %ERRORLEVEL% EQU 0 (
    echo [BUILD SUCCESS] Binary generated at bin\smart_ev.exe
) else (
    echo [BUILD FAILED]
)
