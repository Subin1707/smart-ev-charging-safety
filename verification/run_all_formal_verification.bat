@echo off
echo ============================================================
echo   SMART EV CHARGING SYSTEM - FORMAL VERIFICATION (Z3/BMC)   
echo ============================================================
echo.

echo [0] CHAY CBMC VULNERABLE/FIXED MODELS:
call verification\run_bmc_evidence.bat
echo.

echo [1] CHAY KIEM CHUNG BMC - XAC THUC TRUOC SAC:
python verification/bmc/kiem_chung_xac_thuc_truoc_sac.py
echo.

echo [2] CHAY KIEM CHUNG BMC - DUNG KHI QUA NHIET:
python verification/bmc/kiem_chung_dung_khi_qua_nhiet.py
echo.

echo [3] CHAY KIEM CHUNG BMC - DUNG KHAN CAP:
python verification/bmc/kiem_chung_dung_khan_cap.py
echo.

echo [4] CHAY KIEM CHUNG BMC - DOC QUYEN CONG SAC:
python verification/bmc/kiem_chung_doc_quyen_cong_sac.py
echo.

echo [5] CHAY KIEM CHUNG BMC - GIOI HAN CONG SUAT:
python verification/bmc/kiem_chung_gioi_han_cong_suat.py
echo.

echo [6] CHAY SMT SOLVER - GIOI HAN SOC:
python verification/smt/kiem_chung_gioi_han_soc.py
echo.

echo [7] CHAY SMT SOLVER - PHAN PHOI CONG SUAT TRAM:
python verification/smt/kiem_chung_phan_phoi_cong_suat.py
echo.

echo [8] CHAY SMT SOLVER - NANG LUONG DONG KHONG AM:
python verification/smt/kiem_chung_tinh_nang_luong.py
echo.

echo [9] CHAY SMT SOLVER - NGUONG AN TOAN NHIET DO:
python verification/smt/kiem_chung_nhiet_do.py
echo.

echo [10] CHAY SMT/Z3 PIPELINE VA LUU EVIDENCE:
call verification\run_smt.bat
echo.

echo ============================================================
echo         FORMAL VERIFICATION DEMONSTRATION COMPLETED        
echo ============================================================
