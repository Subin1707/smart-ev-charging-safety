@echo off
if not exist reports\analysis mkdir reports\analysis
echo ============================================================
echo      RUNNING ADDRESS SANITIZER (ASan) VIA DOCKER GCC        
echo ============================================================
echo.
echo [1] RUNNING ASan ON VULNERABLE: loi_id_xe.c (EXPECTED STACK-BUFFER-OVERFLOW)
docker run --rm -v "%CD%:/workspace" -w /workspace gcc:latest bash -c "gcc -fsanitize=address -g static_analysis/vulnerable/loi_id_xe.c -o /tmp/loi_id_xe && /tmp/loi_id_xe" > reports\analysis\asan_vulnerable_id.txt 2>&1
type reports\analysis\asan_vulnerable_id.txt

echo.
echo [2] RUNNING ASan ON VULNERABLE: loi_phan_tich_thong_diep.c (EXPECTED STACK-BUFFER-OVERFLOW)
docker run --rm -v "%CD%:/workspace" -w /workspace gcc:latest bash -c "gcc -fsanitize=address -g static_analysis/vulnerable/loi_phan_tich_thong_diep.c -o /tmp/loi_parser && /tmp/loi_parser" > reports\analysis\asan_vulnerable_parser.txt 2>&1
type reports\analysis\asan_vulnerable_parser.txt

echo.
echo [3] RUNNING ASan ON FIXED SAMPLES (EXPECTED PASS)
docker run --rm -v "%CD%:/workspace" -w /workspace gcc:latest bash -c "gcc -fsanitize=address -g static_analysis/fixed/sua_id_xe.c -o /tmp/sua_id_xe && /tmp/sua_id_xe && gcc -fsanitize=address -g static_analysis/fixed/sua_phan_tich_thong_diep.c -o /tmp/sua_parser && /tmp/sua_parser" > reports\analysis\asan_fixed.txt 2>&1
type reports\analysis\asan_fixed.txt
