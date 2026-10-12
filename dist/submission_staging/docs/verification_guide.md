# Chạy và đọc bằng chứng

Windows: `verify-all.bat` hoặc `python scripts/verify_all.py`.
Máy có Make: `make verify-all`. Chạy riêng một bước:
`python scripts/verify_all.py --stage sanitizer-test`.

Cần GCC, Clang (ASan/UBSan), cppcheck, CBMC, Python dependencies trong
requirements.txt, Node và dependencies web. Cài browser bằng `python -m playwright install chromium`.
Runner tìm CBMC local trong tools
hoặc PATH. Trên Windows runner thêm thư mục DLL sanitizer của Clang vào PATH
riêng cho tiến trình thử nghiệm.

Pipeline: build -> Kripke -> static -> sanitizer -> SMT -> BMC -> C tests ->
fuzz comparison -> API E2E -> dashboard build -> browser thật -> PostgreSQL. Mỗi lệnh lưu command, exit code,
thời gian và stdout/stderr. Tổng hợp chỉ PASS khi mọi bước thực chạy đạt;
UNAVAILABLE/FAIL trả exit code khác 0. Không lấy báo cáo cũ để bù bước thiếu.
Không dùng số lượng test mẫu trong hướng dẫn làm kết quả thật.

## Golden scenario quá nhiệt

Chuỗi C/API hiện có: kết nối -> xác thực -> CHARGING -> tiêm OVERHEAT ->
FAULT, power=0 -> sự kiện OVERHEAT_TRIP -> snapshot API cho dashboard.
`tests/e2e/test_golden_overheat.py` lưu snapshot trước/sau của EV03 vào
`evidence/06_e2e/`; `test_luong_qua_nhiet.c` kiểm tra trực tiếp monitor C.

`browser-test` khởi chạy C, bridge và Vite riêng, kiểm tra EV03 trong inspector,
sự kiện OVERHEAT_TRIP và dòng Charging stopped, rồi lưu `golden_dashboard.png`.
Browser test dùng `SMART_EV_SCENARIO=GOLDEN_OVERHEAT`: EV03 ở P03, SOC=12,
nhiệt độ 35°C, sau đó tiêm 61°C. Không dùng snapshot giả để tạo ảnh.
File SQL dump không phải bằng chứng PostgreSQL đã INSERT thành công.

Để kiểm chứng PostgreSQL, chạy `docker compose up -d database` trước pipeline.
Bước `postgres-test` truy vấn sự kiện EV03 mới hơn thời điểm bắt đầu browser test.
Truy vấn thủ công tương ứng:
`SELECT vehicle_code,event_type,severity,description FROM su_kien_an_toan
WHERE vehicle_code='EV03' ORDER BY id DESC;` và lưu kết quả cùng ảnh dashboard.
Nếu Docker Engine không hoạt động hoặc không truy cập được, PostgreSQL trả
UNAVAILABLE và toàn pipeline không PASS; các bước độc lập vẫn chạy và lưu bằng chứng.
