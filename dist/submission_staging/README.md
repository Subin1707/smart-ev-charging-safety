# Smart EV Charging Safety System

He thong quan ly, dieu khien va kiem chung an toan cho tram sac xe dien thong minh.

## Trang thai GĐ10

Ket qua tich hop cuoi cung nam trong `reports/verification/final_verification_report.md`.
GĐ10 khong sua logic production; no tong hop lai evidence da co va giu nguyen cac
limitation thay vi ep thanh PASS.

Tom tat ket qua chinh:

| Hang muc | Ket qua |
|---|---:|
| Requirements | 11 |
| Requirement traceability | 11/11 |
| CTL properties | 16/16 |
| Negative controls | 6/6 DETECTED |
| SMT/Z3 requirements | 2/2 |
| Production harness | 11/11 |
| Dynamic requirements | 11/11 |
| Boundary cases | 14 |
| Boolean combinations | 128 |
| Docker ASan/UBSan sanitizer cases | 142 |
| Final requirement status | 11/11 PASS |

## Tai lieu nen doc khi cham bai

- `reports/verification/final_verification_report.md`: bao cao kiem chung cuoi.
- `reports/verification/final_requirement_matrix.md`: ma tran 11 requirement kem evidence path.
- `reports/traceability/spec_traceability.md`: mapping specification -> production code -> verification.
- `reports/verification/final_evidence_manifest.json`: manifest evidence dau vao cua GĐ10.
- `reports/verification/integrated_verification.md`: traceability table chi tiet theo requirement.

## Cach chay kiem chung

Tren Windows:

```powershell
.\verify-all.bat
```

Hoac:

```powershell
python scripts\verify_all.py
```

Neu co Make:

```powershell
make verify-all
```

Pipeline lich su cua repo co cac module Kripke/formal, static analysis, sanitizer,
SMT/Z3, unit/integration, fuzzing/API/dashboard. Ket qua GĐ10 cuoi cung duoc danh
gia theo evidence trong `reports/verification/final_evidence_manifest.json`, gom
16 CTL properties, 2 SMT/Z3 requirements, production harness 11/11, 14 boundary
cases, 128 boolean combinations va Docker sanitizer 142 cases.

PostgreSQL: chay `docker compose up -d database` neu can cac test database/API.
Native C chi ket noi Docker PostgreSQL khi `SMART_EV_POSTGRES=1`.

## Dong goi ban nop sach

De tao ZIP nop bai khong kem `.env`, `node_modules`, cache pytest, `__pycache__`,
binary build co the tai tao, log tam va cac artifact runtime:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\package_submission.ps1
```

ZIP se nam o `dist\smart-ev-charging-safety-submission.zip`.
Neu giang vien yeu cau nop kem `teacher_app\SpecVerificationLab.exe`, nop rieng
file tool do hoac sua script dong goi co chu y vi file nay hon 100 MB.
