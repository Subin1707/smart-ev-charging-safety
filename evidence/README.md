# Đọc bằng chứng

`summary.json` là kết quả pipeline đầy đủ gần nhất. `summary_<stage>.json`
là lần chạy riêng một bước, không tự thay đổi kết quả toàn pipeline.

| Thư mục | Nội dung |
|---|---|
| 00_build | Compiler command, exit code, output |
| 01_model | Đồ thị PNG, danh sách trạng thái, transition và kiểm tra Kripke |
| 02_static | Pattern/cppcheck trước–sau; ASan/UBSan trước–sau; memory check mã C thực |
| 03_formal | SMT, CBMC và counterexample cho sáu bản vulnerable |
| 04_tests | Kết quả từng bộ kiểm tra C |
| 05_fuzzing | So sánh black-box/white-box và input Z3 |
| 06_e2e | API tests, snapshot EV03, ảnh browser, truy vấn PostgreSQL |

PASS trên log vulnerable nghĩa là **đã phát hiện đúng lỗi mong đợi**, không
phải bản vulnerable an toàn. CBMC cần exit 10 và VERIFICATION FAILED;
sanitizer cần đúng dấu hiệu lỗi. Lỗi compiler, thiếu DLL hoặc Docker lỗi không
được tính thành counterexample.

Ảnh dashboard lấy từ trình duyệt kết nối C/API thật. PostgreSQL chỉ PASS khi
truy vấn tìm thấy sự kiện mới trong lần chạy golden tương ứng. Các bằng chứng
chỉ áp dụng cho phạm vi mô hình, test và miền input đã ghi trong tài liệu.
