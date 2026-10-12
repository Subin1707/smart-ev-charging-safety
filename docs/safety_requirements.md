# Phạm vi và yêu cầu an toàn

Đề tài: **Xây dựng và kiểm chứng an toàn End-to-End cho hệ thống trạm sạc xe điện thông minh**.
Phạm vi là mô phỏng điều khiển bằng C, 5 cổng, công suất trạm 100 kW,
giám sát, API, dashboard và lưu sự kiện PostgreSQL. Không phải bộ điều khiển
được chứng nhận cho phần cứng sạc thực tế.

| ID | Yêu cầu và điều kiện chấp nhận |
|---|---|
| SR01 | Xác thực chỉ thành công sau khi xe kết nối. |
| SR02 | CHARGING yêu cầu xác thực thành công. Ngắt kết nối xóa xác thực. |
| SR03 | Nhiệt độ **>= 60°C**: từ chối START; nếu đang sạc, monitor cắt công suất trong lần xử lý hiện tại và chuyển FAULT. |
| SR04 | SOC >= 100%: không tiếp tục cấp điện. |
| SR05 | Emergency của trạm/cổng: công suất bằng 0 sau xử lý stop. |
| SR06 | Xe FAULT không được START trực tiếp; phải phục hồi và kiểm tra lại. |
| SR07 | Mỗi cổng chỉ có tối đa một xe; xe khác không được ngắt cổng của chủ sở hữu. |
| SR08 | Một ID xe không được chiếm đồng thời hai cổng trong trạm. CONNECT lặp không reset phiên đang sạc. |
| SR09 | SOC hữu hạn, trong [0,100]; cập nhật pin phải chặn vượt miền. |
| SR10 | Tổng công suất sau phân phối <= công suất trạm, mỗi cổng <= 22 kW. |
| SR11 | Khi thiếu công suất, bộ phân phối xét xe có SOC thấp trước; không hứa không starvation nếu yêu cầu mới đến vô hạn. |

## Gateway Authentication

| Ký hiệu | Tham số | Giá trị 0 | Giá trị 1 |
|---|---|---|---|
| `C` | Connected | Chưa kết nối | Đã kết nối |
| `T` | Token Valid | Token sai | Token đúng |
| `A` | Authenticated | Chưa xác thực | Đã xác thực |
| `R` | Start Request | Không yêu cầu sạc | Có yêu cầu sạc |
| `S` | Safety OK | Không an toàn | An toàn |
| `E` | Emergency | Bình thường | Khẩn cấp |

Mô hình Gateway Authentication dùng 6 biến Boolean, nên không gian tổ hợp ban đầu là:

`2^6 = 64`

Đây là 64 tổ hợp lý thuyết ứng viên, không phải 64 trạng thái thực tế của hệ thống.
Tập trạng thái hợp lệ sẽ được rút gọn bằng các ràng buộc trong
`formal/gateway_auth/gateway_auth_constraints.md`.

Việc đếm trạng thái hợp lệ được thực hiện bằng
`formal/gateway_auth/gateway_state_space.py`: sinh 64 candidate states từ
`C T A R S E`, áp dụng trước GA-C01 (`A -> C`) và GA-C02 (`A -> T`), rồi tách
valid/invalid states. Với hai ràng buộc này, 64 candidate states được rút gọn
còn 40 valid states và loại 24 invalid states. `CHARGING` không được đưa vào như
biến độc lập vì đây là kết quả chuyển trạng thái, không phải đầu vào Gateway Auth.

Liveness mong muốn: `G(valid_request -> F charging)` **với giả thiết** yêu cầu
được duy trì, token hợp lệ, cảm biến an toàn, cổng và công suất được cấp,
không có emergency và scheduler công bằng. Đồ thị không ràng buộc có vòng
hủy yêu cầu nên không thỏa mệnh đề này vô điều kiện. Mô hình hiện tại kiểm tra
đường tiến triển `WAITING -> CONNECTED -> AUTH_OK -> CHARGING` (EF).

Quy ước SR ở đây là chuẩn báo cáo mới. Tên hàm cũ `kiem_tra_sr06_soc_hop_le`,
`kiem_tra_sr08_ma_loi`, `kiem_tra_sr09_ngat_ket_noi` là tên tương thích lịch sử,
lần lượt liên quan SR09, SR06, SR01/SR02; không suy diễn coverage từ tên hàm.

PASS chỉ áp dụng cho phạm vi, miền dữ liệu và số bước ghi trong bằng chứng.
Static scanner không chứng minh logic nghiệp vụ; fuzzing hữu hạn không chứng minh mọi input.

## Function Parameter Coverage

Bao phủ tham số theo chức năng được tổng hợp trong:

`formal/system_functions/system_function_spec.md`

Tài liệu này bổ sung chuỗi:

`chức năng -> tham số -> tổ hợp trạng thái -> ràng buộc -> đặc tả yêu cầu -> code kiểm chứng tĩnh/động`.

Bốn file đặc tả đầu vào cho generator:

`specification/auth.json`, `specification/battery.json`,
`specification/port.json`, `specification/charging.json`.

State-space generator:

`generator/state_generator.py`

Static/dynamic code generators:

`generator/static_generator.py`, `generator/dynamic_generator.py`

Live terminal monitor while the simulator is running:

`python generator/live_monitor.py`
