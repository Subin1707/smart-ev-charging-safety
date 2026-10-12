@echo off
if not exist reports\analysis mkdir reports\analysis
echo ============================================================
echo   RUNNING UNDEFINED BEHAVIOR SANITIZER (UBSan) VIA DOCKER   
echo ============================================================
echo.
echo [1] RUNNING UBSan ON VULNERABLE: loi_tinh_nang_luong.c (EXPECTED SIGNED INTEGER OVERFLOW)
docker run --rm -v "%CD%:/workspace" -w /workspace gcc:latest bash -c "gcc -fsanitize=undefined -g static_analysis/vulnerable/loi_tinh_nang_luong.c -o /tmp/loi_int && /tmp/loi_int" > reports\analysis\ubsan_vulnerable.txt 2>&1
type reports\analysis\ubsan_vulnerable.txt

echo.
echo [2] RUNNING UBSan ON FIXED: sua_tinh_nang_luong.c (EXPECTED PASS)
docker run --rm -v "%CD%:/workspace" -w /workspace gcc:latest bash -c "gcc -fsanitize=undefined -g static_analysis/fixed/sua_tinh_nang_luong.c -o /tmp/sua_int && /tmp/sua_int" > reports\analysis\ubsan_fixed.txt 2>&1
type reports\analysis\ubsan_fixed.txt
